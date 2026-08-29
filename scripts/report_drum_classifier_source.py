#!/usr/bin/env python3
"""Print drum-classifier source windows for evidence-led tuning."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT / "src" / "analyzer.cpp", ROOT / "src" / "analyzer.hpp")
TERMS = ("drumdebuguppertomsnareactivebleed",)
CONTEXT = 36


def main() -> None:
    for source in SOURCES:
        lines = source.read_text(encoding="utf-8").splitlines()
        matches = [index for index, line in enumerate(lines) if any(term in line.lower() for term in TERMS)]
        emitted_until = -1
        for index in matches:
            start = max(0, index - CONTEXT)
            end = min(len(lines), index + CONTEXT + 1)
            if start <= emitted_until:
                continue
            emitted_until = end
            print(f"{source.relative_to(ROOT)}:{index + 1}")
            for line_index in range(start, end):
                print(f"{line_index + 1:6}: {lines[line_index]}")


if __name__ == "__main__":
    main()
