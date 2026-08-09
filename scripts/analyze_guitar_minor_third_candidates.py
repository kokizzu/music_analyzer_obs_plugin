#!/usr/bin/env python3
"""Sweep compact plain-triad third recovery evidence in guitar attribute TSVs."""

from __future__ import annotations

import argparse
import pathlib

from summarize_guitarset_attributes import (
    NOTE_TO_PC,
    chord_root,
    load_rows,
    parse_cell_levels,
    parse_pitch_classes,
    split_chord_components,
)


ANALYSIS_FLOORS = (0.01, 0.02, 0.04, 0.08, 0.09, 0.10, 0.12, 0.16, 0.20)
PROBE_FLOORS = (0.00, 0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50)


def plain_quality(component: str, quality: str) -> bool:
    root = chord_root(component)
    suffix = component[len(root) :] if root else ""
    return bool(root) and suffix == ("m" if quality == "minor" else "")


def collect(path: pathlib.Path, quality: str) -> list[tuple[bool, float, float, dict[str, str]]]:
    rows: list[tuple[bool, float, float, dict[str, str]]] = []
    for row in load_rows(path):
        labels = split_chord_components(row.get("guitar_chord", ""))
        if len(labels) != 1 or not plain_quality(labels[0], quality):
            continue
        root = NOTE_TO_PC[chord_root(labels[0])]
        third = (root + (3 if quality == "minor" else 4)) % 12
        fifth = (root + 7) % 12
        visible = parse_pitch_classes(row.get("guitar_pitch_classes", ""))
        analysis = parse_cell_levels(row.get("guitar_analysis_cells", ""))
        if root not in visible or fifth not in visible or third in visible or third not in analysis:
            continue
        probe = parse_cell_levels(row.get("guitar_probe_pitch_class_levels", ""))
        expected = parse_pitch_classes(row.get("expected_pitch_classes", ""))
        rows.append((third in expected, analysis[third], probe.get(third, 0.0), row))
    return rows


def report(path: pathlib.Path, quality: str) -> None:
    rows = collect(path, quality)
    positive = sum(correct for correct, _, _, _ in rows)
    print(f"{path.name}: candidates={len(rows)} recoveries={positive} false={len(rows) - positive}")
    for analysis_floor in ANALYSIS_FLOORS:
        for probe_floor in PROBE_FLOORS:
            selected = [row for row in rows if row[1] >= analysis_floor and row[2] >= probe_floor]
            recoveries = sum(correct for correct, _, _, _ in selected)
            false = len(selected) - recoveries
            if recoveries and false == 0:
                print(f"  safe analysis>={analysis_floor:.2f} probe>={probe_floor:.2f}: +{recoveries}")
    for correct, analysis, probe, row in rows:
        print(
            f"  {'recover' if correct else 'false':7} a={analysis:.3f} probe={probe:.3f} "
            f"expected={row.get('expected_chords', '--')} guitar={row.get('guitar_chord', '--')} "
            f"{row.get('recording_id', '--')}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=("minor", "major"), default="minor")
    parser.add_argument("path", nargs="+", type=pathlib.Path)
    args = parser.parse_args()
    for path in args.path:
        report(path, args.quality)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
