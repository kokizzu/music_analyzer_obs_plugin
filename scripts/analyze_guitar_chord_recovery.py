#!/usr/bin/env python3
"""Inspect GuitarSet-style chord misses for recoverable pitch-class support."""

from __future__ import annotations

import argparse
import csv
import pathlib
import re


NOTE_TO_PC = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

CELL_RE = re.compile(r"^([A-G]#?)(?:-?\d+)?:([0-9.]+)$")


def chord_root(label: str) -> str:
    if len(label) >= 2 and label[1] == "#":
        return label[:2]
    return label[:1]


def split_labels(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [label for label in value.replace("/", "=").split("=") if label]


def pitch_classes(value: str) -> set[int]:
    if not value or value == "--":
        return set()
    return {NOTE_TO_PC[item] for item in value.split(",") if item in NOTE_TO_PC}


def parse_cell_levels(value: str) -> dict[int, float]:
    levels: dict[int, float] = {}
    if not value or value == "--":
        return levels
    for item in value.split(","):
        match = CELL_RE.match(item)
        if not match:
            continue
        pitch_class = NOTE_TO_PC.get(match.group(1))
        if pitch_class is None:
            continue
        try:
            level = float(match.group(2))
        except ValueError:
            continue
        levels[pitch_class] = max(levels.get(pitch_class, 0.0), level)
    return levels


def level(levels: dict[int, float], pitch_class: int) -> str:
    return f"{levels.get(pitch_class % 12, 0.0):.3f}".rstrip("0").rstrip(".")


def expected_third(label: str, root: int) -> int:
    return root + 3 if label.endswith("m") and not label.endswith("maj") else root + 4


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expected_root(label: str) -> int | None:
    root = chord_root(label)
    return NOTE_TO_PC.get(root)


def add_derived_fields(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    labels = split_labels(row.get("expected_chords", ""))
    root = expected_root(labels[0]) if labels else None

    visible = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smooth = pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    if root is not None:
        tones = {root, expected_third(labels[0], root) % 12, (root + 7) % 12}
        root_visible = int(root in visible)
        result["support"] = (
            f"visible{len(tones & visible)}_analysis{len(tones & analysis)}_"
            f"smooth{len(tones & smooth)}_rootvis{root_visible}"
        )

        raw_levels = parse_cell_levels(row.get("raw_pitch_class_levels", ""))
        if not raw_levels:
            raw_levels = parse_cell_levels(row.get("expected_raw_cells", ""))
        result["raw_root"] = level(raw_levels, root)
        result["raw_third"] = level(raw_levels, expected_third(labels[0], root))
        result["raw_fifth"] = level(raw_levels, root + 7)
    return result


def summarize(path: pathlib.Path, examples: int) -> list[str]:
    rows = [add_derived_fields(row) for row in load_rows(path) if row.get("status") == "chord_miss"]
    lines = [f"guitar chord recovery rows={len(rows)}"]
    for field in (
        "guitar_pitch_classes",
        "guitar_analysis_pitch_classes",
        "guitar_smoothed_pitch_classes",
    ):
        recoverable = []
        for row in rows:
            labels = split_labels(row.get("expected_chords", ""))
            if not labels:
                continue
            root = expected_root(labels[0])
            if root is None:
                continue
            current = pitch_classes(row.get(field, ""))
            if root in current and (root + 7) % 12 in current:
                recoverable.append(row)
        lines.append(f"{field} root+fifth={len(recoverable)}")
        for row in recoverable[:examples]:
            lines.append(
                "  "
                f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                f"got={row.get('guitar_chord', '--')} pc={row.get(field, '--')} "
                f"support={row.get('support', '--')} "
                f"raw={row.get('raw_root', '--')}/{row.get('raw_third', '--')}/{row.get('raw_fifth', '--')}"
            )

    combined = []
    for row in rows:
        labels = split_labels(row.get("expected_chords", ""))
        if not labels:
            continue
        root = expected_root(labels[0])
        if root is None:
            continue
        visible = pitch_classes(row.get("guitar_pitch_classes", ""))
        analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
        if (
            root in visible
            and (root + 7) % 12 in visible
            and root in analysis
            and (root + 7) % 12 in analysis
        ):
            combined.append(row)
    lines.append(f"visible+analysis root+fifth={len(combined)}")
    for row in combined[:examples]:
        lines.append(
            "  "
            f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
            f"got={row.get('guitar_chord', '--')} "
            f"visible={row.get('guitar_pitch_classes', '--')} "
            f"analysis={row.get('guitar_analysis_pitch_classes', '--')}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--examples", type=int, default=12)
    args = parser.parse_args()

    for line in summarize(pathlib.Path(args.path), max(0, args.examples)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
