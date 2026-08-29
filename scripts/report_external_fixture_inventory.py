#!/usr/bin/env python3
"""Summarize external audio fixture collections without copying them into Git."""

from collections import Counter
from pathlib import Path


ROOT = Path("build/InstrumentSamples")
AUDIO_SUFFIXES = {".aif", ".aiff", ".flac", ".mp3", ".ogg", ".opus", ".wav"}


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"missing external fixture store: {ROOT}")
    collections: Counter[str] = Counter()
    suffixes: Counter[str] = Counter()
    total = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in AUDIO_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        collection = relative.parts[0] if relative.parts else "."
        collections[collection] += 1
        suffixes[path.suffix.lower()] += 1
        total += 1
    print(f"root={ROOT.resolve()} audio_files={total}")
    print("suffixes=" + " ".join(f"{name}:{count}" for name, count in sorted(suffixes.items())))
    for name, count in collections.most_common():
        print(f"collection={name} audio_files={count}")


if __name__ == "__main__":
    main()
