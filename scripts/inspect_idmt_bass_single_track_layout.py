#!/usr/bin/env python3
"""Inspect audio and annotation files in the compact IDMT bass-line corpus."""

from __future__ import annotations

import collections
import pathlib


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass_single_track/source")


def main() -> int:
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path.name != ".complete")
    suffixes = collections.Counter(path.suffix.lower() or "<none>" for path in files)
    print("suffixes: " + " ".join(f"{suffix}={count}" for suffix, count in sorted(suffixes.items())))
    for path in files[:80]:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
