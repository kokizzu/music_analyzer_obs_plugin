#!/usr/bin/env python3
"""Inventory public Candombe audio and expert beat labels."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def stem(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "", path.stem.lower())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    audio = sorted((args.root / "audio").rglob("*.flac"))
    labels = sorted((args.root / "annotations").rglob("*.csv"))
    if len(audio) < 35 or len(labels) < 35:
        raise SystemExit(f"Candombe needs at least 35 FLAC/CSV pairs, found {len(audio)} audio and {len(labels)} labels")
    count = sum(stem(path) in {stem(label) for label in labels} for path in audio)
    lines = [f"candombe root: {args.root}", f"audio files: {len(audio)}", f"annotation files: {len(labels)}", f"audio stems with direct annotation-name match: {count}"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
