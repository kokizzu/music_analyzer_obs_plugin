#!/usr/bin/env python3
"""Assert the measured full-mix vocal recall floor from the real-audio audit."""

import argparse
import re
from pathlib import Path


SUMMARY = re.compile(r"expected-row-by-family.*?\bvocals=(\d+)/(\d+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit", type=Path)
    parser.add_argument("--minimum-hits", type=int, required=True)
    arguments = parser.parse_args()
    contents = arguments.audit.read_text(encoding="utf-8")
    matches = SUMMARY.findall(contents)
    if not matches:
        raise SystemExit(f"no vocal expected-row summary in {arguments.audit}")
    hits, total = (int(value) for value in matches[-1])
    print(f"real-vocal expected-row={hits}/{total} minimum={arguments.minimum_hits}")
    if hits < arguments.minimum_hits:
        raise SystemExit(f"expected at least {arguments.minimum_hits} full-mix vocal rows, got {hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
