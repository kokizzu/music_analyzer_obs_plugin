#!/usr/bin/env python3
"""Summarize MusicNet's annotated instrument notes against analyzer row grids."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


NOTE_RE = re.compile(r"([A-G](?:#|b)?)(-?\d+):")
PITCH = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
         "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
         "A#": 10, "Bb": 10, "B": 11}
ROWS = ("bass", "piano", "guitar", "other")


def row_for_program(program: int) -> str:
    # MusicNet uses one-based General MIDI program numbers.
    if 1 <= program <= 8:
        return "piano"
    if 25 <= program <= 32:
        return "guitar"
    if 33 <= program <= 40:
        return "bass"
    return "other"


def notes(text: str) -> set[int]:
    result: set[int] = set()
    for name, octave in NOTE_RE.findall(text or ""):
        if name in PITCH:
            result.add((int(octave) + 1) * 12 + PITCH[name])
    return result


def active_notes(text: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for item in (text or "").split(","):
        try:
            program, midi = item.split(":", 1)
            result.append((int(program), int(midi)))
        except ValueError:
            continue
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    totals: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    with args.input.open(encoding="utf-8", newline="") as handle:
        for sample in csv.DictReader(handle, delimiter="\t"):
            raw = {
                "bass": notes(sample.get("bass_notes", "")),
                "piano": notes(sample.get("keys_notes", "")),
                "guitar": notes(sample.get("guitar_notes", "")),
                "other": notes(sample.get("other_notes", "")),
            }
            visible = {
                "bass": notes(sample.get("bass_visual_notes", "")),
                "piano": notes(sample.get("keys_visual_notes", "")),
                "guitar": notes(sample.get("guitar_visual_notes", "")),
                "other": notes(sample.get("other_visual_notes", "")),
            }
            for program, midi in active_notes(sample.get("active_notes", "")):
                row = row_for_program(program)
                for scope in ("All", row.title()):
                    for metric, lit in (("Exact note in expected row", midi in raw[row]),
                                        ("Pitch class in expected row", any(note % 12 == midi % 12 for note in raw[row])),
                                        ("Visible exact note in expected row", midi in visible[row]),
                                        ("Visible pitch class in expected row", any(note % 12 == midi % 12 for note in visible[row]))):
                        cell = totals[(scope, metric)]
                        cell[0] += int(lit)
                        cell[1] += 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        out = csv.writer(handle, delimiter="\t", lineterminator="\n")
        out.writerow(("scope", "metric", "accurate", "total"))
        for (scope, metric), (accurate, total) in sorted(totals.items()):
            out.writerow((scope, metric, accurate, total))
    print(f"musicnet_routing: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
