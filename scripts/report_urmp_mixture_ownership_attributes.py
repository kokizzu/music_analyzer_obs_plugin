#!/usr/bin/env python3
"""Compare URMP mixture ownership evidence by actual instrument and routed row."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("debug_conf", "keyboard_score", "guitar_score", "vocal_score", "other_score",
          "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise",
          "partial2", "partial3", "partial4", "partial5")


def rows() -> dict[str, dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for shard in range(4):
        path = ROOT / "build" / f"urmp_mixture_attributes_{shard}.tsv"
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                existing = best.get(row["sample_id"])
                score = float(row.get("debug_conf") or 0.0)
                if existing is None or score > float(existing.get("debug_conf") or 0.0):
                    best[row["sample_id"]] = row
    return best


def median(group: list[dict[str, str]], field: str) -> str:
    values = [float(row[field]) for row in group if row.get(field)]
    return f"{statistics.median(values):.3f}" if values else "n/a"


def main() -> int:
    samples = list(rows().values())
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in samples:
        grouped.setdefault(row["source"].removeprefix("urmpmix-"), []).append(row)
    for instrument, group in sorted(grouped.items()):
        route = Counter(row["visual_first_row"] for row in group)
        hit = [row for row in group if row["detected_expected_row"] == "1"]
        miss = [row for row in group if row["detected_expected_row"] != "1"]
        print(f"{instrument}=count:{len(group)} hit:{len(hit)} miss:{len(miss)} routes:" +
              ",".join(f"{name}={count}" for name, count in route.most_common()))
        for label, subset in (("hit", hit), ("miss", miss)):
            print(f"  {label} " + " ".join(f"{field}={median(subset, field)}" for field in FIELDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
