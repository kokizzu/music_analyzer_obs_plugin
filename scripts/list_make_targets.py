#!/usr/bin/env python3
"""List repository Make targets, optionally filtered by a case-insensitive term."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print("usage: list_make_targets.py MAKEFILE [TERM]", file=sys.stderr)
        return 2
    makefile = Path(sys.argv[1])
    term = sys.argv[2].lower() if len(sys.argv) == 3 else ""
    targets: set[str] = set()
    for line in makefile.read_text(encoding="utf-8").splitlines():
        if not line or line[0].isspace() or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.%/-]+(?:\s+[A-Za-z0-9_.%/-]+)*):", line)
        if match is None:
            continue
        targets.update(match.group(1).split())
    for target in sorted(target for target in targets if term in target.lower()):
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
