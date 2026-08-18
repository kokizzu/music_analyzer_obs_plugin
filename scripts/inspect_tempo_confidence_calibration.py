#!/usr/bin/env python3
"""Audit whether lowering the BPM display-confidence gate would stay accurate."""

from __future__ import annotations

import argparse
import pathlib


def fields(line: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in line.split("\t")[1:] if "=" in item)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=pathlib.Path)
    parser.add_argument("--prefix", default="MAESTRO tempo diag\t")
    parser.add_argument("--tolerance", type=float, default=8.0)
    args = parser.parse_args()
    rows = [fields(line) for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.startswith(args.prefix)]
    if not rows:
        print("tempo confidence calibration: no rows")
        return 0
    for gate in (0.0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90):
        shown = [row for row in rows if float(row.get("confidence", 0.0)) >= gate]
        correct = sum(abs(float(row.get("raw", 0.0)) - float(row["expected"])) <= args.tolerance for row in shown)
        print(f"tempo confidence calibration: gate {gate:.2f} correct {correct}/{len(shown)} total {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
