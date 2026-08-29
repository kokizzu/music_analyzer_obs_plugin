#!/usr/bin/env python3
"""Print the retained real-instrument expansion fixture selector for review."""

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source = root / "scripts" / "prepare_real_instrument_expansion.py"
    print(source)
    print(source.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
