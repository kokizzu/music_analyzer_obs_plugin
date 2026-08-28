#!/usr/bin/env python3
"""Preview or remove only the interrupted IDMT fixture staging directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "build" / "idmt_bass_single_track_fixture.tmp"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()

    if not TARGET.exists():
        print(f"no stale staging directory: {TARGET}")
        return 0
    if args.mode == "plan":
        print(f"would remove stale staging directory: {TARGET}")
        return 0

    shutil.rmtree(TARGET)
    print(f"removed stale staging directory: {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
