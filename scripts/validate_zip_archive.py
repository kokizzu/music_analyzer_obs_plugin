#!/usr/bin/env python3
"""Fully validate a ZIP archive, including every member's compressed data."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.archive) as archive:
        bad_member = archive.testzip()
    if bad_member:
        raise SystemExit(f"invalid ZIP member: {bad_member}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
