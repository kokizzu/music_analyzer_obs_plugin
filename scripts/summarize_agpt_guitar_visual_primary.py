#!/usr/bin/env python3
"""Summarize strict expected-note Guitar visual-primary coverage on AG-PT."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


REQUIRED = {"sample_id", "family", "expected_note", "visual_first_row", "guitar_visual_notes"}


def visual_primary_hit(row: dict[str, str]) -> bool:
    visible_notes = {
        token.split(":", 1)[0]
        for token in row["guitar_visual_notes"].split(",")
        if token and token != "--"
    }
    return (
        row["visual_first_row"] == "guitar"
        and row["expected_note"] in visible_notes
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        raise ValueError(f"{args.input}: no AG-PT visual rows")
    missing = REQUIRED - set(rows[0])
    if missing:
        raise ValueError(f"{args.input}: missing columns: {', '.join(sorted(missing))}")
    if any(row["family"] != "guitar" for row in rows):
        raise ValueError(f"{args.input}: AG-PT visual measurement contains a non-guitar row")

    row_primary_buffer_hits = sum(row["visual_first_row"] == "guitar" for row in rows)
    buffer_hits = sum(visual_primary_hit(row) for row in rows)
    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)
    row_primary_sample_hits = sum(
        any(row["visual_first_row"] == "guitar" for row in sample_rows)
        for sample_rows in by_sample.values()
    )
    sample_hits = sum(any(visual_primary_hit(row) for row in sample_rows) for sample_rows in by_sample.values())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "corpus\tmetric\taccurate\ttotal\tremaining\n"
        f"AG-PT\tGuitar visual primary row (buffer)\t{row_primary_buffer_hits}\t{len(rows)}\t{len(rows) - row_primary_buffer_hits}\n"
        f"AG-PT\tGuitar visual primary row (sample)\t{row_primary_sample_hits}\t{len(by_sample)}\t{len(by_sample) - row_primary_sample_hits}\n"
        f"AG-PT\texpected exact note on Guitar visual primary (buffer)\t{buffer_hits}\t{len(rows)}\t{len(rows) - buffer_hits}\n"
        f"AG-PT\texpected exact note on Guitar visual primary (sample)\t{sample_hits}\t{len(by_sample)}\t{len(by_sample) - sample_hits}\n",
        encoding="utf-8",
    )
    print(
        "summarize_agpt_guitar_visual_primary: "
        f"row-buffer={row_primary_buffer_hits}/{len(rows)} row-sample={row_primary_sample_hits}/{len(by_sample)} "
        f"exact-buffer={buffer_hits}/{len(rows)} exact-sample={sample_hits}/{len(by_sample)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
