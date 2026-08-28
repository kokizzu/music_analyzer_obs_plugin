#!/usr/bin/env python3
"""Print the guitar extension-chord tests and recognition gates."""

from pathlib import Path


def print_matches(path: Path, marker: str, context: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    printed = set()
    for index, line in enumerate(lines):
        if marker not in line:
            continue
        print(f"## {path}:{index + 1} {marker}")
        for line_index in range(max(0, index - context), min(len(lines), index + context + 1)):
            if line_index in printed:
                continue
            printed.add(line_index)
            print(f"{line_index + 1}: {lines[line_index]}")


def main() -> int:
    print_matches(Path("tests/analyzer_cases.cpp"), "Cdim", 10)
    print_matches(Path("src/analyzer.cpp"), "allow_extensions", 14)
    print_matches(Path("src/analyzer.cpp"), "simplify_weak_extensions", 14)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
