#!/usr/bin/env python3
"""Compare exact guitar-owned expected notes rendered as guitar versus piano."""

import csv
from collections import defaultdict
from pathlib import Path


REPORT = Path(__file__).resolve().parents[1] / "build" / "full_mix_guitar_attributes_shard_0.tsv"
FEATURES = (
    "debug_conf", "keyboard_score", "guitar_score", "vocal_score", "other_score",
    "onset_strength", "decay_rate", "pitch_stability", "simultaneous_onset",
    "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error",
    "centroid", "slope", "noise", "partial1", "partial2", "partial3", "partial4",
    "partial5",
)


def expected_note_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    last_buffer = max(float(row["buffer"]) for row in rows)
    matching = [
        row
        for row in rows
        if float(row["buffer"]) == last_buffer and row["debug_midi"] == row["expected_midi"]
    ]
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
        if row is None or row["debug_owner"] != "guitar":
            continue
        visual = row["buffer_visual_strongest_row"]
        if visual in {"guitar", "piano"}:
            buckets[visual].append(row)

    for visual in ("guitar", "piano"):
        rows = buckets[visual]
        print(f"guitar-owned visual-{visual} samples={len(rows)}")
        if not rows:
            continue
        for feature in FEATURES:
            mean = sum(float(row[feature]) for row in rows) / len(rows)
            print(f"  {feature}={mean:.4f}")
        for row in rows:
            print(
                f"  row={row['sample_id']} expected={row['expected_note']} "
                f"conf={row['debug_conf']} keyboard={row['keyboard_score']} "
                f"guitar={row['guitar_score']} vocal={row['vocal_score']} "
                f"other={row['other_score']} level={row['spectral_level']} "
                f"onset={row['onset_strength']} decay={row['decay_rate']} "
                f"stability={row['pitch_stability']} simultaneous={row['simultaneous_onset']} "
                f"pitch={row['pitch_confidence']} period={row['periodicity']} "
                f"harmonicity={row['harmonicity']} fit={row['fit_error']} "
                f"centroid={row['centroid']} slope={row['slope']} noise={row['noise']} "
                f"p2={row['partial2']} p3={row['partial3']} p4={row['partial4']} "
                f"p5={row['partial5']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
