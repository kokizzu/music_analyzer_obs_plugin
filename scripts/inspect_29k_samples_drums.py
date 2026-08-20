#!/usr/bin/env python3
"""Summarize the published 29kSamplesDrumsDataset ZIP before preparation."""

from __future__ import annotations

import collections
import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_29k_samples_drums.py ARCHIVE", file=sys.stderr)
        return 2
    archive = Path(sys.argv[1])
    with zipfile.ZipFile(archive) as source:
        files = [item for item in source.infolist() if not item.is_dir()]
    suffixes = collections.Counter(Path(item.filename).suffix.lower() or "[none]" for item in files)
    roots = collections.Counter(item.filename.split("/", 1)[0] for item in files)
    wav_parents = collections.Counter(
        "/".join(item.filename.split("/")[:2]) for item in files
        if Path(item.filename).suffix.lower() == ".wav"
    )
    print(f"29k_samples_drums: archive={archive}")
    print(f"regular_members={len(files)}")
    print("suffixes=" + ",".join(f"{name}:{count}" for name, count in sorted(suffixes.items())))
    print("top_levels=" + ",".join(f"{name}:{count}" for name, count in sorted(roots.items())))
    print(f"wav_members={sum(wav_parents.values())}")
    print("wav_parent_samples=" + ",".join(sorted(wav_parents)[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
