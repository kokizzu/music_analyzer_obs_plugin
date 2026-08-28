#!/usr/bin/env python3
"""Attribute GAPS guitar tone misses to pre-display candidate formation or pruning."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/gaps_guitar_attributes.tsv"


def pitch_classes(value: str) -> set[str]:
    return {item for item in value.split(",") if item and item != "--"}


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row.get("instrument") == "guitar"]

    expected_total = 0
    formed_hits = 0
    displayed_hits = 0
    missing_before_analysis = 0
    dropped_after_analysis = 0
    analysis_false = 0
    display_false = 0
    rows_with_dropped_expected = 0
    rows_with_only_preanalysis_miss = 0
    examples: list[str] = []
    for row in rows:
        expected = pitch_classes(row["expected_pitch_classes"])
        analysis = pitch_classes(row["guitar_analysis_pitch_classes"])
        displayed = pitch_classes(row["guitar_pitch_classes"])
        expected_total += len(expected)
        formed_hits += len(expected & analysis)
        displayed_hits += len(expected & displayed)
        missing_before = expected - analysis
        dropped = (expected & analysis) - displayed
        missing_before_analysis += len(missing_before)
        dropped_after_analysis += len(dropped)
        analysis_false += len(analysis - expected)
        display_false += len(displayed - expected)
        rows_with_dropped_expected += bool(dropped)
        rows_with_only_preanalysis_miss += bool(missing_before and not dropped)
        if dropped and len(examples) < 12:
            examples.append(
                f"expected={','.join(sorted(expected))} analysis={','.join(sorted(analysis))} "
                f"display={','.join(sorted(displayed))} dropped={','.join(sorted(dropped))} "
                f"sample={Path(row['audio_path']).name}@{row['center_seconds']}"
            )

    print(f"rows={len(rows)} expected_tones={expected_total}")
    print(f"analysis_hits={formed_hits} ({formed_hits / max(1, expected_total):.3f})")
    print(f"displayed_hits={displayed_hits} ({displayed_hits / max(1, expected_total):.3f})")
    print(f"missing_before_analysis={missing_before_analysis}")
    print(f"dropped_after_analysis={dropped_after_analysis} rows={rows_with_dropped_expected}")
    print(f"rows_only_preanalysis_miss={rows_with_only_preanalysis_miss}")
    print(f"analysis_false_pitch_classes={analysis_false}")
    print(f"display_false_pitch_classes={display_false}")
    print("display_pruning_examples")
    for example in examples:
        print(example)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
