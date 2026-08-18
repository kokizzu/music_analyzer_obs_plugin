#!/usr/bin/env python3
"""Compare raw bass-envelope attack grids with annotated FiloBass tempi.

This is an offline diagnostic only: it reads converted WAV samples and never
opens an audio device.  It establishes whether a simple absolute-envelope
attack stream can recover the reviewed beat grid before that stream is allowed
to influence the live tempo detector.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import struct
import wave


MIN_BPM = 50
MAX_BPM = 220


def midi_bpm(path: Path) -> float:
    data = path.read_bytes()
    marker = b"\xff\x51\x03"
    offset = data.find(marker)
    if offset < 0 or offset + len(marker) + 3 > len(data):
        raise ValueError(f"missing MIDI tempo in {path}")
    microseconds = int.from_bytes(data[offset + len(marker):offset + len(marker) + 3], "big")
    if microseconds <= 0:
        raise ValueError(f"invalid MIDI tempo in {path}")
    return 60_000_000.0 / microseconds


def pcm_sample(data: bytes, offset: int, width: int) -> float:
    if width == 1:
        return (data[offset] - 128) / 128.0
    if width == 2:
        return struct.unpack_from("<h", data, offset)[0] / 32768.0
    if width == 3:
        value = int.from_bytes(data[offset:offset + 3], "little", signed=False)
        if value & 0x800000:
            value -= 0x1000000
        return value / 8388608.0
    if width == 4:
        return struct.unpack_from("<i", data, offset)[0] / 2147483648.0
    raise ValueError(f"unsupported PCM sample width {width}")


def envelope_onsets(path: Path, start_seconds: float, seconds: float, window: int, hop: int) -> tuple[list[float], float]:
    with wave.open(str(path), "rb") as audio:
        if audio.getcomptype() != "NONE":
            raise ValueError(f"compressed WAV is unsupported: {path}")
        sample_rate = audio.getframerate()
        channels = audio.getnchannels()
        width = audio.getsampwidth()
        start = max(0, int(round(start_seconds * sample_rate)))
        frames = min(int(round(seconds * sample_rate)), max(0, audio.getnframes() - start))
        audio.setpos(start)
        raw = audio.readframes(frames)
    frame_size = channels * width
    samples: list[float] = []
    for frame in range(len(raw) // frame_size):
        base = frame * frame_size
        samples.append(sum(pcm_sample(raw, base + channel * width, width) for channel in range(channels)) / channels)
    energies: list[float] = []
    for begin in range(0, max(0, len(samples) - window + 1), hop):
        square_sum = sum(value * value for value in samples[begin:begin + window])
        energies.append(math.log(max(math.sqrt(square_sum / window), 1.0e-7)))
    if not energies:
        return [], sample_rate / hop
    onsets = [0.0]
    previous = energies[0]
    slow = energies[0]
    for energy in energies[1:]:
        # A short rising difference relative to a slow body envelope rejects
        # sustained bass notes while retaining new plucks of the same pitch.
        onsets.append(max(0.0, energy - max(previous * 0.55 + slow * 0.45, slow)))
        previous = energy
        slow = slow * 0.985 + energy * 0.015
    return onsets, sample_rate / hop


def candidate_score(onsets: list[float], frames_per_second: float, bpm: int) -> float:
    if not onsets:
        return 0.0
    period = 60.0 / bpm
    duration = len(onsets) / frames_per_second
    tolerance = min(0.070, max(0.028, period * 0.10))
    total_onset_energy = sum(onsets)
    best = 0.0
    for phase_step in range(24):
        phase = period * phase_step / 24.0
        score = 0.0
        covered_onset_energy = 0.0
        expected = 0
        beat = phase
        while beat < duration:
            center = int(round(beat * frames_per_second))
            radius = max(1, int(math.ceil(tolerance * frames_per_second)))
            local = 0.0
            for frame in range(max(0, center - radius), min(len(onsets), center + radius + 1)):
                distance = abs(frame / frames_per_second - beat)
                if distance <= tolerance:
                    local = max(local, onsets[frame] * (1.0 - distance / tolerance))
            score += local
            # The unweighted local peak estimates how much of the source's
            # actual attack energy this candidate explains.  A half-time grid
            # can align with every other event, but must lose the intervening
            # attacks instead of tying the complete beat grid.
            covered_onset_energy += local
            expected += 1
            beat += period
        if expected >= 3:
            coverage = min(1.0, covered_onset_energy / max(total_onset_energy, 1.0e-9))
            best = max(best, score / expected * (0.20 + coverage * 0.80))
    return best


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=18.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    metadata = args.root / "maestro-v3.0.0.csv"
    rows: list[dict[str, object]] = []
    with metadata.open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            audio = args.root / item["audio_filename"]
            midi = args.root / item["midi_filename"]
            expected = midi_bpm(midi)
            onsets, frame_rate = envelope_onsets(audio, float(item["tempo_audio_offset_seconds"]), args.seconds, 1024, 512)
            scores = [(candidate_score(onsets, frame_rate, bpm), bpm) for bpm in range(MIN_BPM, MAX_BPM + 1)]
            scores.sort(reverse=True)
            expected_rank = next(index + 1 for index, (_, bpm) in enumerate(scores) if abs(bpm - expected) <= 0.5)
            expected_score = next(score for score, bpm in scores if abs(bpm - expected) <= 0.5)
            doubled_top_bpm = scores[0][1] * 2
            direct_or_double_hit = abs(scores[0][1] - expected) <= 8.0 or (
                doubled_top_bpm <= MAX_BPM and abs(doubled_top_bpm - expected) <= 8.0
            )
            rows.append({
                "id": Path(item["audio_filename"]).stem.removeprefix("filobass_"),
                "expected_bpm": f"{expected:.2f}",
                "top_bpm": scores[0][1],
                "top_double_bpm": doubled_top_bpm if doubled_top_bpm <= MAX_BPM else "--",
                "top_or_double_hit": int(direct_or_double_hit),
                "expected_rank": expected_rank,
                "top_score": f"{scores[0][0]:.6f}",
                "expected_score": f"{expected_score:.6f}",
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "expected_bpm", "top_bpm", "top_double_bpm", "top_or_double_hit", "expected_rank", "top_score", "expected_score"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    top_one = sum(row["expected_rank"] == 1 for row in rows)
    top_five = sum(int(row["expected_rank"]) <= 5 for row in rows)
    direct_or_double = sum(int(row["top_or_double_hit"]) for row in rows)
    print(f"inspect_bass_tempo_onsets: rows={len(rows)} expected-rank1={top_one}/{len(rows)} expected-rank5={top_five}/{len(rows)} top-or-double={direct_or_double}/{len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
