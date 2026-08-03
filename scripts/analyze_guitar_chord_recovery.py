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
PROMOTION_RATIOS = (0.005, 0.010, 0.015, 0.020, 0.030, 0.040)
PROMOTION_SOURCES = (
    ("probe", "internal-probe"),
    ("melodic", "internal-melodic-probe"),
    ("raw", "test-raw-profile"),
)
PROMOTION_SCOPES = (
    ("all-candidates", None, None),
    ("labels<=5", None, 5),
    ("any_power", "any_power", None),
    ("first_power", "first_power", None),
    ("primary_power", "primary_power", None),
)
SOURCE_PRIMARY_CHORD_FIELDS = (
    ("guitar_raw_chord", "raw-chord-primary"),
    ("guitar_smoothed_chord", "smoothed-chord-primary"),
)
SOURCE_PRIMARY_LEVEL_FLOORS = (0.20, 0.30, 0.40)
SOURCE_PRIMARY_OPPOSITE_MARGINS = (1.20, 1.50, 1.80)
SOURCE_PRIMARY_MAX_PITCH_CLASSES = (4, 5, 6)


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


def displayed_label_count(row: dict[str, str]) -> int:
    return len(split_labels(row.get("guitar_chord", "")))


def plain_primary_label(value: str) -> str:
    labels = split_labels(value)
    if not labels:
        return ""
    return labels[0] if is_plain_major_or_minor(labels[0]) else ""


def root_third_supported_by_grids(row: dict[str, str], label: str, root: int) -> bool:
    third = expected_third(label, root) % 12
    display_levels = parse_cell_levels(row.get("guitar_cells", ""))
    analysis_levels = parse_cell_levels(row.get("guitar_analysis_cells", ""))
    visible = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    return (
        root in visible
        and third in visible
        and root in analysis
        and third in analysis
        and display_levels.get(root, 0.0) >= 0.08
        and display_levels.get(third, 0.0) >= 0.08
        and analysis_levels.get(root, 0.0) >= 0.08
        and analysis_levels.get(third, 0.0) >= 0.08
    )


def source_primary_rescue_candidate(
    row: dict[str, str],
    chord_field: str,
    level_source: str,
    level_floor: float,
    opposite_margin: float,
    max_pitch_classes: int,
) -> str:
    source_primary = plain_primary_label(row.get(chord_field, ""))
    if not source_primary:
        return ""
    displayed_labels = split_labels(row.get("guitar_chord", ""))
    if displayed_labels and displayed_labels[0] == source_primary:
        return ""
    if displayed_label_count(row) > max_pitch_classes:
        return ""
    if len(pitch_classes(row.get("guitar_pitch_classes", ""))) > max_pitch_classes:
        return ""
    if len(pitch_classes(row.get("guitar_analysis_pitch_classes", ""))) > max_pitch_classes:
        return ""

    root = expected_root(source_primary)
    if root is None or not root_third_supported_by_grids(row, source_primary, root):
        return ""

    levels = source_levels(row, level_source)
    if not levels:
        return ""
    third = expected_third(source_primary, root)
    fifth = (root + 7) % 12
    opposite_third = (root + (4 if is_minor_label(source_primary) else 3)) % 12
    root_level = levels.get(root, 0.0)
    third_level = levels.get(third % 12, 0.0)
    fifth_level = levels.get(fifth, 0.0)
    opposite_level = levels.get(opposite_third, 0.0)
    anchor = max(root_level, fifth_level)
    if anchor <= 0.0:
        return ""
    if third_level < level_floor or fifth_level < level_floor:
        return ""
    if third_level < anchor * 0.16 or fifth_level < anchor * 0.16:
        return ""
    if third_level < opposite_level * opposite_margin:
        return ""
    return source_primary


