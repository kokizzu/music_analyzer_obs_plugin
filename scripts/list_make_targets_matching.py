#!/usr/bin/env python3
"""List declared Makefile targets containing one or more search terms."""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    terms = tuple(term.lower() for term in sys.argv[1:])
    if not terms:
        raise SystemExit("usage: list_make_targets_matching.py TERM [TERM ...]")
    targets = []
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z0-9_.%/-]+):", line)
        if not match:
            continue
        target = match.group(1)
        lowered = target.lower()
        if any(term in lowered for term in terms):
            targets.append(target)
    for target in dict.fromkeys(targets):
        print(target)


if __name__ == "__main__":
    main()
