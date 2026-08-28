#!/usr/bin/env python3
"""Show the E-GMD verbose window formatter before adding diagnostics."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "analyzer_egmd.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "drum_debug_details" not in line or "std::string" not in line:
            continue
        for number in range(max(0, index - 16), min(len(lines), index + 28)):
            print(f"{number + 1:5}: {lines[number]}")
        return 0
    raise SystemExit("E-GMD verbose formatter not found")


if __name__ == "__main__":
    raise SystemExit(main())
