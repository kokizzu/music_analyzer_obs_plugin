#!/usr/bin/env python3
"""Print the final metrics and chord-miss lines from the latest GuitarSet replay."""

from __future__ import annotations

import pathlib


SUMMARY = pathlib.Path("build/guitarset_verbose.log.summary")
DETAIL = pathlib.Path("build/guitarset_verbose.log")


def main() -> int:
    if not SUMMARY.is_file():
        raise SystemExit("GuitarSet summary is missing")
    print("summary:")
    print(SUMMARY.read_text(encoding="utf-8", errors="replace").strip())
    if DETAIL.is_file():
        lines = DETAIL.read_text(encoding="utf-8", errors="replace").splitlines()
        chord_lines = [line for line in lines if "chord" in line.lower()]
        print(f"\nchord diagnostic lines: {len(chord_lines)}")
        for line in chord_lines[:80]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
