#!/usr/bin/env python3
"""Prepare explicitly octave-down-shifted real Philharmonia violin fixtures.

The input recordings are ordinary, correctly labeled acoustic violin samples.
This fixture intentionally shifts their audio down one octave so the analyzer has
coverage for non-acoustic/sample-playback violin timbres below the violin's
physical range.  It is a coverage fixture, not an acoustic-source benchmark.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import wave
from collections import defaultdict
from pathlib import Path


HEADER = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]


def midi_note(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        if reader.fieldnames != HEADER:
            raise SystemExit(f"unexpected source manifest header in {path}")
        return list(reader)


def select_rows(rows: list[dict[str, str]], per_midi: int) -> list[dict[str, str]]:
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        try:
            midi = int(row["midi"])
        except ValueError:
            continue
        if row["family"] == "other" and row["source"] == "violin" and 55 <= midi <= 59:
            grouped[midi].append(row)

    selected: list[dict[str, str]] = []
    for midi in range(55, 60):
        candidates = sorted(grouped[midi], key=lambda row: (row["qualities"], row["id"]))
        if len(candidates) < per_midi:
            raise SystemExit(
                f"only found {len(candidates)} eligible Philharmonia violin MIDI {midi} rows; "
                f"need {per_midi}"
            )
        selected.extend(candidates[:per_midi])
    return selected


def output_row(source_row: dict[str, str]) -> dict[str, str]:
    source_midi = int(source_row["midi"])
    midi = source_midi - 12
    fixture_id = f"pitchshifted_octave_down_{source_row['id']}"
    return {
        "id": fixture_id,
        "family": "other",
        "nsynth_family": "strings",
        "source": "violin-pitch-shifted-octave-down",
        "midi": str(midi),
        "note": midi_note(midi),
        "path": f"audio/{fixture_id}.wav",
        "qualities": (
            f"{source_row['qualities']},derived,pitch-shifted-octave-down,"
            f"source-midi-{source_midi}"
        ),
    }


def manifest_complete(path: Path, min_rows: int) -> bool:
    if not path.is_file():
        return False
    try:
        rows = read_manifest(path)
    except (OSError, csv.Error, SystemExit):
        return False
    return len(rows) >= min_rows and all((path.parent / row["path"]).is_file() for row in rows)


def shift_one(source: Path, destination: Path, ffmpeg: str) -> None:
    if destination.is_file():
        return
    with wave.open(str(source), "rb") as wav:
        sample_rate = wav.getframerate()
    if sample_rate <= 0:
        raise SystemExit(f"invalid sample rate in {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.stem + ".partial.wav")
    try:
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-af",
                f"asetrate={sample_rate / 2:g},aresample={sample_rate}",
                "-ac",
                "1",
                "-ar",
                str(sample_rate),
                str(temporary),
            ],
            check=True,
        )
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def write_manifest(rows: list[dict[str, str]], output: Path) -> None:
    temporary = output / "manifest.tsv.tmp"
    with temporary.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=HEADER, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output / "manifest.tsv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--per-midi", type=int, default=4)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    if args.per_midi < 1:
        raise SystemExit("--per-midi must be positive")
    ffmpeg = shutil.which(args.ffmpeg) if "/" not in args.ffmpeg else args.ffmpeg
    if not ffmpeg:
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    selected = select_rows(read_manifest(args.source_manifest), args.per_midi)
    rows = [output_row(row) for row in selected]
    if manifest_complete(output / "manifest.tsv", len(rows)):
        print(f"prepare_pitch_shifted_violin_samples: keeping existing {output / 'manifest.tsv'}")
        return

    source_root = args.source_manifest.parent
    for source_row, row in zip(selected, rows):
        shift_one(source_root / source_row["path"], output / row["path"], ffmpeg)
    write_manifest(rows, output)
    print(
        "prepare_pitch_shifted_violin_samples: wrote "
        f"{len(rows)} derived real-audio rows to {output / 'manifest.tsv'}"
    )


if __name__ == "__main__":
    main()
