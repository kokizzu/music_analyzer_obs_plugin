#!/usr/bin/env python3
"""Summarize per-window MAPS piano note and chord detection traits."""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path


def labels(value: str) -> list[str]:
    return [] if value in {"", "--"} else value.split(",")


def top(counter: collections.Counter[str], limit: int) -> str:
    return " ".join(f"{name}={count}" for name, count in counter.most_common(limit)) or "none"


def summarize(path: Path, limit: int) -> list[str]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"missing_pcs", "extra_pcs", "expected_chords", "chord_hit", "keyboard_chord"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing MAPS attribute columns")

    missing_components: collections.Counter[str] = collections.Counter()
    extra_components: collections.Counter[str] = collections.Counter()
    missing_patterns: collections.Counter[str] = collections.Counter()
    chord_misses: collections.Counter[str] = collections.Counter()
    chord_miss_predictions: collections.Counter[str] = collections.Counter()
    no_chord_detected_pc_counts: collections.Counter[int] = collections.Counter()
    no_keyboard_chord = 0
    complete_pitch_chord_misses = 0
    for row in rows:
        missing = labels(row["missing_pcs"])
        extra = labels(row["extra_pcs"])
        missing_components.update(missing)
        extra_components.update(extra)
        if missing:
            missing_patterns[row["missing_pcs"]] += 1
        expected_chords = labels(row["expected_chords"])
        if expected_chords and row["chord_hit"] != "1":
            chord_misses[row["expected_chords"]] += 1
            chord_miss_predictions[row["keyboard_chord"]] += 1
            if row["keyboard_chord"] == "--":
                no_keyboard_chord += 1
                no_chord_detected_pc_counts[len(labels(row["detected_chord_pcs"]))] += 1
            complete_pitch_chord_misses += not labels(row["missing_pcs"])

    chord_windows = sum(bool(labels(row["expected_chords"])) for row in rows)
    return [
        f"analyze_maps_piano_attributes: windows={len(rows)} chord_windows={chord_windows}",
        "missing pitch-class components " + top(missing_components, limit),
        "extra keyboard pitch-class components " + top(extra_components, limit),
        "top missing pitch-class patterns " + top(missing_patterns, limit),
        f"chord misses={sum(chord_misses.values())}/{chord_windows} no_keyboard_chord={no_keyboard_chord}",
        "no-label missed windows by chord-grid pitch classes " + top(no_chord_detected_pc_counts, limit),
        f"chord misses with every expected pitch class visible={complete_pitch_chord_misses}/{sum(chord_misses.values())}",
        "top missed expected chord labels " + top(chord_misses, limit),
        "keyboard labels on chord misses " + top(chord_miss_predictions, limit),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    try:
        print("\n".join(summarize(args.input, max(1, args.limit))))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
