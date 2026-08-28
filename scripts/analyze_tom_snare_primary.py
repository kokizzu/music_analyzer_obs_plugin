#!/usr/bin/env python3
"""Compare tom/snare primary-arbitration measurements from the drum TSV."""

from __future__ import annotations

import csv
from pathlib import Path


INPUT = Path("build/drum_primary_miss_attribute_rows.tsv")
METRICS = (
    ("tom_snare_level", "tom_level", "snare_level"),
    ("tom_snare_band", "tom_band", "snare_band"),
    ("tom_snare_trigger", "tom_trigger", "snare_trigger"),
    ("tom_snare_shape", "tom_shape_score", "snare_shape_score"),
    ("tom_snare_body", "tom_body", "snare_body"),
)


def ratio(row: dict[str, str], numerator: str, denominator: str) -> float:
    return float(row.get(numerator, "0") or 0) / (float(row.get(denominator, "0") or 0) + 1.0e-6)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def report(label: str, rows: list[dict[str, str]]) -> None:
    print(f"{label} rows={len(rows)}")
    for name, numerator, denominator in METRICS:
        values = [ratio(row, numerator, denominator) for row in rows]
        print(
            f"  {name} min={min(values, default=0):.3f} q25={percentile(values, .25):.3f}"
            f" med={percentile(values, .5):.3f} q75={percentile(values, .75):.3f}"
            f" max={max(values, default=0):.3f}"
        )


def main() -> int:
    with INPUT.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    tom_to_snare = [row for row in rows if row.get("expected") == "tom" and row.get("got") == "snare"]
    correct_tom = [row for row in rows if row.get("expected") == "tom" and row.get("got") == "tom"]
    correct_snare = [row for row in rows if row.get("expected") == "snare" and row.get("got") == "snare"]
    report("tom_to_snare", tom_to_snare)
    report("correct_tom", correct_tom)
    report("correct_snare", correct_snare)
    for row in tom_to_snare[:5]:
        print(
            "sample=" + row.get("sample", "") +
            f" level={ratio(row, 'tom_level', 'snare_level'):.3f}" +
            f" band={ratio(row, 'tom_band', 'snare_band'):.3f}" +
            f" trigger={ratio(row, 'tom_trigger', 'snare_trigger'):.3f}" +
            f" shape={ratio(row, 'tom_shape_score', 'snare_shape_score'):.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
