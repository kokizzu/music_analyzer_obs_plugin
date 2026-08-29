#!/usr/bin/env python3
"""Locate chord-tracking tests and internal test seams."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    source = ROOT / "tests" / "analyzer_internal.cpp"
    lines = source.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "ChordTrackingState tracking" not in line:
            continue
        print(f"source={source.relative_to(ROOT)}")
        for line_number in range(max(0, index - 8), min(len(lines), index + 96)):
            print(f"{line_number + 1:6} {lines[line_number]}")
        break
    makefile = ROOT / "Makefile"
    print("makefile-targets=")
    for number, line in enumerate(makefile.read_text(encoding="utf-8").splitlines(), start=1):
        if "analyzer_internal" in line:
            print(f"{number:6} {line}")
    return 0


def legacy_main() -> int:
    for source in sorted((ROOT / "tests").glob("*")):
        if not source.is_file() or source.suffix not in {".cpp", ".py", ".sh"}:
            continue
        try:
            lines = source.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        matches = [index for index, line in enumerate(lines) if "ChordTrackingState" in line or "stabilize_chord" in line]
        if not matches:
            continue
        print(f"source={source.relative_to(ROOT)}")
        for index in matches:
            for line_number in range(max(0, index - 2), min(len(lines), index + 3)):
                print(f"{line_number + 1:6} {lines[line_number]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
