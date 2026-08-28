#!/usr/bin/env python3
"""Print an inclusive, line-numbered source range for recurring diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    args = parser.parse_args()
    lines = args.source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, args.start)
    end = min(len(lines), args.end)
    print(f"source_range source={args.source} start={start} end={end}")
    for line_number in range(start, end + 1):
        print(f"{line_number}: {lines[line_number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
