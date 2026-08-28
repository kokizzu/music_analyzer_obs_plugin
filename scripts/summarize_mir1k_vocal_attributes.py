#!/usr/bin/env python3
"""Summarize full-mix ownership evidence for the MIR-1K vocal regression set."""

from __future__ import annotations

import collections
import csv
import pathlib


PATH = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")


def number(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, ""))
    except ValueError:
        return 0.0


def main() -> int:
    if not PATH.is_file():
        raise SystemExit("attributes are missing; run make collect-mir1k-clean-vocal-attributes first")
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise SystemExit("attribute TSV has no rows")
    print("columns: " + ", ".join(rows[0].keys()))
    expected_rows = [
        row for row in rows
        if row.get("debug_midi", "") and row.get("expected_midi", "") == row.get("debug_midi", "")
    ]
    print(f"expected-pitch debug rows: {len(expected_rows)}/{len(rows)}")
    owners = collections.Counter(row.get("debug_owner", "unknown") for row in expected_rows)
    print("debug owners: " + " ".join(f"{key}={value}" for key, value in sorted(owners.items())))
    numeric_columns = (
        "vocal_score", "bass_score", "keyboard_score", "guitar_score", "other_score", "debug_conf",
        "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise",
        "partial1", "partial2", "partial3", "partial4", "partial5", "vocal_tone_profile",
        "vocal_rejected_polyphony", "raw_tuned_abs_cent_offset",
    )
    for owner in sorted(owners):
        owner_rows = [row for row in expected_rows if row.get("debug_owner", "unknown") == owner]
        print(f"\nowner={owner} rows={len(owner_rows)}")
        for key in numeric_columns:
            values = [number(row, key) for row in owner_rows if row.get(key, "")]
            if values:
                print(f"{key} mean={sum(values) / len(values):.4f} min={min(values):.4f} max={max(values):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
