#!/usr/bin/env python3
"""Create deterministic, chromatically stable MIR-1K clean-vocal fixtures."""

from __future__ import annotations

import pathlib
import struct
import wave


SOURCE_ROOT = pathlib.Path("build/mir1k_vocal_fixtures/source/MIR-1K")
OUTPUT_ROOT = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocals")
MIX_OUTPUT_ROOT = pathlib.Path("build/mir1k_vocal_fixtures/vocal_mixes")
FRAME_SECONDS = 0.020
CLIP_SECONDS = 0.500
MIN_STABLE_FRAMES = 8
MAX_DEVIATION_SEMITONES = 0.180
PER_MIDI_LIMIT = 8

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def label_values(path: pathlib.Path) -> list[float]:
    values: list[float] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            values.append(float(raw.split()[0]))
        except ValueError:
            values.append(0.0)
    return values


def stable_runs(values: list[float]) -> list[tuple[int, int, int, float]]:
    runs: list[tuple[int, int, int, float]] = []
    start = 0
    current_midi: int | None = None
    deviations: list[float] = []
    for index, value in enumerate(values + [0.0]):
        midi = int(round(value)) if value > 0.0 else None
        deviation = abs(value - midi) if midi is not None else 0.0
        valid = midi is not None and deviation <= MAX_DEVIATION_SEMITONES
        if not valid or midi != current_midi:
            if current_midi is not None and index - start >= MIN_STABLE_FRAMES:
                runs.append((current_midi, start, index, sum(deviations) / len(deviations)))
            start = index
            current_midi = midi if valid else None
            deviations = [deviation] if valid else []
        elif current_midi is not None:
            deviations.append(deviation)
    return runs


def read_channels(path: pathlib.Path, start_seconds: float, clip_seconds: float) -> tuple[int, bytes, bytes]:
    with wave.open(str(path), "rb") as audio:
        if audio.getnchannels() != 2 or audio.getsampwidth() != 2:
            raise ValueError(f"expected 16-bit stereo MIR-1K WAV: {path}")
        sample_rate = audio.getframerate()
        frame_count = int(round(clip_seconds * sample_rate))
        start_frame = max(0, min(int(round(start_seconds * sample_rate)), audio.getnframes() - frame_count))
        audio.setpos(start_frame)
        raw = audio.readframes(frame_count)
        pairs = struct.iter_unpack("<hh", raw)
        right = bytearray()
        mixed = bytearray()
        for accompaniment, vocal in pairs:
            right.extend(struct.pack("<h", vocal))
            mixed.extend(struct.pack("<h", int((int(accompaniment) + int(vocal)) / 2)))
        return sample_rate, bytes(right), bytes(mixed)


def write_mono_wav(path: pathlib.Path, sample_rate: int, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(payload)


def main() -> int:
    labels_dir = SOURCE_ROOT / "PitchLabel"
    wav_dir = SOURCE_ROOT / "Wavfile"
    if not labels_dir.is_dir() or not wav_dir.is_dir():
        raise SystemExit("MIR-1K source is missing; run make import-mir1k-vocal-archive first")

    candidates: dict[int, list[tuple[str, pathlib.Path, int, int, int, float]]] = {}
    for label_path in sorted(labels_dir.glob("*.pv")):
        audio_path = wav_dir / f"{label_path.stem}.wav"
        if not audio_path.is_file():
            continue
        values = label_values(label_path)
        for midi, start, end, deviation in stable_runs(values):
            if midi < 36 or midi > 84:
                continue
            candidates.setdefault(midi, []).append(
                (label_path.stem, audio_path, start, end, end - start, deviation))

    selected: list[tuple[int, str, pathlib.Path, int, int, int, float]] = []
    for midi in sorted(candidates):
        # One candidate per clip before reusing a singer, then favor long, in-tune runs.
        ordered = sorted(candidates[midi], key=lambda item: (-item[4], item[5], item[0], item[2]))
        seen_clip: set[str] = set()
        for candidate in ordered:
            if candidate[0] in seen_clip:
                continue
            selected.append((midi, *candidate))
            seen_clip.add(candidate[0])
            if len(seen_clip) >= PER_MIDI_LIMIT:
                break

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    MIX_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_lines = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath"]
    for midi, clip_id, audio_path, start, end, _, deviation in selected:
        # The existing real-note harness starts its first window 25 ms after the
        # clip onset, so align the labelled stable run with that window.
        start_seconds = max(0.0, start * FRAME_SECONDS - 0.025)
        output_id = f"mir1k-{clip_id}-{start:04d}-{midi}"
        relative_path = pathlib.Path("audio") / f"{output_id}.wav"
        sample_rate, payload, mixed_payload = read_channels(audio_path, start_seconds, CLIP_SECONDS)
        write_mono_wav(OUTPUT_ROOT / relative_path, sample_rate, payload)
        write_mono_wav(MIX_OUTPUT_ROOT / relative_path, sample_rate, mixed_payload)
        manifest_lines.append(
            f"{output_id}\tvocals\tacoustic\tmir1k-clean-vocal\t{midi}\t{note_name(midi)}\t{relative_path.as_posix()}")

    (OUTPUT_ROOT / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    (MIX_OUTPUT_ROOT / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    by_midi: dict[int, int] = {}
    for midi, *_ in selected:
        by_midi[midi] = by_midi.get(midi, 0) + 1
    print(f"prepared fixtures: {len(selected)}")
    print(f"MIDI coverage: {min(by_midi) if by_midi else '--'}-{max(by_midi) if by_midi else '--'}")
    print("per MIDI: " + " ".join(f"{midi}:{count}" for midi, count in sorted(by_midi.items())))
    print(f"clip seconds: {CLIP_SECONDS:.3f}; stable tolerance: {MAX_DEVIATION_SEMITONES * 100:.1f} cents")
    print(f"mixed accompaniment fixtures: {MIX_OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
