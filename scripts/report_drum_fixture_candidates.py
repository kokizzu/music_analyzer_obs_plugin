#!/usr/bin/env python3
"""Locate external real drum/percussion audio that can become test fixtures."""

from __future__ import annotations

import os
from collections import Counter
from pathlib import Path


DEFAULT_ROOT = Path("/media/kyz/sshflashtor/InstrumentSamples")
KEYWORDS = ("drum", "percussion", "kick", "snare", "hihat", "hi-hat", "cymbal", "tom", "rim")
AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".aif", ".aiff"}


def main() -> None:
    root = Path(os.environ.get("MUSIC_ANALYZER_FIXTURE_CACHE", DEFAULT_ROOT))
    if not root.is_dir():
        raise SystemExit(f"fixture root unavailable: {root}")
    top_level = [child for child in root.iterdir() if child.is_dir()]
    candidate_roots = [
        child for child in top_level
        if any(keyword in child.name.lower() for keyword in KEYWORDS)
    ]
    print("top-level=" + ",".join(child.name for child in top_level))
    candidates: Counter[Path] = Counter()
    for candidate_root in candidate_roots:
        for path in candidate_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
                candidates[path.parent] += 1
    print(f"root={root} drum-candidate-directories={len(candidates)} audio={sum(candidates.values())}")
    for directory, count in candidates.most_common(40):
        print(f"{count:5} {directory.relative_to(root)}")


if __name__ == "__main__":
    main()