def source_primary_rescue_rows(
    rows: list[dict[str, str]],
    chord_field: str,
    level_source: str,
    level_floor: float,
    opposite_margin: float,
    max_pitch_classes: int,
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for row in rows:
        expected = {
            label for label in split_labels(row.get("expected_chords", "")) if is_plain_major_or_minor(label)
        }
        if not expected:
            continue
        rescued = source_primary_rescue_candidate(
            row, chord_field, level_source, level_floor, opposite_margin, max_pitch_classes
        )
        if rescued and rescued in expected:
            candidates.append(row)
    return candidates


def protected_false_source_primary_rescues(
    rows: list[dict[str, str]],
    chord_field: str,
    level_source: str,
    level_floor: float,
    opposite_margin: float,
    max_pitch_classes: int,
) -> list[tuple[dict[str, str], str]]:
    false_promotions: list[tuple[dict[str, str], str]] = []
    for row in rows:
        expected = {
            label for label in split_labels(row.get("expected_chords", "")) if is_plain_major_or_minor(label)
        }
        if not expected:
            continue
        rescued = source_primary_rescue_candidate(
            row, chord_field, level_source, level_floor, opposite_margin, max_pitch_classes
        )
        if rescued and rescued not in expected:
            false_promotions.append((row, rescued))
    return false_promotions


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


def promotion_rows(
    rows: list[dict[str, str]],
    ratio: float,
    absolute_floor: float,
    source: str,
    mode: str | None,
    max_label_count: int | None,
) -> list[dict[str, str]]:
    candidates = []
    for row in rows:
        if max_label_count is not None and displayed_label_count(row) > max_label_count:
            continue
        if promotion_candidate(row, ratio, absolute_floor, source, mode):
            candidates.append(row)
    return candidates


def ranked_promotion_opportunities(
    rows: list[dict[str, str]], protected_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []
    for source, label in PROMOTION_SOURCES:
        if not any(source_levels(row, source) for row in rows):
            continue
        for ratio in PROMOTION_RATIOS:
            for scope, mode, max_label_count in PROMOTION_SCOPES:
                candidates = promotion_rows(rows, ratio, 0.005, source, mode, max_label_count)
                if not candidates:
                    continue
                protected_mode = mode or "any_power"
                false_promotions = protected_false_promotions(
                    protected_rows, ratio, 0.005, source, protected_mode, max_label_count
                )
                options.append(
                    {
                        "source": label,
                        "scope": scope,
                        "ratio": ratio,
                        "recover": len(candidates),
                        "same_root_pow": sum(1 for row in candidates if same_root_power_candidate(row)),
                        "protected_false": len(false_promotions),
                    }
                )

    best_by_scope: dict[tuple[str, str], dict[str, object]] = {}
    for option in options:
        key = (str(option["source"]), str(option["scope"]))
        current = best_by_scope.get(key)
        if current is None:
            best_by_scope[key] = option
            continue
        option_key = (
            int(option["protected_false"]),
            -int(option["recover"]),
            -int(option["same_root_pow"]),
            float(option["ratio"]),
        )
        current_key = (
            int(current["protected_false"]),
            -int(current["recover"]),
            -int(current["same_root_pow"]),
            float(current["ratio"]),
        )
        if option_key < current_key:
            best_by_scope[key] = option

    return sorted(
        best_by_scope.values(),
        key=lambda option: (
            int(option["protected_false"]),
            -int(option["recover"]),
            -int(option["same_root_pow"]),
            str(option["source"]),
            str(option["scope"]),
            float(option["ratio"]),
        ),
    )


def append_ranked_promotion_summary(lines: list[str], options: list[dict[str, object]], limit: int) -> None:
    lines.append("ranked same-root promotion opportunities")
    if not options:
        lines.append("  no recoverable promotion opportunities")
        return

    zero_false = [option for option in options if int(option["protected_false"]) == 0]
    if zero_false:
        best = zero_false[0]
        lines.append(
            "  best_zero_false "
            f"{best['source']} {best['scope']} "
            f"floor=max(anchor*{float(best['ratio']):.3f},0.005) "
            f"recover={best['recover']} same_root_pow={best['same_root_pow']}"
        )
    else:
        lines.append("  no zero-protected recovery option found")

    for option in options[: max(0, limit)]:
        lines.append(
            "  "
            f"{option['source']} {option['scope']} "
            f"floor=max(anchor*{float(option['ratio']):.3f},0.005) "
            f"recover={option['recover']} same_root_pow={option['same_root_pow']} "
            f"protected_false={option['protected_false']}"
        )


def ranked_source_primary_rescues(
    rows: list[dict[str, str]], protected_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []
    for chord_field, chord_label in SOURCE_PRIMARY_CHORD_FIELDS:
        if not any(plain_primary_label(row.get(chord_field, "")) for row in rows):
            continue
        for level_source, level_label in PROMOTION_SOURCES:
            if not any(source_levels(row, level_source) for row in rows):
                continue
            for level_floor in SOURCE_PRIMARY_LEVEL_FLOORS:
                for opposite_margin in SOURCE_PRIMARY_OPPOSITE_MARGINS:
                    for max_pitch_classes in SOURCE_PRIMARY_MAX_PITCH_CLASSES:
                        candidates = source_primary_rescue_rows(
                            rows,
                            chord_field,
                            level_source,
                            level_floor,
                            opposite_margin,
                            max_pitch_classes,
                        )
                        if not candidates:
                            continue
                        false_promotions = protected_false_source_primary_rescues(
                            protected_rows,
                            chord_field,
                            level_source,
                            level_floor,
                            opposite_margin,
                            max_pitch_classes,
                        )
                        options.append(
                            {
                                "chord": chord_label,
                                "source": level_label,
                                "floor": level_floor,
                                "opposite_margin": opposite_margin,
                                "max_pitch_classes": max_pitch_classes,
                                "recover": len(candidates),
                                "protected_false": len(false_promotions),
                            }
                        )

    best_by_scope: dict[tuple[str, str, int], dict[str, object]] = {}
    for option in options:
        key = (
            str(option["chord"]),
            str(option["source"]),
            int(option["max_pitch_classes"]),
        )
        current = best_by_scope.get(key)
        if current is None:
            best_by_scope[key] = option
            continue
        option_key = (
            int(option["protected_false"]),
            -int(option["recover"]),
            -float(option["floor"]),
            -float(option["opposite_margin"]),
        )
        current_key = (
            int(current["protected_false"]),
            -int(current["recover"]),
            -float(current["floor"]),
            -float(current["opposite_margin"]),
        )
        if option_key < current_key:
            best_by_scope[key] = option

    return sorted(
        best_by_scope.values(),
        key=lambda option: (
            int(option["protected_false"]),
            -int(option["recover"]),
            str(option["chord"]),
            str(option["source"]),
            int(option["max_pitch_classes"]),
            -float(option["floor"]),
            -float(option["opposite_margin"]),
        ),
    )


def append_source_primary_rescue_summary(
    lines: list[str], rows: list[dict[str, str]], protected_rows: list[dict[str, str]], limit: int
) -> None:
    options = ranked_source_primary_rescues(rows, protected_rows)
    lines.append("ranked source-primary rescue opportunities")
    if not options:
        lines.append("  no source-primary rescue opportunities")
        return

    zero_false = [option for option in options if int(option["protected_false"]) == 0]
    if zero_false:
        best = zero_false[0]
        lines.append(
            "  best_zero_false "
            f"{best['chord']} {best['source']} "
            f"floor={float(best['floor']):.2f} opposite_margin={float(best['opposite_margin']):.2f} "
            f"max_pc={best['max_pitch_classes']} recover={best['recover']}"
        )
    else:
        lines.append("  no zero-protected source-primary rescue option found")

    printed = 0
    for option in options[: max(0, limit)]:
        lines.append(
            "  "
            f"{option['chord']} {option['source']} "
            f"floor={float(option['floor']):.2f} "
            f"opposite_margin={float(option['opposite_margin']):.2f} "
            f"max_pc={option['max_pitch_classes']} recover={option['recover']} "
            f"protected_false={option['protected_false']}"
        )
        if printed >= limit:
            continue
        chord_field = next(
            field for field, label in SOURCE_PRIMARY_CHORD_FIELDS if label == option["chord"]
        )
        level_source = next(
            source for source, label in PROMOTION_SOURCES if label == option["source"]
        )
        candidates = source_primary_rescue_rows(
            rows,
            chord_field,
            level_source,
            float(option["floor"]),
            float(option["opposite_margin"]),
            int(option["max_pitch_classes"]),
        )
        for row in candidates[: max(0, limit - printed)]:
            rescued = source_primary_rescue_candidate(
                row,
                chord_field,
                level_source,
                float(option["floor"]),
                float(option["opposite_margin"]),
                int(option["max_pitch_classes"]),
            )
            levels = source_levels(row, level_source)
            root = expected_root(rescued) if rescued else None
            root_value = third_value = fifth_value = "--"
            if root is not None:
                root_value = level(levels, root)
                third_value = level(levels, expected_third(rescued, root))
                fifth_value = level(levels, root + 7)
            lines.append(
                "    "
                f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                f"got={row.get('guitar_chord', '--')} rescued={rescued} "
                f"{level_source}={root_value}/{third_value}/{fifth_value}"
            )
            printed += 1
        false_promotions = protected_false_source_primary_rescues(
            protected_rows,
            chord_field,
            level_source,
            float(option["floor"]),
            float(option["opposite_margin"]),
            int(option["max_pitch_classes"]),
        )
        for row, rescued in false_promotions[: max(0, limit - printed)]:
            lines.append(
                "    protected "
                f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                f"got={row.get('guitar_chord', '--')} rescued={rescued}"
            )
            printed += 1


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
        for ratio in PROMOTION_RATIOS:
            candidates = [row for row in rows if promotion_candidate(row, ratio, 0.005, source)]
            power_candidates = [row for row in candidates if same_root_power_candidate(row)]
            false_promotions = protected_false_promotions(
                protected_rows, ratio, 0.005, source, "any_power"
            )
            bounded_label_candidates = [
                row for row in candidates if displayed_label_count(row) <= 5
            ]
            bounded_label_false = protected_false_promotions(
                protected_rows, ratio, 0.005, source, "any_power", 5
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
                f"labels<=5={len(bounded_label_candidates)}/{len(bounded_label_false)}"
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
            if bounded_label_candidates and not bounded_label_false:
                lines.append(
                    f"    zero_false labels<=5 recover={len(bounded_label_candidates)} "
                    "mode=any_power"
                )
                for row in bounded_label_candidates[: min(examples, limit)]:
                    levels = source_levels(row, source)
                    labels = split_labels(row.get("expected_chords", ""))
                    root = expected_root(labels[0]) if labels else None
                    root_value = third_value = fifth_value = "--"
                    if root is not None:
                        root_value = level(levels, root)
                        third_value = level(levels, expected_third(labels[0], root))
                        fifth_value = level(levels, root + 7)
                    lines.append(
                        "      bounded "
                        f"{row.get('recording_id', '')} "
                        f"labels={displayed_label_count(row)} "
                        f"expected={row.get('expected_chords', '')} "
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
    append_ranked_promotion_summary(lines, ranked_promotion_opportunities(rows, protected_rows), limit)
    append_source_primary_rescue_summary(lines, rows, protected_rows, limit)
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
