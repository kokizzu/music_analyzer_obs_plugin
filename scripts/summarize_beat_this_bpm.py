#!/usr/bin/env python3
"""Summarize offline Beat This! BPM diagnostics without analyzer fields."""
from __future__ import annotations

import argparse
from pathlib import Path


PREFIX = "Beat This tempo diag\t"


def fields(line: str, prefix: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in line[len(prefix) :].split("\t") if "=" in item)


def fraction(numerator: int, denominator: int) -> str:
    percent = 100.0 * numerator / denominator if denominator else 0.0
    return f"{numerator}/{denominator} ({percent:.1f}%)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--high-tempo-floor", type=float, default=150.0)
    parser.add_argument("--prefix", default=PREFIX)
    args = parser.parse_args()
    rows = [fields(line, args.prefix) for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.startswith(args.prefix)]
    if not rows:
        raise SystemExit("Beat This tempo summary: no rows")
    high = [row for row in rows if float(row["expected"]) >= args.high_tempo_floor]
    for name, subset in (("all", rows), (f"high>={args.high_tempo_floor:.0f}", high)):
        hits = sum(float(row["error"]) <= args.tolerance for row in subset)
        no_beats = sum(int(row.get("intervals", "0")) == 0 for row in subset)
        half_or_double = sum(
            abs(float(row["raw"]) * 2.0 - float(row["expected"])) <= args.tolerance
            or abs(float(row["raw"]) - float(row["expected"]) * 2.0) <= args.tolerance
            for row in subset
        )
        print(
            f"Beat This tempo summary\tsubset={name}\thits={fraction(hits, len(subset))}"
            f"\tno_beats={no_beats}\thalf_or_double={half_or_double}\ttotal={len(subset)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
