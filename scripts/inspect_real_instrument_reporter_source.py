#!/usr/bin/env python3
"""Print the maintained real-instrument attribute reporter for review."""

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    target = root / "scripts" / "report_real_instrument_expansion_bass_attributes.py"
    print(target)
    print(target.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
