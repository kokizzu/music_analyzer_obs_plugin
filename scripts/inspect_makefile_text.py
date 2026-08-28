#!/usr/bin/env python3
"""Print Makefile lines containing a requested literal term."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    term = "analyzer_instrument_samples"
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    found = False
    for number, line in enumerate(lines, start=1):
        if term not in line:
            continue
        print(f"{number}: {line}")
        found = True
    if not found:
        print(f"inspect_makefile_text: no lines containing {term!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
