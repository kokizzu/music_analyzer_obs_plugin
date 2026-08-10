#!/usr/bin/env python3
"""Audit rootless diminished guitar aliases and their competing intervals."""

from __future__ import annotations

import csv
import pathlib
import re
import sys
import argparse


NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
TO_PC = {name: index for index, name in enumerate(NAMES)}
CELL = re.compile(r"([A-G](?:#)?)(?:-?\d+)?:([0-9.]+)$")


def levels(value: str) -> dict[int, float]:
    output: dict[int, float] = {}
    for entry in value.split(","):
        match = CELL.match(entry)
        if match:
            pitch = TO_PC[match.group(1)]
            output[pitch] = max(output.get(pitch, 0.0), float(match.group(2)))
    return output


def expected(value: str) -> set[str]:
    return {component for component in value.split("/") if component}


def main(paths: list[pathlib.Path], root_floor: float, minor_third_floor: float,
         flat_fifth_floor: float, flat_fifth_ceiling: float) -> int:
    for path in paths:
        positive: list[tuple[dict[str, str], int, dict[int, float], dict[int, float]]] = []
        false: list[tuple[dict[str, str], int, dict[int, float], dict[int, float]]] = []
        with path.open(newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                display = levels(row.get("guitar_cells", ""))
                analysis = levels(row.get("guitar_analysis_cells", ""))
                if not 2 <= len(display) <= 3 or not 3 <= len(analysis) <= 4:
                    continue
                for root in range(12):
                    third, flat_fifth = (root + 3) % 12, (root + 6) % 12
                    if (root in display or third not in display or flat_fifth not in display or
                            root not in analysis or third not in analysis or flat_fifth not in analysis):
                        continue
                    if (analysis[root] < root_floor or analysis[third] < minor_third_floor or
                            not flat_fifth_floor <= analysis[flat_fifth] <= flat_fifth_ceiling):
                        continue
                    item = (row, root, display, analysis)
                    (positive if f"{NAMES[root]}dim" in expected(row.get("expected_chords", ""))
                     else false).append(item)
        print(f"{path.name}: candidates={len(positive) + len(false)} expected={len(positive)} false={len(false)}")
        for tag, rows in (("expected", positive), ("false", false)):
            for row, root, display, analysis in rows[:24]:
                pc = lambda interval, data: data.get((root + interval) % 12, 0.0)
                print(f"  {tag} {row['recording_id']}@{row['center_seconds']} candidate={NAMES[root]}dim "
                      f"expected={row.get('expected_chords', '--')} got={row.get('guitar_chord', '--')} "
                      f"display={len(display)} analysis={len(analysis)} "
                      f"r={pc(0, analysis):.3f} m3={pc(3, analysis):.3f} b5={pc(6, analysis):.3f} "
                      f"M3={max(pc(4, display), pc(4, analysis)):.3f} "
                      f"5={max(pc(7, display), pc(7, analysis)):.3f}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-floor", type=float, default=0.0)
    parser.add_argument("--minor-third-floor", type=float, default=0.0)
    parser.add_argument("--flat-fifth-floor", type=float, default=0.0)
    parser.add_argument("--flat-fifth-ceiling", type=float, default=1.0)
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    args = parser.parse_args()
    raise SystemExit(main(args.paths, args.root_floor, args.minor_third_floor,
                          args.flat_fifth_floor, args.flat_fifth_ceiling))
