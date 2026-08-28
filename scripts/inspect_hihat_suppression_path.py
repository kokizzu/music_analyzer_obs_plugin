#!/usr/bin/env python3
"""Show hihat trigger, cap, and suppression logic in the analyzer."""

import re
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "src" / "analyzer.cpp"
PATTERN = re.compile(r"hihat.*(?:suppress|cap|trigger|level)|(?:suppress|cap).*hihat", re.IGNORECASE)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed_until = 0
    for line_number, line in enumerate(lines, start=1):
        if not PATTERN.search(line) or line_number <= printed_until:
            continue
        start = max(1, line_number - 12)
        end = min(len(lines), line_number + 36)
        printed_until = end
        print(f"\n{SOURCE.relative_to(SOURCE.parent.parent)}:{line_number}")
        for current in range(start, end + 1):
            print(f"{current:6}: {lines[current - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
