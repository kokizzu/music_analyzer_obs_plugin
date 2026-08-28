#!/usr/bin/env python3
"""Summarize the strict three-second Kick/Bass/Snare BPM estimate.

The normal analyzer BPM field publishes this freshly recomputed moving-window
estimate directly. This parser reads ``immediate_source`` from fixed-duration
replay logs so availability and tempo-alias evidence remain auditable apart
from the rendered display field.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROW = re.compile(
    r"\bexpected=(?P<expected>[-+]?\d+(?:\.\d+)?)\b.*?"
    r"\bimmediate_source=(?P<immediate>[-+]?\d+(?:\.\d+)?)\b"
)


def parse_input(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError("input must be LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not label or not raw_path:
        raise ValueError("input must be LABEL=PATH")
    return label, Path(raw_path)


def summarize(label: str, path: Path, tolerance: float) -> str:
    rows: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW.search(line)
        if match is not None:
            rows.append((float(match["expected"]), float(match["immediate"])))
    if not rows:
        raise ValueError(f"{path}: no tempo diagnostic rows with immediate_source")
    available = [(expected, immediate) for expected, immediate in rows if immediate > 0.0]
    accurate = sum(abs(expected - immediate) <= tolerance for expected, immediate in available)
    aliases = len(available) - accurate
    return (
        f"immediate_source_bpm: corpus={label} rows={len(rows)} "
        f"available={len(available)}/{len(rows)} accurate={accurate}/{len(rows)} "
        f"accurate_available={accurate}/{len(available)} aliases={aliases} "
        f"unavailable={len(rows) - len(available)} tolerance={tolerance:g}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.tolerance < 0.0:
        parser.error("--tolerance must be non-negative")
    try:
        rendered = [summarize(*parse_input(value), args.tolerance) for value in args.input]
    except (OSError, ValueError) as error:
        parser.error(str(error))
    text = "\n".join(rendered) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.write_text(text, encoding="utf-8")
        print(f"immediate_source_bpm: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
