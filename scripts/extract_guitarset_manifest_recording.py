#!/usr/bin/env python3
"""Extract one AUDIO record and its labelled events from a GuitarSet-style manifest."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--recording-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected: list[str] = []
    collecting = False
    for line in args.input.read_text(encoding="utf-8").splitlines(keepends=True):
        fields = line.rstrip("\n").split("\t", 2)
        if fields[0] == "AUDIO":
            if collecting:
                break
            collecting = len(fields) > 1 and fields[1] == args.recording_id
        if collecting:
            selected.append(line)

    if not selected:
        raise SystemExit(f"recording id not found: {args.recording_id}")
    if selected[0].split("\t", 1)[0] != "AUDIO":
        raise SystemExit(f"recording id has no AUDIO entry: {args.recording_id}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(selected), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
