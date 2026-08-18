#!/usr/bin/env python3
"""Inventory GTZAN-Rhythm before connecting its labels to the BPM harness."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


AUDIO_SUFFIXES = {".au", ".flac", ".mp3", ".ogg", ".wav"}
ANNOTATION_SUFFIXES = {".beats", ".csv", ".jams", ".json", ".lab", ".txt"}


def stem_key(path: Path) -> str:
    name = path.name.lower()
    known_suffixes = AUDIO_SUFFIXES | ANNOTATION_SUFFIXES
    while True:
        suffix = Path(name).suffix
        if suffix not in known_suffixes:
            break
        name = name[: -len(suffix)]
    return name.replace("_", "").replace("-", "").replace(".", "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = args.root
    audio_root = root / "audio"
    annotations_root = root / "annotations"
    if not audio_root.is_dir() or not annotations_root.is_dir():
        raise SystemExit("GTZAN-Rhythm audio or annotations are missing")

    audio = sorted(path for path in audio_root.rglob("*") if path.suffix.lower() in AUDIO_SUFFIXES)
    annotations = sorted(
        path for path in annotations_root.rglob("*") if path.suffix.lower() in ANNOTATION_SUFFIXES
    )
    if len(audio) < 900:
        raise SystemExit(f"GTZAN-Rhythm expected at least 900 audio files, found {len(audio)}")
    if not annotations:
        raise SystemExit("GTZAN-Rhythm has no recognised beat annotation files")

    annotation_stems = {stem_key(path) for path in annotations}
    matching_audio = sum(stem_key(path) in annotation_stems for path in audio)
    audio_suffixes = Counter(path.suffix.lower() for path in audio)
    annotation_suffixes = Counter(path.suffix.lower() for path in annotations)

    lines = [
        f"gtzan rhythm root: {root}",
        f"audio files: {len(audio)}",
        f"annotation files: {len(annotations)}",
        f"audio stems with direct annotation-name match: {matching_audio}",
        "audio suffixes: " + ", ".join(f"{key}={value}" for key, value in sorted(audio_suffixes.items())),
        "annotation suffixes: "
        + ", ".join(f"{key}={value}" for key, value in sorted(annotation_suffixes.items())),
        "audio examples: " + ", ".join(str(path.relative_to(audio_root)) for path in audio[:3]),
        "annotation examples: "
        + ", ".join(str(path.relative_to(annotations_root)) for path in annotations[:3]),
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
