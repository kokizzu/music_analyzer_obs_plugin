#!/usr/bin/env python3
"""Show the snapshot activation and final hi-hat recovery paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "analyzer.cpp"
MARKERS = (
	"snapshot.drums[i].active =",
	"final_real_mix_dense_hihat_recovery",
	"final_hihat_trigger_ratio",
	"generic_early_onset_hihat_evidence",
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    regions: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not any(marker in line for marker in MARKERS):
            continue
        regions.append((max(0, index - 10), min(len(lines), index + 16)))

    merged: list[tuple[int, int]] = []
    for start, end in sorted(regions):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    for start, end in merged:
        for number in range(start, end):
            print(f"{number + 1:6} {lines[number]}")
        print()


if __name__ == "__main__":
    main()
