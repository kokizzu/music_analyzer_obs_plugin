#!/usr/bin/env python3
"""Compare Other-owned expected notes rendered as Other versus piano."""

import csv
from collections import defaultdict
from pathlib import Path


REPORT = Path(__file__).resolve().parents[1] / "build" / "full_mix_other_attributes_shard_0.tsv"
FEATURES = (
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
)


def expected_note_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    matching = [row for row in rows if row["debug_midi"] == row["expected_midi"]]
    if not matching:
        return None
    return max(matching, key=lambda row: float(row["debug_conf"]))


def main() -> int:
    with REPORT.open(encoding="utf-8", newline="") as source:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in csv.DictReader(source, delimiter="\t"):
            grouped[row["sample_id"]].append(row)

    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rows in grouped.values():
        row = expected_note_row(rows)
        if row is None:
            continue
        visual = row["buffer_visual_strongest_row"]
        if visual in {"other", "piano"}:
            buckets[visual].append(row)

    for visual in ("other", "piano"):
        rows = buckets[visual]
        print(f"visual-{visual} samples={len(rows)}")
        if not rows:
            continue
        for feature in FEATURES:
            mean = sum(float(row[feature]) for row in rows) / len(rows)
            print(f"  {feature}={mean:.4f}")
        for row in rows:
            print(
                f"  row={row['sample_id']} expected={row['expected_note']} "
                f"owner={row['debug_owner']} conf={row['debug_conf']} "
                f"other={row['other_score']} keyboard={row['keyboard_score']} "
                f"guitar={row['guitar_score']} visual={visual}"
            )
            if visual == "piano" and row["debug_owner"] == "other":
                print(
                    f"    other-owned profile: midi={row['debug_midi']} "
                    f"level={row['spectral_level']} pitch={row['pitch_confidence']} "
                    f"period={row['periodicity']} harmonicity={row['harmonicity']} "
                    f"fit={row['fit_error']} centroid={row['centroid']} "
                    f"slope={row['slope']} noise={row['noise']} "
                    f"p2={row['partial2']} p3={row['partial3']} p4={row['partial4']} "
                    f"p5={row['partial5']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
