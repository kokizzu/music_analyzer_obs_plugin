#!/usr/bin/env python3
"""Inspect GuitarSet-style chord misses for recoverable pitch-class support."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re

from inspect_guitarset_attribute_buckets import derive_row as derive_guitarset_row


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


def compact(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def expected_root(label: str) -> int | None:
    root = chord_root(label)
    return NOTE_TO_PC.get(root)


def note_name(pitch_class: int) -> str:
    for name, value in NOTE_TO_PC.items():
        if value == pitch_class % 12:
            return name
    return "?"


def is_minor_label(label: str) -> bool:
    return label.endswith("m") and not label.endswith("maj")


def is_plain_major_or_minor(label: str) -> bool:
    if not label:
        return False
    if label.endswith("m") and not label.endswith("maj"):
        return True
    root = chord_root(label)
    return label == root


def is_power_label(label: str) -> bool:
    return label.endswith("pow")


def first_power_label(labels: list[str]) -> str:
    for label in labels:
        if is_power_label(label):
            return label
    return ""


def label_has_root_third_component(labels: list[str], root: int) -> bool:
    for label in labels:
        if expected_root(label) != root:
            continue
        if is_plain_major_or_minor(label):
            return True
    return False


def plain_label_for(root: int, minor: bool) -> str:
    return f"{note_name(root)}{'m' if minor else ''}"


def power_root_allowed(labels: list[str], root: int, mode: str) -> bool:
    power_label = f"{note_name(root)}pow"
    if mode == "any_power":
        return power_label in labels
    if mode == "first_power":
        return first_power_label(labels) == power_label
    if mode == "primary_power":
        return bool(labels) and labels[0] == power_label
    raise ValueError(f"unknown power promotion mode `{mode}`")


def visible_and_analysis_root_fifth(row: dict[str, str], root: int) -> bool:
    fifth = (root + 7) % 12
    visible = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    return root in visible and fifth in visible and root in analysis and fifth in analysis


def source_levels(row: dict[str, str], source: str) -> dict[int, float]:
    if source == "probe":
        return parse_cell_levels(row.get("guitar_probe_pitch_class_levels", ""))
    if source == "melodic":
        return parse_cell_levels(row.get("guitar_melodic_probe_pitch_class_levels", ""))
    if source == "raw":
        levels = parse_cell_levels(row.get("raw_pitch_class_levels", ""))
        if not levels:
            levels = parse_cell_levels(row.get("expected_raw_cells", ""))
        return levels
    raise ValueError(f"unknown level source `{source}`")


def raw_levels(row: dict[str, str]) -> dict[int, float]:
    for source in ("probe", "melodic", "raw"):
        levels = source_levels(row, source)
        if levels:
            return levels
    return {}


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

        levels = raw_levels(row)
        result["raw_root"] = level(levels, root)
        result["raw_third"] = level(levels, expected_third(labels[0], root))
        result["raw_fifth"] = level(levels, root + 7)
    return result


def promotion_candidate(
    row: dict[str, str],
    ratio: float,
    absolute_floor: float,
    source: str,
    mode: str | None = None,
) -> bool:
    labels = split_labels(row.get("expected_chords", ""))
    if not labels:
        return False
    label = labels[0]
    root = expected_root(label)
    if root is None or not visible_and_analysis_root_fifth(row, root):
        return False
    if mode is not None and not power_root_allowed(split_labels(row.get("guitar_chord", "")), root, mode):
        return False

    levels = source_levels(row, source)
    if not levels:
        return False
    root_level = levels.get(root, 0.0)
    fifth_level = levels.get((root + 7) % 12, 0.0)
    third = expected_third(label, root)
    opposite_third = root + (4 if is_minor_label(label) else 3)
    third_level = levels.get(third % 12, 0.0)
    opposite_level = levels.get(opposite_third % 12, 0.0)
    floor = max(max(root_level, fifth_level) * ratio, absolute_floor)
    return third_level >= floor and third_level >= opposite_level * 1.10


def promoted_quality_for_power_root(
    row: dict[str, str], root: int, ratio: float, absolute_floor: float, source: str
) -> str | None:
    if not visible_and_analysis_root_fifth(row, root):
        return None

    levels = source_levels(row, source)
    if not levels:
        return None
    root_level = levels.get(root, 0.0)
    fifth_level = levels.get((root + 7) % 12, 0.0)
    anchor = max(root_level, fifth_level)
    if anchor <= 0.0:
        return None

    minor_third = levels.get((root + 3) % 12, 0.0)
    major_third = levels.get((root + 4) % 12, 0.0)
    floor = max(anchor * ratio, absolute_floor)
    choose_minor = minor_third >= floor and minor_third >= major_third * 1.10
    choose_major = major_third >= floor and major_third >= minor_third * 1.10
    if choose_minor == choose_major:
        return None
    return plain_label_for(root, choose_minor)


def same_root_power_candidate(row: dict[str, str]) -> bool:
    labels = split_labels(row.get("expected_chords", ""))
    if not labels:
        return False
    root = expected_root(labels[0])
    if root is None:
        return False
    root_name = note_name(root)
    return f"{root_name}pow" in split_labels(row.get("guitar_chord", ""))


def protected_false_promotions(
    rows: list[dict[str, str]],
    ratio: float,
    absolute_floor: float,
    source: str,
    mode: str = "any_power",
    max_label_count: int | None = None,
) -> list[tuple[dict[str, str], str]]:
    false_promotions: list[tuple[dict[str, str], str]] = []
    for row in rows:
        expected = {
            label for label in split_labels(row.get("expected_chords", "")) if is_plain_major_or_minor(label)
        }
        if not expected:
            continue
        displayed_labels = split_labels(row.get("guitar_chord", ""))
        if max_label_count is not None and len(displayed_labels) > max_label_count:
            continue
        for label in displayed_labels:
            if not is_power_label(label):
                continue
            root = expected_root(label)
            if root is None:
                continue
            if not power_root_allowed(displayed_labels, root, mode):
                continue
            if label_has_root_third_component(displayed_labels, root):
                continue
            promoted = promoted_quality_for_power_root(row, root, ratio, absolute_floor, source)
            if promoted and promoted not in expected:
                false_promotions.append((row, promoted))
                break
    return false_promotions


def summarize(path: pathlib.Path, examples: int, limit: int) -> list[str]:
    all_rows = [derive_guitarset_row(row) for row in load_rows(path)]
    rows = [row for row in all_rows if row.get("status") == "chord_miss"]
    protected_rows = [row for row in all_rows if row.get("status") == "chord_hit"]
    lines = [f"guitar chord recovery rows={len(rows)}"]
    lines.append(
        "evidence classes "
        f"{compact(collections.Counter(row.get('evidence_class', '--') or '--' for row in rows))}"
    )
    lines.append(
        "evidence sources "
        f"{compact(collections.Counter(row.get('evidence_source', '--') or '--' for row in rows))}"
    )
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

    for source, label in (
        ("probe", "internal-probe"),
        ("melodic", "internal-melodic-probe"),
        ("raw", "test-raw-profile"),
    ):
        if not any(source_levels(row, source) for row in rows):
            continue
        lines.append(f"{label} same-root promotion simulation")
        for ratio in (0.005, 0.010, 0.015, 0.020, 0.030, 0.040):
            candidates = [row for row in rows if promotion_candidate(row, ratio, 0.005, source)]
            power_candidates = [row for row in candidates if same_root_power_candidate(row)]
            false_promotions = protected_false_promotions(
                protected_rows, ratio, 0.005, source, "any_power"
            )
            first_power_candidates = [
                row for row in rows if promotion_candidate(row, ratio, 0.005, source, "first_power")
            ]
            primary_power_candidates = [
                row for row in rows if promotion_candidate(row, ratio, 0.005, source, "primary_power")
            ]
            first_power_false = protected_false_promotions(
                protected_rows, ratio, 0.005, source, "first_power"
            )
            primary_power_false = protected_false_promotions(
                protected_rows, ratio, 0.005, source, "primary_power"
            )
            lines.append(
                f"  floor=max(anchor*{ratio:.3f},0.005) recover={len(candidates)} "
                f"same_root_pow={len(power_candidates)} protected_false={len(false_promotions)} "
                f"first_power={len(first_power_candidates)}/{len(first_power_false)} "
                f"primary_power={len(primary_power_candidates)}/{len(primary_power_false)} "
                f"labels<=5={len([row for row in candidates if len(split_labels(row.get('guitar_chord', ''))) <= 5])}/"
                f"{len(protected_false_promotions(protected_rows, ratio, 0.005, source, 'any_power', 5))}"
            )
            for row in candidates[: min(examples, limit)]:
                levels = source_levels(row, source)
                labels = split_labels(row.get("expected_chords", ""))
                root = expected_root(labels[0]) if labels else None
                root_value = third_value = fifth_value = "--"
                if root is not None:
                    root_value = level(levels, root)
                    third_value = level(levels, expected_third(labels[0], root))
                    fifth_value = level(levels, root + 7)
                lines.append(
                    "    "
                    f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                    f"got={row.get('guitar_chord', '--')} "
                    f"{source}={root_value}/{third_value}/{fifth_value}"
                )
            for row in primary_power_candidates[: min(examples, limit)]:
                levels = source_levels(row, source)
                labels = split_labels(row.get("expected_chords", ""))
                root = expected_root(labels[0]) if labels else None
                root_value = third_value = fifth_value = "--"
                if root is not None:
                    root_value = level(levels, root)
                    third_value = level(levels, expected_third(labels[0], root))
                    fifth_value = level(levels, root + 7)
                lines.append(
                    "    primary "
                    f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                    f"got={row.get('guitar_chord', '--')} "
                    f"{source}={root_value}/{third_value}/{fifth_value}"
                )
            for row, promoted in false_promotions[: min(examples, limit)]:
                lines.append(
                    "    protected "
                    f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                    f"got={row.get('guitar_chord', '--')} promoted={promoted}"
                )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--examples", type=int, default=12)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="maximum examples to print for each simulation subsection; defaults to --examples",
    )
    args = parser.parse_args()

    examples = max(0, args.examples)
    limit = examples if args.limit is None else max(0, args.limit)
    for line in summarize(pathlib.Path(args.path), examples, limit):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
