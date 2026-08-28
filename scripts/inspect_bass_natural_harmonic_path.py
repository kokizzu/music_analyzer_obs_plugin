#!/usr/bin/env python3
"""Print the bass candidate and tuning logic relevant to natural harmonics."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "analyzer.cpp"
NEEDLES = (
    "bass_candidate_score",
    "kChromaticTuneToleranceCents",
    "chromatic_tuning_probe",
    "Bass",
)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for needle in (*NEEDLES, "correct_isolated_bass_upper_partial_alias"):
        print(f"## {needle}")
        matches = 0
        for index, line in enumerate(lines):
            if needle not in line:
                continue
            matches += 1
            if matches == 1:
                continue
            start = max(0, index - 8)
            end = min(len(lines), index + 34)
            for line_no in range(start, end):
                print(f"{line_no + 1}: {lines[line_no]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
