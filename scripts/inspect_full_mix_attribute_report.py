#!/usr/bin/env python3
"""Print the full-mix attribute report implementation for maintenance and reuse."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "scripts" / "report_full_mix_bass_attributes.py"


def main() -> int:
    print(f"source={SOURCE.relative_to(ROOT)}")
    for number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{number:6} {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
