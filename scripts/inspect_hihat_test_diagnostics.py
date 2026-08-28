#!/usr/bin/env python3
"""Show the hihat diagnostic formatting and associated fixture setup."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tests" / "analyzer_instrument_samples.cpp"
TERMS = ("expected HIHAT active", "drum_debug_rule_flags", "getenv", "MUSIC_ANALYZER")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed_until = 0
    for line_number, line in enumerate(lines, start=1):
        if not any(term in line for term in TERMS) or line_number <= printed_until:
            continue
        start = max(1, line_number - 10)
        end = min(len(lines), line_number + 28)
        printed_until = end
        print(f"\n{SOURCE.relative_to(ROOT)}:{line_number}")
        for current in range(start, end + 1):
            print(f"{current:6}: {lines[current - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
