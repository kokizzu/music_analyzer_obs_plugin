#!/usr/bin/env python3
"""Print bounded context for a literal term across project source files."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".hpp", ".py"}
SKIP_PARTS = {".git", "build", ".cache", "node_modules"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("term")
    parser.add_argument("--context", type=int, default=3)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    printed = 0
    for path in sorted(root.rglob("*")):
        if printed >= args.limit or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for index, line in enumerate(lines):
            if args.term not in line:
                continue
            start = max(0, index - args.context)
            end = min(len(lines), index + args.context + 1)
            print(f"--- {path.relative_to(root)}:{start + 1}-{end} ---")
            for number in range(start, end):
                print(f"{number + 1}: {lines[number]}")
            printed += 1
            if printed >= args.limit:
                break
    print(f"matches={printed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
