#!/usr/bin/env python3
"""Summarize BTT range-sweep precision, including high-tempo labels."""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


def fields(line: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in line.split("\t")[1:] if "=" in item)


def fraction(numerator: int, denominator: int) -> str:
    percent = 100.0 * numerator / denominator if denominator else 0.0
    return f"{numerator}/{denominator} ({percent:.1f}%)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--high-tempo-floor", type=float, default=150.0)
    parser.add_argument("--confidence-gates", default="0.00,0.35,0.45,0.55,0.60,0.70,0.80")
    args = parser.parse_args()
    gates = [float(item) for item in args.confidence_gates.split(",") if item]
    rows_by_range: dict[float, list[dict[str, str]]] = defaultdict(list)
    for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("BTT range sweep\t"):
            row = fields(line)
            rows_by_range[float(row["min_tempo"])].append(row)
    if not rows_by_range:
        raise SystemExit("BTT range sweep: no rows")

    for min_tempo in sorted(rows_by_range):
        rows = rows_by_range[min_tempo]
        high = [row for row in rows if float(row["expected"]) >= args.high_tempo_floor]
        for subset_name, subset in (("all", rows), (f"high>={args.high_tempo_floor:.0f}", high)):
            raw_hits = sum(float(row["error"]) <= args.tolerance for row in subset)
            print(
                "BTT range sweep"
                f"\tmin_tempo={min_tempo:.2f}\tsubset={subset_name}"
                f"\tgate=raw\tcorrect={fraction(raw_hits, len(subset))}\ttotal={len(subset)}"
            )
            for gate in gates:
                shown = [row for row in subset if float(row["confidence"]) >= gate]
                hits = sum(float(row["error"]) <= args.tolerance for row in shown)
                print(
                    "BTT range sweep"
                    f"\tmin_tempo={min_tempo:.2f}\tsubset={subset_name}"
                    f"\tgate={gate:.2f}\tcorrect={fraction(hits, len(shown))}\ttotal={len(subset)}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
