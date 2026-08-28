#!/usr/bin/env python3
"""Summarize exact Guitar visual-note coverage from real-note attribute TSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def contains_expected_note(cells: str, expected: str) -> bool:
    return any(cell.split(":", 1)[0] == expected for cell in cells.split(",") if ":" in cell)


def summarize(path: Path, label: str) -> str:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"sample_id", "family", "expected_note", "guitar_visual_notes"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
    guitar_rows = [row for row in rows if row["family"] == "guitar"]
    if not guitar_rows:
        raise ValueError(f"{path}: no Guitar rows")
    exact_rows = [
        row for row in guitar_rows if contains_expected_note(row["guitar_visual_notes"], row["expected_note"])
    ]
    samples = {row["sample_id"] for row in guitar_rows}
    exact_samples = {row["sample_id"] for row in exact_rows}
    return (
        f"isolated_guitar_visual: source={label} buffers={len(exact_rows)}/{len(guitar_rows)} "
        f"samples={len(exact_samples)}/{len(samples)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = summarize(args.input, args.label)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"isolated_guitar_visual: wrote {args.output}")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
