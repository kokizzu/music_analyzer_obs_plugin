#!/usr/bin/env python3
"""Inventory usable FiloBass bass-stem/downbeat-MIDI pairs without playing audio."""

import argparse
import csv
from pathlib import Path
import re


def normalized_stem(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "", path.stem.lower())


def directories_named(root: Path, name: str) -> list[Path]:
    return sorted(path for path in root.rglob(name) if path.is_dir())


def files_in(directories: list[Path], suffixes: set[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for directory in directories:
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            key = normalized_stem(path)
            if key and key not in result:
                result[key] = path
    return result


def collect(root: Path) -> tuple[list[dict[str, str]], int, int, int]:
    audio = files_in(directories_named(root, "audio_bass_stems"), {".mp3", ".wav", ".flac"})
    midi = files_in(directories_named(root, "midi_downbeat_aligned"), {".mid", ".midi"})
    syncpoints = sum(
        1 for directory in directories_named(root, "syncpoints") for path in directory.rglob("*") if path.is_file()
    )
    rows = [
        {
            "track_id": key,
            "audio_path": str(audio[key]),
            "downbeat_midi_path": str(midi[key]),
        }
        for key in sorted(audio.keys() & midi.keys())
    ]
    return rows, len(audio), len(midi), syncpoints


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-pairs", type=int, default=1)
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        raise SystemExit(f"inspect_filobass_dataset: missing extracted root: {args.root}")
    rows, audio_count, midi_count, syncpoints = collect(args.root)
    if len(rows) < max(1, args.min_pairs):
        raise SystemExit(
            f"inspect_filobass_dataset: expected at least {max(1, args.min_pairs)} paired bass stems and "
            f"downbeat MIDI files, got {len(rows)} (audio={audio_count}, midi={midi_count})"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=("track_id", "audio_path", "downbeat_midi_path"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"inspect_filobass_dataset: pairs={len(rows)} audio_stems={audio_count} "
        f"downbeat_midis={midi_count} syncpoint_files={syncpoints} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
