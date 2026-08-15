#!/usr/bin/env python3
"""Print an auditable count of label-bearing IRMAS test WAV files."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from prepare_irmas_manifest import labels_for


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    counts: Counter[str] = Counter()
    for wav in root.rglob("*.wav"):
        counts.update(labels_for(wav, root))
    print(f"IRMAS WAV files: {sum(counts.values())}")
    for label in sorted(counts):
        print(f"{label}: {counts[label]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
