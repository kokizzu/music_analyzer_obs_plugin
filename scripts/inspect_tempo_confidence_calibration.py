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
    parser.add_argument("--estimate-field", default="raw")
    parser.add_argument("--confidence-field", default="confidence")
    parser.add_argument("--fallback-only-field")
    parser.add_argument("--fallback-floor", type=float, default=0.60)
    parser.add_argument("--details-min-confidence", type=float)
    parser.add_argument("--details-max-confidence", type=float)
    args = parser.parse_args()
    rows = [fields(line) for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.startswith(args.prefix)]
    if not rows:
        print("tempo confidence calibration: no rows")
        return 0
    for gate in (0.0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90):
        shown = [row for row in rows if float(row.get(args.confidence_field, 0.0)) >= gate]
        if args.fallback_only_field:
            shown = [row for row in shown if float(row.get(args.fallback_only_field, 0.0)) < args.fallback_floor]
        correct = sum(abs(float(row.get(args.estimate_field, 0.0)) - float(row["expected"])) <= args.tolerance for row in shown)
        print(f"tempo confidence calibration: gate {gate:.2f} correct {correct}/{len(shown)} total {len(rows)}")
    if args.details_min_confidence is not None or args.details_max_confidence is not None:
        lower = args.details_min_confidence if args.details_min_confidence is not None else float("-inf")
        upper = args.details_max_confidence if args.details_max_confidence is not None else float("inf")
        print("tempo confidence candidates:")
        for row in rows:
            confidence = float(row.get(args.confidence_field, 0.0))
            if confidence < lower or confidence >= upper:
                continue
            if args.fallback_only_field and float(row.get(args.fallback_only_field, 0.0)) >= args.fallback_floor:
                continue
            estimate = float(row.get(args.estimate_field, 0.0))
            expected = float(row["expected"])
            status = "hit" if abs(estimate - expected) <= args.tolerance else "wrong"
            print(
                "tempo confidence candidate:"
                f" id={row.get('id', '?')} expected={expected:.2f} estimate={estimate:.2f}"
                f" backend_confidence={confidence:.3f} phase={float(row.get('phase_raw', 0.0)):.2f}"
                f" phase_confidence={float(row.get('phase_confidence', 0.0)):.3f} status={status}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
