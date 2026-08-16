#!/usr/bin/env python3
"""Audit a plain-triad-to-dominant-seventh display extension across corpora."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
PITCH = {name: index for index, name in enumerate(NAMES)}


@dataclass
class Counts:
    candidates: int = 0
    gains: int = 0
    regressions: int = 0


def parse_levels(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for token in value.split():
        name, separator, level = token.partition(":")
        if separator and name in PITCH:
            result[name] = float(level)
    if result and max(result.values()) > 2.0:
        result = {name: level / 100.0 for name, level in result.items()}
    return result


def plain_root(label: str) -> int | None:
    return PITCH.get(label.split("=", 1)[0])


def expected_dominant(value: str, root: int) -> bool:
    return f"{NAMES[root]}7" in value.split("/")


def measured_pitch_classes(row: dict[str, str]) -> set[int]:
    field = "detected_pcs" if "detected_pcs" in row else "guitar_pitch_classes"
    tokens = row.get(field, "").replace(",", " ").split()
    return {PITCH[name] for name in tokens if name in PITCH}


def raw_levels(row: dict[str, str]) -> dict[str, float]:
    field = "raw_chroma" if "raw_chroma" in row else "raw_pitch_class_levels"
    return parse_levels(row.get(field, ""))


def audit(path: Path, floor: float) -> Counts:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected_chords", "global_chord", "chord_hit"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing chord evidence columns")

    result = Counts()
    for row in rows:
        root = plain_root(row["global_chord"])
        if root is None:
            continue
        dominant_tones = {root, (root + 4) % 12, (root + 7) % 12, (root + 10) % 12}
        if measured_pitch_classes(row) != dominant_tones:
            continue
        seventh = NAMES[(root + 10) % 12]
        if raw_levels(row).get(seventh, 0.0) < floor:
            continue
        result.candidates += 1
        expected = expected_dominant(row["expected_chords"], root)
        hit = row["chord_hit"] == "1"
        result.gains += int(expected and not hit)
        result.regressions += int(not expected and hit)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--floor", type=float, default=0.25)
    args = parser.parse_args()
    if not 0.0 <= args.floor <= 1.0:
        parser.error("--floor must be within 0..1")

    supported = 0
    regressions = 0
    for path in args.paths:
        counts = audit(path, args.floor)
        supported += int(counts.gains > 0 and counts.regressions == 0)
        regressions += counts.regressions
        print(
            f"{path.name}: candidates={counts.candidates} gains={counts.gains} "
            f"regressions={counts.regressions}"
        )
    print(
        "dominant_seventh_extension: "
        f"supported_corpora={supported}/{len(args.paths)} regressions={regressions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
