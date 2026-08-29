#!/usr/bin/env python3
"""Summarize the attribute schema and result classes from multitrack analysis."""

import csv
from collections import Counter
from pathlib import Path


INPUT = Path("build/prepared_multitrack_attributes.tsv")


def level_map(value: str) -> dict[str, float]:
    levels = {}
    for item in value.split():
        name, separator, raw_level = item.partition(":")
        if not separator:
            continue
        try:
            levels[name] = float(raw_level)
        except ValueError:
            continue
    return levels


def mean(values: list[float]) -> str:
    return f"{sum(values) / len(values):.2f}" if values else "n/a"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(f"missing Prepared Multitrack attribute export: {INPUT}")
    with INPUT.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
    print("columns=" + " ".join(reader.fieldnames or ()))
    print(f"rows={len(rows)}")
    for column in ("status", "note_status", "pitch_status", "chord_status"):
        values = [row.get(column) for row in rows if row.get(column)]
        if values:
            counts = Counter(values)
            print(f"{column}=" + " ".join(f"{key}:{value}" for key, value in sorted(counts.items())))
    for row in rows[:5]:
        print("sample=" + " ".join(f"{key}={value}" for key, value in row.items() if value)[:500])

    true_levels = []
    false_levels = []
    false_distances = Counter()
    for row in rows:
        expected = set((row.get("expected_pcs") or "").split())
        levels = level_map(row.get("detected_levels") or "")
        for pitch_class, level in levels.items():
            if pitch_class in expected:
                true_levels.append(level)
            else:
                false_levels.append(level)
                false_distances["unresolved"] += 1
    print(
        f"levels=true_count:{len(true_levels)} mean:{mean(true_levels)} "
        f"false_count:{len(false_levels)} mean:{mean(false_levels)}"
    )
    for threshold in range(10, 101, 10):
        retained_true = sum(level >= threshold for level in true_levels)
        retained_false = sum(level >= threshold for level in false_levels)
        recall = 100.0 * retained_true / len(true_levels) if true_levels else 0.0
        precision = 100.0 * retained_true / (retained_true + retained_false) if retained_true + retained_false else 0.0
        print(
            f"level_threshold={threshold} true={retained_true}/{len(true_levels)} "
            f"false={retained_false}/{len(false_levels)} recall={recall:.2f}% precision={precision:.2f}%"
        )


if __name__ == "__main__":
    main()
