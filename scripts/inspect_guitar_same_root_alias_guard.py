#!/usr/bin/env python3
"""Show the final same-root guitar alias support guard."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(
        index for index, line in enumerate(lines)
        if "bool same_root_alias_component_supported_by_clean_primary" in line
    )
    end = min(start + 180, len(lines))
    for number, line in enumerate(lines[start:end], start + 1):
        print(f"{number}: {line}")


if __name__ == "__main__":
    main()
