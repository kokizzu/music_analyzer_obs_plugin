#!/usr/bin/env python3
"""Report source-aware spectral separation for broad low-guitar mirror candidates."""

import csv
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("guitar_score", "other_score", "noise", "centroid", "slope", "partial2", "partial3", "partial4", "partial5")


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "0"))
    except ValueError:
        return 0.0


def shared_low_guitar_shape(row: dict[str, str]) -> bool:
    return (
        row.get("debug_owner") == "other"
        and int(row.get("debug_midi", "-1")) <= 52
        and number(row, "pitch_confidence") >= 0.50
        and number(row, "periodicity") >= 0.65
        and number(row, "fit_error") <= 0.20
        and 0.18 <= number(row, "noise") <= 0.70
        and number(row, "partial2") >= 0.25
        and number(row, "partial3") >= 0.18
        and number(row, "partial4") >= 0.050
    )


def potential_electronic_piano_body(row: dict[str, str]) -> bool:
    return (
        shared_low_guitar_shape(row)
        and number(row, "other_score") >= 0.62
        and number(row, "guitar_score") <= 0.40
        and number(row, "noise") >= 0.30
        and number(row, "partial2") >= 0.30
        and number(row, "partial3") >= 0.25
        and number(row, "partial4") >= 0.050
        and number(row, "partial5") <= 0.16
    )


def rows_for(family: str) -> list[dict[str, str]]:
    path = ROOT / "build" / f"real_note_{family}_low_guitar.tsv"
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if shared_low_guitar_shape(row):
                rows.append(row)
    return rows


def report(label: str, rows: list[dict[str, str]]) -> None:
    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_source[row.get("source", "unknown")].append(row)
    for source, group in sorted(by_source.items()):
        blocked = sum(potential_electronic_piano_body(row) for row in group)
        print(f"{label}/{source} frames={len(group)} potential_block={blocked} " + " ".join(
            f"{field}={statistics.median(number(row, field) for row in group):.3f}"
            for field in FIELDS
        ))


def main() -> int:
    report("piano", rows_for("piano"))
    report("guitar", rows_for("guitar"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
