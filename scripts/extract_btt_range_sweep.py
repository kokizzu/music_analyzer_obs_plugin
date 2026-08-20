#!/usr/bin/env python3
"""Publish one deterministic BTT range from a completed range-sweep log."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


PREFIX = "BTT range sweep\t"


def fields(line: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in line.split("\t")[1:] if "=" in item)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-tempo", type=float, required=True)
    args = parser.parse_args()
    rows = []
    for line in args.input.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(PREFIX):
            continue
        row = fields(line)
        if abs(float(row["min_tempo"]) - args.min_tempo) <= 0.001:
            rows.append(row)
    rows.sort(key=lambda row: int(row["id"]))
    if not rows:
        parser.error(f"no BTT range-sweep rows at min tempo {args.min_tempo:.2f}")
    ids = [int(row["id"]) for row in rows]
    if ids != list(range(1, len(ids) + 1)):
        parser.error("selected BTT range-sweep ids are not contiguous")
    rendered = "".join(
        "BTT tempo diag"
        f"\tid={row['id']}\texpected={float(row['expected']):.2f}"
        f"\traw={float(row['raw']):.2f}\tconfidence={float(row['confidence']):.3f}"
        f"\tmin_tempo={float(row['min_tempo']):.2f}\tmax_tempo={float(row['max_tempo']):.2f}"
        f"\terror={float(row['error']):.2f}\n"
        for row in rows
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(f"extract_btt_range_sweep: wrote {len(rows)} rows at min tempo {args.min_tempo:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
