#!/usr/bin/env python3
"""Summarize the most frequent real-note row-attribution confusions."""

import csv
from collections import Counter
from pathlib import Path
from statistics import median
import sys


ROW_FIELDS = ("family", "buffer_strongest_row", "buffer_visual_strongest_row", "sample_id")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("build/real_note_full_mix_attributes.tsv")
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))
    if not rows:
        raise SystemExit("no attribute rows")
    missing = [field for field in ROW_FIELDS if field not in rows[0]]
    if missing:
        raise SystemExit(f"missing TSV fields: {', '.join(missing)}")

    for row_name in ("buffer_strongest_row", "buffer_visual_strongest_row"):
        routes: Counter[tuple[str, str]] = Counter()
        samples: Counter[tuple[str, str, str]] = Counter()
        for row in rows:
            expected = row["family"]
            observed = row[row_name]
            if not expected or not observed or expected == observed:
                continue
            routes[(expected, observed)] += 1
            samples[(expected, observed, row["sample_id"])] += 1
        print(row_name)
        for (expected, observed), count in routes.most_common(12):
            leading = [
                f"{sample_id}:{sample_count}"
                for (family, route, sample_id), sample_count in samples.most_common()
                if family == expected and route == observed
            ][:4]
            print(f"  {expected}->{observed} rows={count} samples={' '.join(leading)}")

    feature_fields = ("partial2", "partial3", "partial4", "partial5", "centroid", "slope", "noise",
                      "harmonicity", "fit_error", "pitch_confidence", "periodicity")
    groups = {
        "piano->piano": [row for row in rows if row["family"] == "piano" and row["buffer_strongest_row"] == "piano"],
        "piano->guitar": [row for row in rows if row["family"] == "piano" and row["buffer_strongest_row"] == "guitar"],
        "guitar->guitar": [row for row in rows if row["family"] == "guitar" and row["buffer_strongest_row"] == "guitar"],
        "guitar->piano": [row for row in rows if row["family"] == "guitar" and row["buffer_strongest_row"] == "piano"],
    }
    print("owner-feature-medians")
    for name, group in groups.items():
        if not group:
            continue
        values = []
        for field in feature_fields:
            series = [float(row[field]) for row in group if row.get(field)]
            values.append(f"{field}={median(series):.3f}" if series else f"{field}=--")
        print(f"  {name} rows={len(group)} {' '.join(values)}")

    def electronic_keyboard_shape(row: dict[str, str]) -> bool:
        try:
            return (
                0.30 <= float(row["partial2"]) <= 0.50 and
                0.050 <= float(row["partial3"]) <= 0.120 and
                float(row["partial4"]) <= 0.060 and
                float(row["partial5"]) <= 0.030 and
                0.14 <= float(row["centroid"]) <= 0.24 and
                0.075 <= float(row["slope"]) <= 0.16 and
                float(row["noise"]) <= 0.030 and
                float(row["pitch_confidence"]) >= 0.85
            )
        except ValueError:
            return False

    print("candidate-electronic-keyboard-shape")
    for name, group in groups.items():
        matched = sum(electronic_keyboard_shape(row) for row in group)
        print(f"  {name} {matched}/{len(group)}")


if __name__ == "__main__":
    main()
