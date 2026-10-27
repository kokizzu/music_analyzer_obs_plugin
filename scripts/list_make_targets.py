#!/usr/bin/env python3
"""List Make targets whose names match a regular expression."""

from __future__ import annotations
from makefile_source import read_makefile

import argparse
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="Makefile")
    parser.add_argument("--pattern", default=".")
    parser.add_argument("legacy_file", nargs="?")
    parser.add_argument("legacy_pattern", nargs="?")
    args = parser.parse_args()

    expression = re.compile(args.legacy_pattern if args.legacy_pattern is not None else args.pattern, re.IGNORECASE)
    target_pattern = re.compile(r"^([A-Za-z0-9_.@%/+:-]+):(?:\s|$)")
    path = Path(args.legacy_file or args.file)
    for line_number, line in enumerate(read_makefile(path, encoding="utf-8", errors="replace").splitlines(), 1):
        match = target_pattern.match(line)
        if match and expression.search(match.group(1)):
            print(f"{line_number}: {match.group(1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
