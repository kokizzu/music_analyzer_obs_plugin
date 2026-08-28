#!/usr/bin/env python3
"""Inspect IDMT-SMT-Bass naming and audio layout before fixture preparation."""

from __future__ import annotations

import collections
import pathlib


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass/source")


def main() -> int:
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path.name != ".complete")
    suffixes = collections.Counter(path.suffix.lower() or "<none>" for path in files)
    wavs = [path for path in files if path.suffix.lower() == ".wav"]
    print("suffixes: " + " ".join(f"{suffix}={count}" for suffix, count in sorted(suffixes.items())))
    print(f"WAVs: {len(wavs)}")
    for path in wavs[:30]:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
