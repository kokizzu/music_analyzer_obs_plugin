#!/usr/bin/env python3
"""Summarize vocal expected-row misses by observed route and numeric attributes."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


INPUT = Path("build/real_note_vocal_attributes.tsv")
NUMERIC_COLUMNS = (
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
)


def mean(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):.3f}"


def float_value(row: dict[str, str], column: str) -> float:
    try:
        return float(row.get(column) or "-inf")
    except ValueError:
        return float("-inf")


def representative_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: dict[str, dict[str, str]] = {}
    for row in rows:
        sample_id = row.get("sample_id") or ""
        previous = selected.get(sample_id)
        if previous is None or float_value(row, "raw_expected_peak") > float_value(previous, "raw_expected_peak"):
            selected[sample_id] = row
    return list(selected.values())


def true_count(rows: list[dict[str, str]], column: str) -> int:
    return sum((row.get(column) or "").lower() in {"1", "true", "yes"} for row in rows)


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(f"missing attribute export: {INPUT}")
    with INPUT.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
    print(f"columns={len(reader.fieldnames or ())}")
    misses = [row for row in rows if row.get("status") == "ownership_miss"]
    hits = [row for row in rows if row.get("status") == "hit"]
    print(f"rows={len(rows)} hits={len(hits)} ownership_misses={len(misses)}")
    for name, group in (("hits", hits), ("ownership_misses", misses)):
        routes = Counter(row.get("first_row") or "unknown" for row in group)
        print(f"{name} routes=" + " ".join(f"{key}:{value}" for key, value in sorted(routes.items())))
        fields = []
        for column in NUMERIC_COLUMNS:
            values = []
            for row in group:
                try:
                    values.append(float(row[column]))
                except (KeyError, ValueError):
                    pass
            if values:
                fields.append(f"{column}={mean(values)}")
        print(f"{name} means=" + " ".join(fields))

    by_route: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in misses:
        by_route[row.get("first_row") or "unknown"].append(row)
    for route, group in sorted(by_route.items()):
        fields = []
        for column in NUMERIC_COLUMNS:
            values = []
            for row in group:
                try:
                    values.append(float(row[column]))
                except (KeyError, ValueError):
                    pass
            if values:
                fields.append(f"{column}={mean(values)}")
        print(f"miss-route={route} count={len(group)} " + " ".join(fields))

    sample_rows = representative_rows(rows)
    sample_hits = [row for row in sample_rows if row.get("status") == "hit"]
    sample_misses = [row for row in sample_rows if row.get("status") == "ownership_miss"]
    print(f"representative-samples={len(sample_rows)} hits={len(sample_hits)} ownership_misses={len(sample_misses)}")
    for name, group in (("sample_hits", sample_hits), ("sample_misses", sample_misses)):
        fields = []
        for column in NUMERIC_COLUMNS + ("raw_expected_ratio", "raw_octave_up_ratio", "raw_fifth_up_ratio"):
            values = [float_value(row, column) for row in group]
            values = [value for value in values if value != float("-inf")]
            if values:
                fields.append(f"{column}={mean(values)}")
        print(f"{name} means=" + " ".join(fields))
    sample_miss_routes: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sample_misses:
        sample_miss_routes[row.get("first_row") or "unknown"].append(row)
    for route, group in sorted(sample_miss_routes.items()):
        fields = []
        for column in ("pitch_confidence", "periodicity", "fit_error", "centroid", "slope", "noise",
                       "partial2", "partial3", "partial4", "partial5", "raw_expected_ratio"):
            values = [float_value(row, column) for row in group]
            values = [value for value in values if value != float("-inf")]
            if values:
                fields.append(f"{column}={mean(values)}")
        print(
            f"sample-miss-route={route} count={len(group)} "
            f"tone={true_count(group, 'vocal_tone_profile')} "
            f"polyphony_rejected={true_count(group, 'vocal_rejected_polyphony')} "
            + " ".join(fields)
        )


if __name__ == "__main__":
    main()
