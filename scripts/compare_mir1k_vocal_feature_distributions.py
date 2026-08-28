#!/usr/bin/env python3
"""Compare missed MIR-1K vocal candidates against protected instrument candidates."""

from __future__ import annotations

import csv
import pathlib
import statistics


MIR_PATH = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")
REFERENCE_PATH = pathlib.Path("build/real_note_full_mix_attributes.tsv")
FEATURES = (
    "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise",
    "partial2", "partial3", "partial4", "partial5", "raw_tuned_abs_cent_offset",
)


def load(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expected_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("debug_midi", "") == row.get("expected_midi", "")]


def values(rows: list[dict[str, str]], feature: str) -> list[float]:
    output: list[float] = []
    for row in rows:
        try:
            output.append(float(row[feature]))
        except (KeyError, ValueError):
            pass
    return output


def describe(rows: list[dict[str, str]], feature: str) -> str:
    numbers = sorted(values(rows, feature))
    if not numbers:
        return "--"
    def percentile(fraction: float) -> float:
        return numbers[min(len(numbers) - 1, int(round((len(numbers) - 1) * fraction)))]
    return f"p10={percentile(.10):.3f} p50={statistics.median(numbers):.3f} p90={percentile(.90):.3f}"


def main() -> int:
    mir = [row for row in expected_rows(load(MIR_PATH)) if row.get("debug_owner") != "vocals"]
    reference = expected_rows(load(REFERENCE_PATH))
    groups: dict[str, list[dict[str, str]]] = {"MIR missed vocal": mir}
    for family in ("bass", "guitar", "piano", "other"):
        groups[f"protected {family}"] = [row for row in reference if row.get("family") == family]
    for name, rows in groups.items():
        print(f"\n{name}: {len(rows)} expected-pitch windows")
        for feature in FEATURES:
            print(f"{feature}: {describe(rows, feature)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
