#!/usr/bin/env python3
"""Print the upbeat drum fixture and kick suppression sites for review."""

from pathlib import Path


def print_function(path: Path, marker: str, following_lines: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if marker not in line:
            continue
        print(f"## {path}:{index + 1}")
        for line_index in range(index, min(index + following_lines, len(lines))):
            print(f"{line_index + 1}: {lines[line_index]}")
        return
    raise SystemExit(f"missing marker {marker} in {path}")


def main() -> int:
    print_function(Path("tests/analyzer_cases.cpp"), "check_upbeat_mix_drums_and_chords", 180)
    analyzer = Path("src/analyzer.cpp")
    lines = analyzer.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "cap_drum_level(Kick" not in line:
            continue
        print(f"## {analyzer}:{index + 1}")
        for line_index in range(max(0, index - 12), min(index + 3, len(lines))):
            print(f"{line_index + 1}: {lines[line_index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
