#!/usr/bin/env python3
"""Print the URMP chord report driver so debug output can be extended safely."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "scripts" / "report_urmp_chord_cases.py"


def main() -> int:
    print(f"source={SOURCE.relative_to(ROOT)}")
    for number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{number:6} {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
