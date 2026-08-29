#!/usr/bin/env python3
"""Print the display-mirror arbitration function for routing diagnostics."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"
SIGNATURES = ("enum class FullMixDisplayRow", "void add_full_mix_display_mirror(")


def main() -> None:
    lines = SOURCE.read_text().splitlines()
    for signature in SIGNATURES:
        start = next(index for index, line in enumerate(lines) if signature in line)
        depth = 0
        entered = False
        for index in range(start, len(lines)):
            line = lines[index]
            if "{" in line:
                entered = True
            depth += line.count("{") - line.count("}")
            print(f"{index + 1:6d}  {line}")
            if entered and depth == 0:
                break
        else:
            raise RuntimeError(f"unterminated declaration: {signature}")


if __name__ == "__main__":
    main()
