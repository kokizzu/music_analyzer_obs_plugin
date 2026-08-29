#!/usr/bin/env python3
"""Print drum-classifier source windows for evidence-led tuning."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "analyzer.cpp"
TERMS = ("upper_tom", "rule_flags", "tom_strength", "snare_strength")
CONTEXT = 12


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [
        index for index, line in enumerate(lines)
        if any(term in line.lower() for term in TERMS)
    ]
    emitted_until = -1
    for index in matches:
        start = max(0, index - CONTEXT)
        end = min(len(lines), index + CONTEXT + 1)
        if start <= emitted_until:
            continue
        emitted_until = end
        print(f"{SOURCE.relative_to(ROOT)}:{index + 1}")
        for line_index in range(start, end):
            print(f"{line_index + 1:6}: {lines[line_index]}")


if __name__ == "__main__":
    main()
