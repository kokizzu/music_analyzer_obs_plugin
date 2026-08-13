#!/usr/bin/env python3
"""Create stable isolated-note probes from annotated URMP saxophone stems."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from pathlib import Path


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_from_frequency(frequency: float) -> int:
    return round(69 + 12 * math.log2(frequency / 440.0))


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def probe_id(notes_path: Path, index: int) -> str:
    """Name a probe uniquely even when an arrangement has multiple sax stems."""
    stem = notes_path.stem.removeprefix("Notes_")
    return f"urmp-sax-{notes_path.parent.name}-{stem}-{index:03d}"


def note_events(path: Path, minimum_duration: float) -> list[tuple[float, int, float]]:
    events: list[tuple[float, int, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 3:
            raise ValueError(f"invalid note row in {path}: {line!r}")
        onset, frequency, duration = (float(field) for field in fields)
        if frequency <= 0.0 or duration < minimum_duration:
            continue
        midi = midi_from_frequency(frequency)
        if 21 <= midi <= 108:
            events.append((onset, midi, duration))
    if not events:
        raise ValueError(f"no usable saxophone notes in {path}")
    return events


def spread(events: list[tuple[float, int, float]], limit: int) -> list[tuple[float, int, float]]:
    if limit <= 0 or len(events) <= limit:
        return events
    if limit == 1:
        return [events[len(events) // 2]]
    return [events[index * (len(events) - 1) // (limit - 1)] for index in range(limit)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--minimum-duration", type=float, default=0.14)
    parser.add_argument("--clip-duration", type=float, default=0.16)
    parser.add_argument("--limit-per-track", type=int, default=36)
    args = parser.parse_args()

    if args.minimum_duration <= 0.0 or args.clip_duration <= 0.0:
        raise SystemExit("minimum and clip durations must be positive")
    if not args.source_root.is_dir():
        raise SystemExit(f"missing URMP Dataset root: {args.source_root}")
    if shutil.which(args.ffmpeg) is None:
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")

    output = args.output
    audio_dir = output / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for notes_path in sorted(args.source_root.glob("*/Notes_*_sax_*.txt")):
        wav_name = notes_path.name.replace("Notes_", "AuSep_").replace(".txt", ".wav")
        wav_path = notes_path.with_name(wav_name)
        if not wav_path.is_file():
            raise SystemExit(f"missing matching sax stem: {wav_path}")
        events = spread(note_events(notes_path, args.minimum_duration), args.limit_per_track)
        for index, (onset, midi, duration) in enumerate(events):
            clip = min(args.clip_duration, duration * 0.70)
            start = onset + (duration - clip) * 0.5
            sample_id = probe_id(notes_path, index)
            relative = Path("audio") / f"{sample_id}_{note_name(midi)}.wav"
            subprocess.run(
                [
                    args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{start:.6f}", "-t", f"{clip:.6f}", "-i", str(wav_path),
                    "-ac", "1", "-ar", "44100", str(output / relative),
                ],
                check=True,
            )
            rows.append(
                {
                    "id": sample_id,
                    "family": "other",
                    "nsynth_family": "reed",
                    "source": "urmp-sax-stem",
                    "midi": str(midi),
                    "note": note_name(midi),
                    "path": str(relative),
                }
            )

    if not rows:
        raise SystemExit(f"no saxophone annotation files beneath {args.source_root}")
    with (output / "manifest.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"prepared {len(rows)} annotated URMP saxophone probes: {output / 'manifest.tsv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
