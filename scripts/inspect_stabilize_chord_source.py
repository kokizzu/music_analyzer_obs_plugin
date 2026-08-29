#!/usr/bin/env python3
"""Print the full chord stabilizer implementation from the analyzer source."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "analyzer.cpp"
SIGNATURE = "void stabilize_chord("


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if SIGNATURE in line)
    depth = 0
    began = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{")
        began = began or "{" in line
        print(f"{index + 1:6} {line}")
        depth -= line.count("}")
        if began and depth == 0:
            return 0
    raise RuntimeError("unterminated stabilize_chord")


if __name__ == "__main__":
    raise SystemExit(main())
