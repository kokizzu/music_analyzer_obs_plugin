#!/usr/bin/env python3
"""Create an annotated GTZAN-Rhythm BPM fixture without copying the audio."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import struct
from pathlib import Path


def vlq(value: int) -> bytes:
    encoded = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        encoded.append((value & 0x7F) | 0x80)
    return bytes(reversed(encoded))


def midi_with_tempo(bpm: float) -> bytes:
    microseconds = round(60_000_000 / bpm)
    track = b"\x00\xff\x51\x03" + microseconds.to_bytes(3, "big")
    track += b"\x00\x90\x3c\x40" + vlq(480 * 64) + b"\x80\x3c\x00"
    track += b"\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def stable_segment(beats: list[float], minimum_seconds: float) -> tuple[float, float, float] | None:
    for begin in range(len(beats) - 1):
        intervals: list[float] = []
        best: tuple[float, float, float] | None = None
        for end in range(begin + 1, len(beats)):
            interval = beats[end] - beats[end - 1]
            if interval <= 0.20 or interval >= 2.00:
                break
            intervals.append(interval)
            duration = beats[end] - beats[begin]
            if duration < minimum_seconds or len(intervals) < 12:
                continue
            mean = sum(intervals) / len(intervals)
            if max(abs(item - mean) for item in intervals) > mean * 0.10:
                break
            best = (beats[begin], 60.0 / mean, duration)
        if best is not None:
            return best
    return None


def read_beats(path: Path) -> list[float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for annotation in payload.get("annotations", []):
        if annotation.get("namespace") != "beat":
            continue
        beats = [float(item["time"]) for item in annotation.get("data", []) if "time" in item]
        if len(beats) >= 2:
            return beats
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-seconds", type=float, default=14.0)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    wavs = {path.name: path for path in args.audio_root.rglob("*.wav")}
    if len(wavs) < 900:
        raise SystemExit(f"expected at least 900 GTZAN WAV files, found {len(wavs)}")
    eligible_by_genre: dict[str, list[tuple[Path, float, float, float]]] = {}
    for annotation in sorted(args.annotations_root.rglob("*.jams")):
        if not annotation.name.endswith(".wav.jams"):
            continue
        wav = wavs.get(annotation.name[: -len(".jams")])
        if wav is None:
            continue
        segment = stable_segment(read_beats(annotation), args.minimum_seconds)
        if segment is None:
            continue
        offset, bpm, duration = segment
        eligible_by_genre.setdefault(wav.parent.name, []).append((wav, offset, bpm, duration))

    if args.output.exists():
        shutil.rmtree(args.output)
    (args.output / "audio").mkdir(parents=True)
    (args.output / "midi").mkdir()
    rows: list[dict[str, str]] = []
    while len(rows) < args.limit:
        selected = False
        for genre in sorted(eligible_by_genre):
            if len(rows) >= args.limit:
                break
            candidates = eligible_by_genre[genre]
            if not candidates:
                continue
            wav, offset, bpm, duration = candidates.pop(0)
            identity = f"{genre}_{wav.stem}"
            audio_name = f"audio/{identity}.wav"
            midi_name = f"midi/{identity}.mid"
            link = args.output / audio_name
            os.symlink(os.path.relpath(wav, link.parent), link)
            (args.output / midi_name).write_bytes(midi_with_tempo(bpm))
            rows.append(
                {
                    "audio_filename": audio_name,
                    "midi_filename": midi_name,
                    "tempo_audio_offset_seconds": f"{offset:.6f}",
                    "tempo_duration_seconds": f"{duration:.6f}",
                }
            )
            selected = True
        if not selected:
            break
    if not rows:
        raise SystemExit("no GTZAN-Rhythm WAV/JAMS pairs with a stable beat interval")
    with (args.output / "maestro-v3.0.0.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"prepare_gtzan_rhythm_tempo_fixture: tracks={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
