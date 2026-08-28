#!/usr/bin/env python3
"""Summarize drum-lane activation in melodic real-note analysis attributes."""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


DRUM_COLUMNS = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
GROUP_COLUMNS = (
    "expected_family",
    "family",
    "source",
    "sample_id",
    "mode",
    "source_name",
    "sample",
    "lane",
    "source_mode",
    "instrument",
)
ACTIVE_LEVEL = 0.30


def number(value: str | None) -> float:
    try:
        return float(value or 0.0)
    except ValueError:
        return 0.0


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "build/real_note_full_mix_attributes.tsv")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    if not rows:
        raise SystemExit("no attribute rows")
    fields = set(rows[0])
    drum_columns = tuple(column for column in DRUM_COLUMNS if column in fields)
    if not drum_columns:
        raise SystemExit("missing drum activation columns; fields=" + ",".join(rows[0]))

    print("fields=" + ",".join(rows[0]))
    activations = [
        (row, tuple(column for column in drum_columns if number(row.get(column)) >= ACTIVE_LEVEL))
        for row in rows
    ]
    active = [(row, lanes) for row, lanes in activations if lanes]
    print(f"rows={len(rows)} active_rows={len(active)} threshold={ACTIVE_LEVEL:.2f}")
    print("lane_rows=" + " ".join(
        f"{column}={sum(column in lanes for _, lanes in active)}" for column in drum_columns))

    hihat_active = [row for row, lanes in active if "hihat" in lanes]
    hihat_inactive = [row for row, lanes in activations if "hihat" not in lanes]
    for column in ("rms", "low", "mid", "high", "onset_strength", "decay_rate", "spectral_level",
                   "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise"):
        if column not in fields:
            continue
        def median(values: list[float]) -> float:
            values.sort()
            return values[len(values) // 2] if values else 0.0
        print(f"hihat_{column}=active:{median([number(row.get(column)) for row in hihat_active]):.3f} "
              f"inactive:{median([number(row.get(column)) for row in hihat_inactive]):.3f}")

    for column in GROUP_COLUMNS:
        if column not in fields:
            continue
        grouped: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row, lanes in activations:
            value = row.get(column) or "<empty>"
            grouped[value][0] += 1
            grouped[value][1] += bool(lanes)
        ranked = sorted(grouped.items(), key=lambda item: (-item[1][1], -item[1][0], item[0]))[:15]
        print(f"by_{column}=" + " ".join(
            f"{value}:{hits}/{total}" for value, (total, hits) in ranked if hits))

    sample_column = next((column for column in ("sample_id", "sample", "source_name") if column in fields), None)
    if sample_column:
        sample_lanes: dict[str, Counter[str]] = defaultdict(Counter)
        sample_rows: Counter[str] = Counter()
        for row, lanes in active:
            sample = row.get(sample_column) or "<empty>"
            sample_rows[sample] += 1
            sample_lanes[sample].update(lanes)
        print("top_samples=")
        for sample, count in sample_rows.most_common(20):
            lanes = ",".join(f"{name}:{amount}" for name, amount in sample_lanes[sample].most_common())
            print(f"  {sample} {count} [{lanes}]")


if __name__ == "__main__":
    main()
