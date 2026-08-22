#!/usr/bin/env python3
"""Compare raw pitch-class evidence for missing and extra SATB chord tones."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FLOORS = (1, 5, 10, 18, 30)


def parse_pitch_classes(value: str) -> set[str]:
    return {token for token in value.split() if token}


def parse_chroma(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for token in value.split():
        try:
            name, level = token.split(":", 1)
            result[name] = float(level)
        except ValueError:
            continue
    return result


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * fraction))]


def summarize(label: str, path: Path) -> list[str]:
    missing_levels: list[float] = []
    extra_levels: list[float] = []
    rows = 0
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"missing_pcs", "extra_pcs", "raw_chroma"}
        absent = required - set(reader.fieldnames or ())
        if absent:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(absent))}")
        for row in reader:
            rows += 1
            chroma = parse_chroma(row["raw_chroma"])
            missing_levels.extend(chroma.get(pitch_class, 0.0) for pitch_class in parse_pitch_classes(row["missing_pcs"]))
            extra_levels.extend(chroma.get(pitch_class, 0.0) for pitch_class in parse_pitch_classes(row["extra_pcs"]))

    def counts(levels: list[float]) -> str:
        return " ".join(f">={floor}:{sum(level >= floor for level in levels)}/{len(levels)}" for floor in FLOORS)

    return [
        f"{label}: rows={rows} missing_pcs={len(missing_levels)} extra_pcs={len(extra_levels)}",
        f"  missing raw-chroma p50={quantile(missing_levels, 0.50):.1f} p75={quantile(missing_levels, 0.75):.1f} p90={quantile(missing_levels, 0.90):.1f} {counts(missing_levels)}",
        f"  extra raw-chroma p50={quantile(extra_levels, 0.50):.1f} p75={quantile(extra_levels, 0.75):.1f} p90={quantile(extra_levels, 0.90):.1f} {counts(extra_levels)}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="LABEL=PATH")
    args = parser.parse_args()
    for item in args.input:
        try:
            label, raw_path = item.split("=", 1)
        except ValueError:
            parser.error(f"expected LABEL=PATH, got {item!r}")
        for line in summarize(label, Path(raw_path)):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
