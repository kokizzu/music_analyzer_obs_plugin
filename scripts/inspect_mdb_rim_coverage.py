#!/usr/bin/env python3
"""Summarize annotated MDB Drums Rim-event detection from verbose windows."""

from __future__ import annotations

import argparse
from pathlib import Path

from evaluate_egmd_drum_recovery import active, read_events


def summarize(path: Path) -> tuple[int, int]:
    events = [event for event in read_events([path]) if "rim" in event.expected]
    return sum(active(event, "rim") for event in events), len(events)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        detected, total = summarize(args.input)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if total <= 0:
        parser.error(f"{args.input}: no annotated MDB Rim events")
    rendered = f"mdb_rim_coverage: detected={detected}/{total}\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"mdb_rim_coverage: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
