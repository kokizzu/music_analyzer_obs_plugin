#!/usr/bin/env python3
"""Print only the guitar extended-chord tests and template-selection callsites."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests/analyzer_cases.cpp"
ANALYZER = ROOT / "src/analyzer.cpp"
CMAKE = ROOT / "CMakeLists.txt"


def print_context(path: Path, marker: str, before: int, after: int, limit: int = 2) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if marker.lower() in line.lower()]
    print(f"\n--- {path.relative_to(ROOT)} marker={marker!r} matches={len(matches)} ---")
    for index in matches[:limit]:
        start = max(0, index - before)
        end = min(len(lines), index + after + 1)
        print(f"@ {index + 1}")
        for line_number in range(start, end):
            print(f"{line_number + 1:6}: {lines[line_number]}")


def print_guitar_chord_callsites() -> None:
    lines = ANALYZER.read_text(encoding="utf-8").splitlines()
    matches = [
        index for index, line in enumerate(lines)
        if "guitar" in line.lower() and "chord" in line.lower()
    ]
    print(f"\n--- src/analyzer.cpp guitar/chord callsites={len(matches)} ---")
    for index in matches[:8]:
        print(f"{index + 1:6}: {lines[index]}")


def main() -> None:
    print_context(ANALYZER, "clear_instrument_state(snapshot.guitar_chord", 12, 40, 8)
    print_context(ANALYZER, "reset_chord_tracking(guitar_chord_tracking", 12, 40, 8)


if __name__ == "__main__":
    main()
