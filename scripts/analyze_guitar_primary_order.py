#!/usr/bin/env python3
"""Inspect guitar chord primary-label ordering from exported attribute rows."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
from collections.abc import Callable


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

PC_TO_NOTE = {value: key for key, value in NOTE_TO_PC.items()}
CELL_RE = re.compile(r"([A-G]#?)(?:-?\d+)?:([-+0-9.eE]+)")
CHORD_INTERVALS = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "6": (0, 4, 7, 9),
    "7": (0, 4, 7, 10),
    "9": (0, 2, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "maj9": (0, 2, 4, 7, 11),
    "add9": (0, 2, 4, 7),
    "m6": (0, 3, 7, 9),
    "m7": (0, 3, 7, 10),
    "m9": (0, 2, 3, 7, 10),
}


def split_components(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [item for item in re.split(r"[=/]", value) if item and item != "--"]


def chord_root(label: str) -> str:
    if len(label) >= 2 and label[1] == "#":
        return label[:2]
    return label[:1]


def chord_quality(label: str) -> str:
    root = chord_root(label)
    return label[len(root) :]


def parse_plain(label: str) -> tuple[int, bool] | None:
    root_name = chord_root(label)
    if root_name not in NOTE_TO_PC:
        return None
    quality = chord_quality(label)
    if quality == "":
        return NOTE_TO_PC[root_name], False
    if quality == "m":
        return NOTE_TO_PC[root_name], True
    return None


def extension_family(label: str) -> tuple[int, str] | None:
    root_name = chord_root(label)
    if root_name not in NOTE_TO_PC:
        return None
    quality = chord_quality(label)
    if quality in {"6", "7", "9", "maj7", "maj9", "add9"}:
        return NOTE_TO_PC[root_name], "major"
    if quality in {"m6", "m7", "m9"}:
        return NOTE_TO_PC[root_name], "minor"
    return None


def chord_pitch_set(label: str) -> set[int] | None:
    root_name = chord_root(label)
    if root_name not in NOTE_TO_PC:
        return None
    quality = chord_quality(label)
    intervals = CHORD_INTERVALS.get(quality)
    if intervals is None:
        return None
    root = NOTE_TO_PC[root_name]
    return {(root + interval) % 12 for interval in intervals}


def same_root_extension_primary_candidate(components: list[str]) -> str | None:
    if not components:
        return None
    primary = parse_plain(components[0])
    if primary is None:
        return None
    primary_root, primary_minor = primary
    primary_family = "minor" if primary_minor else "major"
    for component in components[1:]:
        family = extension_family(component)
        if family == (primary_root, primary_family):
            return component
    return None


def current_same_root_extension_primary(components: list[str]) -> tuple[str, str] | None:
    if not components:
        return None
    family = extension_family(components[0])
    if family is None:
        return None
    root, quality_family = family
    plain = f"{PC_TO_NOTE[root]}{'m' if quality_family == 'minor' else ''}"
    if plain not in components[1:]:
        return None
    return components[0], plain


def is_power_for_root(label: str, root: int) -> bool:
    return label == f"{PC_TO_NOTE[root % 12]}pow"


def parse_cells(value: str) -> dict[int, float]:
    levels: dict[int, float] = {}
    for match in CELL_RE.finditer(value or ""):
        note = match.group(1)
        if note not in NOTE_TO_PC:
            continue
        try:
            level = float(match.group(2))
        except ValueError:
            continue
        pc = NOTE_TO_PC[note]
        levels[pc] = max(levels.get(pc, 0.0), level)
    return levels


def cell_level_min(levels: dict[int, float], pitch_classes: set[int]) -> float:
    if not pitch_classes:
        return 0.0
    return min(levels.get(pitch_class, 0.0) for pitch_class in pitch_classes)


def primary_component(value: str) -> str:
    components = split_components(value)
    return components[0] if components else "--"


def component_root_pc(label: str) -> int | None:
    root_name = chord_root(label)
    return NOTE_TO_PC.get(root_name)


def primary_quality_bucket(label: str) -> str:
    if not label or label == "--":
        return "none"
    quality = chord_quality(label)
    if quality == "":
        return "plain_major"
    if quality == "m":
        return "plain_minor"
    if quality == "pow":
        return "power"
    if quality in {"sus2", "sus4"}:
        return "sus"
    if quality in {"dim", "dim7", "m7b5", "aug"}:
        return "altered"
    return "extension"


def root_relation(expected: set[str], primary: str) -> str:
    primary_root = component_root_pc(primary)
    if primary_root is None:
        return "no_primary"
    expected_roots = {component_root_pc(label) for label in expected}
    expected_roots.discard(None)
    if primary_root in expected_roots:
        return "same_root"
    return "different_root"


def compact_value(value: str | None, fallback: str = "--") -> str:
    value = value if value not in (None, "") else fallback
    return str(value).replace(" ", "_")


def print_counter(title: str, counter: collections.Counter[str], limit: int) -> None:
    print(title)
    if not counter:
        print("  --")
        return
    for key, value in counter.most_common(limit):
        print(f"  {key}={value}")


def pitch_classes(value: str) -> set[int]:
    if not value or value == "--":
        return set()
    return {NOTE_TO_PC[item] for item in value.split(",") if item in NOTE_TO_PC}


def chord_tones(root: int, minor: bool) -> set[int]:
    return {root % 12, (root + (3 if minor else 4)) % 12, (root + 7) % 12}


def quality_third(root: int, minor: bool) -> int:
    return (root + (3 if minor else 4)) % 12


def plain_label(root: int, minor: bool) -> str:
    return f"{PC_TO_NOTE[root % 12]}{'m' if minor else ''}"


def promoted_same_root_smoothed_quality(
    row: dict[str, str],
    levels_field: str,
    min_third: float,
    ratio: float,
    offset: float,
) -> str | None:
    raw_primary = primary_component(row.get("guitar_raw_chord", ""))
    smoothed_primary = primary_component(row.get("guitar_smoothed_chord", ""))
    raw_plain = parse_plain(raw_primary)
    smoothed_plain = parse_plain(smoothed_primary)
    if raw_plain is None or smoothed_plain is None:
        return None
    if raw_plain[0] != smoothed_plain[0] or raw_plain[1] == smoothed_plain[1]:
        return None

    raw_levels = parse_cells(row.get(levels_field, ""))
    smoothed_third = raw_levels.get(quality_third(smoothed_plain[0], smoothed_plain[1]), 0.0)
    raw_third = raw_levels.get(quality_third(raw_plain[0], raw_plain[1]), 0.0)
    if smoothed_third < min_third:
        return None
    if smoothed_third < raw_third * ratio + offset:
        return None
    return smoothed_primary


def analysis_full_anchor_plain_promotions(row: dict[str, str]) -> list[str]:
    components = set(split_components(row.get("guitar_chord", "")))
    display = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    if not display or not analysis:
        return []

    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    raw_levels = parse_cells(row.get("raw_pitch_class_levels", ""))
    melodic_levels = parse_cells(row.get("guitar_melodic_probe_pitch_class_levels", ""))

    promotions: list[str] = []
    for root in range(12):
        for minor in (False, True):
            label = plain_label(root, minor)
            if label in components:
                continue
            tones = chord_tones(root, minor)
            if not tones <= analysis or len(tones & display) < 1:
                continue

            third = quality_third(root, minor)
            opposite = quality_third(root, not minor)
            root_level = analysis_levels.get(root, 0.0)
            third_level = analysis_levels.get(third, 0.0)
            fifth_level = analysis_levels.get((root + 7) % 12, 0.0)
            anchor = min(root_level, fifth_level)
            if anchor < 0.12 or third_level < max(0.08, anchor * 0.40):
                continue

            raw_third = raw_levels.get(third, 0.0)
            raw_opposite = raw_levels.get(opposite, 0.0)
            melodic_third = melodic_levels.get(third, 0.0)
            melodic_opposite = melodic_levels.get(opposite, 0.0)
            raw_clear = raw_third >= 0.08 and raw_third >= raw_opposite * 1.25
            melodic_clear = melodic_third >= 0.16 and melodic_third >= melodic_opposite * 1.25
            if raw_clear or melodic_clear:
                promotions.append(label)
    return promotions


def component_score(
    label: str,
    display: set[int],
    analysis: set[int],
    display_levels: dict[int, float],
    analysis_levels: dict[int, float],
) -> float:
    parsed = parse_plain(label)
    if parsed is None:
        return -1.0
    root, minor = parsed
    tones = chord_tones(root, minor)
    display_tones = len(tones & display)
    analysis_tones = len(tones & analysis)
    if display_tones < 2 or analysis_tones < 2:
        return -1.0
    third = (root + (3 if minor else 4)) % 12
    opposite = (root + (4 if minor else 3)) % 12
    level = lambda pc: max(display_levels.get(pc % 12, 0.0), analysis_levels.get(pc % 12, 0.0))
    root_level = level(root)
    third_level = level(third)
    fifth_level = level(root + 7)
    anchor = min(root_level, fifth_level)
    opposite_level = level(opposite)
    if anchor < 0.08:
        return -1.0
    if third_level < max(0.012, anchor * 0.018) and display_tones + analysis_tones < 5:
        return -1.0
    if opposite_level >= max(0.18, anchor * 0.55) and opposite_level > third_level * 1.35:
        return -1.0
    return display_tones * 1.15 + analysis_tones * 0.85 + anchor * 0.55 + third_level * 0.35


def score_promotion_candidate(
    row: dict[str, str],
    min_gap: float = 0.02,
) -> tuple[float, str, str, float, float] | None:
    components = split_components(row.get("guitar_chord", ""))
    if len(components) < 2:
        return None

    display = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    display_levels = parse_cells(row.get("guitar_cells", ""))
    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    primary = components[0]
    primary_score = component_score(primary, display, analysis, display_levels, analysis_levels)

    best: tuple[float, int, str] | None = None
    for index, label in enumerate(components[1:], start=1):
        score = component_score(label, display, analysis, display_levels, analysis_levels)
        if score < 0.0:
            continue
        if best is None or score > best[0] or (score == best[0] and index < best[1]):
            best = (score, index, label)
    if best is None:
        return None

    candidate_score, _index, promoted = best
    gap = candidate_score - primary_score
    if gap < min_gap:
        return None
    return gap, promoted, primary, primary_score, candidate_score


def score_feature_row(
    gap: float,
    promoted: str,
    primary: str,
    primary_score: float,
    promoted_score: float,
    row: dict[str, str],
) -> dict[str, str | float]:
    components = split_components(row.get("guitar_chord", ""))
    promoted_index = next(
        (index for index, component in enumerate(components) if component == promoted),
        -1,
    )
    primary_parsed = parse_plain(primary)
    promoted_parsed = parse_plain(promoted)
    display = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smoothed = pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    display_levels = parse_cells(row.get("guitar_cells", ""))
    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    smoothed_levels = parse_cells(row.get("guitar_smoothed_cells", ""))
    probe_levels = parse_cells(row.get("guitar_probe_pitch_class_levels", ""))
    raw_levels = parse_cells(row.get("raw_pitch_class_levels", ""))
    melodic_levels = parse_cells(row.get("guitar_melodic_probe_pitch_class_levels", ""))

    def plain_features(prefix: str, parsed: tuple[int, bool] | None) -> dict[str, str | float]:
        if parsed is None:
            return {
                f"{prefix}_plain": "0",
                f"{prefix}_quality": "other",
                f"{prefix}_display_tones": 0.0,
                f"{prefix}_analysis_tones": 0.0,
                f"{prefix}_smooth_tones": 0.0,
                f"{prefix}_root_visible": 0.0,
                f"{prefix}_root_analysis": 0.0,
                f"{prefix}_root_smooth": 0.0,
                f"{prefix}_root_raw": 0.0,
                f"{prefix}_root_probe": 0.0,
                f"{prefix}_root_melodic": 0.0,
                f"{prefix}_third_raw": 0.0,
                f"{prefix}_third_probe": 0.0,
                f"{prefix}_third_melodic": 0.0,
                f"{prefix}_min_combined": 0.0,
            }
        root, minor = parsed
        tones = chord_tones(root, minor)
        third = quality_third(root, minor)
        combined_levels = {
            pitch_class: max(display_levels.get(pitch_class, 0.0), analysis_levels.get(pitch_class, 0.0))
            for pitch_class in tones
        }
        return {
            f"{prefix}_plain": "1",
            f"{prefix}_quality": "m" if minor else "maj",
            f"{prefix}_display_tones": float(len(tones & display)),
            f"{prefix}_analysis_tones": float(len(tones & analysis)),
            f"{prefix}_smooth_tones": float(len(tones & smoothed)),
            f"{prefix}_root_visible": display_levels.get(root, 0.0),
            f"{prefix}_root_analysis": analysis_levels.get(root, 0.0),
            f"{prefix}_root_smooth": smoothed_levels.get(root, 0.0),
            f"{prefix}_root_raw": raw_levels.get(root, 0.0),
            f"{prefix}_root_probe": probe_levels.get(root, 0.0),
            f"{prefix}_root_melodic": melodic_levels.get(root, 0.0),
            f"{prefix}_third_raw": raw_levels.get(third, 0.0),
            f"{prefix}_third_probe": probe_levels.get(third, 0.0),
            f"{prefix}_third_melodic": melodic_levels.get(third, 0.0),
            f"{prefix}_min_combined": min(combined_levels.values()) if combined_levels else 0.0,
        }

    root_interval = "none"
    if primary_parsed is not None and promoted_parsed is not None:
        root_interval = str((promoted_parsed[0] - primary_parsed[0]) % 12)

    features: dict[str, str | float] = {
        "candidate_slot": "1" if promoted_index == 1 else "2+",
        "candidate_index": float(promoted_index),
        "component_count": float(len(components)),
        "root_interval": root_interval,
        "gap": gap,
        "primary_score": primary_score,
        "candidate_score": promoted_score,
        "display_pitch_classes": float(len(display)),
        "analysis_pitch_classes": float(len(analysis)),
        "smooth_pitch_classes": float(len(smoothed)),
    }
    features.update(plain_features("primary", primary_parsed))
    features.update(plain_features("candidate", promoted_parsed))
    return features


def print_score_safe_rules(
    rescues: list[tuple[float, str, str, float, float, dict[str, str]]],
    protected_false: list[tuple[float, str, str, float, float, dict[str, str]]],
    neutral: list[tuple[float, str, str, float, float, dict[str, str]]],
    limit: int,
) -> None:
    rescue_features = [score_feature_row(*item) for item in rescues]
    protected_features = [score_feature_row(*item) for item in protected_false]
    neutral_features = [score_feature_row(*item) for item in neutral]
    category_fields = (
        "candidate_slot",
        "root_interval",
        "primary_plain",
        "primary_quality",
        "candidate_plain",
        "candidate_quality",
    )
    numeric_fields = (
        "candidate_index",
        "component_count",
        "gap",
        "primary_score",
        "candidate_score",
        "display_pitch_classes",
        "analysis_pitch_classes",
        "smooth_pitch_classes",
        "primary_display_tones",
        "primary_analysis_tones",
        "primary_smooth_tones",
        "primary_root_visible",
        "primary_root_analysis",
        "primary_root_smooth",
        "primary_root_raw",
        "primary_root_probe",
        "primary_root_melodic",
        "primary_third_raw",
        "primary_third_probe",
        "primary_third_melodic",
        "primary_min_combined",
        "candidate_display_tones",
        "candidate_analysis_tones",
        "candidate_smooth_tones",
        "candidate_root_visible",
        "candidate_root_analysis",
        "candidate_root_smooth",
        "candidate_root_raw",
        "candidate_root_probe",
        "candidate_root_melodic",
        "candidate_third_raw",
        "candidate_third_probe",
        "candidate_third_melodic",
        "candidate_min_combined",
    )
    patterns: list[tuple[str, Callable[[dict[str, str | float]], bool]]] = []
    for field in category_fields:
        for value in sorted({str(row[field]) for row in rescue_features}):
            patterns.append(
                (
                    f"{field}={value}",
                    lambda row, field=field, value=value: str(row[field]) == value,
                )
            )
    for field in numeric_fields:
        values = sorted({float(row[field]) for row in rescue_features})
        for value in values:
            text = format_feature_value(value)
            patterns.append(
                (
                    f"{field}>={text}",
                    lambda row, field=field, value=value: float(row[field]) >= value,
                )
            )
            patterns.append(
                (
                    f"{field}<={text}",
                    lambda row, field=field, value=value: float(row[field]) <= value,
                )
            )

    results: list[tuple[int, int, int, int, str]] = []
    for left_index, (left_label, left_predicate) in enumerate(patterns):
        candidates = [(left_label, left_predicate)]
        for right_label, right_predicate in patterns[left_index + 1 :]:
            candidates.append(
                (
                    f"{left_label} AND {right_label}",
                    lambda row, left=left_predicate, right=right_predicate: left(row) and right(row),
                )
            )
        for label, predicate in candidates:
            rescue_count = sum(1 for row in rescue_features if predicate(row))
            if rescue_count <= 0:
                continue
            protected_count = sum(1 for row in protected_features if predicate(row))
            if protected_count > 0:
                continue
            neutral_count = sum(1 for row in neutral_features if predicate(row))
            condition_count = label.count(" AND ") + 1
            results.append((-rescue_count, neutral_count, condition_count, len(label), label))

    print("score_promotion_safe_rules:")
    if not results:
        print("  --")
        return
    seen: set[str] = set()
    printed = 0
    for negative_rescues, neutral_count, _condition_count, _label_len, label in sorted(results):
        if label in seen:
            continue
        seen.add(label)
        print(f"  +{-negative_rescues} protected_false=0 neutral={neutral_count} :: {label}")
        printed += 1
        if printed >= limit:
            break


def cpp_style_promotion_candidate(
    row: dict[str, str],
) -> tuple[float, float, str, str, float, float] | None:
    components = split_components(row.get("guitar_chord", ""))
    if len(components) < 2:
        return None

    display = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    display_levels = parse_cells(row.get("guitar_cells", ""))
    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    primary = components[0]
    primary_plain = parse_plain(primary)
    primary_score = (
        component_score(primary, display, analysis, display_levels, analysis_levels)
        if primary_plain
        else -1.0
    )

    best: tuple[float, float, int, str] | None = None
    for index, label in enumerate(components[1:], start=1):
        parsed = parse_plain(label)
        if parsed is None:
            continue
        root, minor = parsed
        score = component_score(label, display, analysis, display_levels, analysis_levels)
        if score < 0.0:
            continue
        has_power = any(is_power_for_root(component, root) for component in components)
        if has_power:
            score += 0.72
        same_root_opposite = (
            primary_plain is not None
            and primary_plain[0] == root
            and primary_plain[1] != minor
        )
        different_root = primary_plain is None or primary_plain[0] != root
        required_margin = (
            0.20
            if primary_plain is None
            else 0.18
            if has_power and different_root
            else 0.04
            if same_root_opposite
            else 0.48
        )
        if score < primary_score + required_margin:
            continue
        if best is None or score > best[0] or (score == best[0] and index < best[2]):
            best = (score, required_margin, index, label)
    if best is None:
        return None

    candidate_score, required_margin, _index, promoted = best
    return candidate_score - primary_score, required_margin, promoted, primary, primary_score, candidate_score


def expected_labels(value: str) -> set[str]:
    return set(split_components(value))


def confidence_value(row: dict[str, str], field: str) -> str:
    value = row.get(field, "")
    return value if value else "--"


def extension_feature_row(
    promoted: str,
    row: dict[str, str],
) -> dict[str, str | float]:
    components = split_components(row.get("guitar_chord", ""))
    primary = components[0] if components else ""
    primary_plain = parse_plain(primary)
    primary_pitch_classes = chord_pitch_set(primary) or set()
    promoted_pitch_classes = chord_pitch_set(promoted) or set()
    extra_pitch_classes = promoted_pitch_classes - primary_pitch_classes
    candidate_index = next(
        (index for index, component in enumerate(components) if component == promoted),
        -1,
    )
    display_pitch_classes = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis_pitch_classes = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smoothed_pitch_classes = pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    display_levels = parse_cells(row.get("guitar_cells", ""))
    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    smoothed_levels = parse_cells(row.get("guitar_smoothed_cells", ""))
    probe_levels = parse_cells(row.get("guitar_probe_pitch_class_levels", ""))
    raw_levels = parse_cells(row.get("raw_pitch_class_levels", ""))
    suffix = chord_quality(promoted) or "maj"
    return {
        "suffix": suffix,
        "primary_family": "minor" if primary_plain and primary_plain[1] else "major",
        "candidate_slot": "1" if candidate_index == 1 else "2+",
        "candidate_index": float(candidate_index),
        "extra_tones": float(len(extra_pitch_classes)),
        "extra_visible_hits": float(len(extra_pitch_classes & display_pitch_classes)),
        "extra_analysis_hits": float(len(extra_pitch_classes & analysis_pitch_classes)),
        "extra_smoothed_hits": float(len(extra_pitch_classes & smoothed_pitch_classes)),
        "extra_visible_min": cell_level_min(display_levels, extra_pitch_classes),
        "extra_analysis_min": cell_level_min(analysis_levels, extra_pitch_classes),
        "extra_smoothed_min": cell_level_min(smoothed_levels, extra_pitch_classes),
        "extra_probe_min": cell_level_min(probe_levels, extra_pitch_classes),
        "extra_raw_min": cell_level_min(raw_levels, extra_pitch_classes),
    }


def current_extension_feature_row(
    current_primary: str,
    plain_fallback: str,
    row: dict[str, str],
) -> dict[str, str | float]:
    components = split_components(row.get("guitar_chord", ""))
    plain_pitch_classes = chord_pitch_set(plain_fallback) or set()
    current_pitch_classes = chord_pitch_set(current_primary) or set()
    extra_pitch_classes = current_pitch_classes - plain_pitch_classes
    plain_index = next(
        (index for index, component in enumerate(components) if component == plain_fallback),
        -1,
    )
    display_pitch_classes = pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis_pitch_classes = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smoothed_pitch_classes = pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    display_levels = parse_cells(row.get("guitar_cells", ""))
    analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
    smoothed_levels = parse_cells(row.get("guitar_smoothed_cells", ""))
    probe_levels = parse_cells(row.get("guitar_probe_pitch_class_levels", ""))
    raw_levels = parse_cells(row.get("raw_pitch_class_levels", ""))
    suffix = chord_quality(current_primary) or "maj"
    return {
        "suffix": suffix,
        "plain_slot": "1" if plain_index == 1 else "2+",
        "plain_index": float(plain_index),
        "extra_tones": float(len(extra_pitch_classes)),
        "extra_visible_hits": float(len(extra_pitch_classes & display_pitch_classes)),
        "extra_analysis_hits": float(len(extra_pitch_classes & analysis_pitch_classes)),
        "extra_smoothed_hits": float(len(extra_pitch_classes & smoothed_pitch_classes)),
        "extra_visible_min": cell_level_min(display_levels, extra_pitch_classes),
        "extra_analysis_min": cell_level_min(analysis_levels, extra_pitch_classes),
        "extra_smoothed_min": cell_level_min(smoothed_levels, extra_pitch_classes),
        "extra_probe_min": cell_level_min(probe_levels, extra_pitch_classes),
        "extra_raw_min": cell_level_min(raw_levels, extra_pitch_classes),
    }


def compact_feature_summary(features: dict[str, str | float]) -> str:
    fields = (
        "suffix",
        "plain_slot",
        "extra_visible_min",
        "extra_analysis_min",
        "extra_smoothed_min",
        "extra_probe_min",
        "extra_raw_min",
    )
    return ",".join(f"{field}={format_feature_value(features[field])}" for field in fields)


def format_feature_value(value: float) -> str:
    if isinstance(value, str):
        return value
    if abs(value - round(value)) < 1.0e-6:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def extension_feature_patterns(
    feature_rows: list[dict[str, str | float]],
    numeric_fields: tuple[str, ...] | None = None,
) -> list[tuple[str, Callable[[dict[str, str | float]], bool]]]:
    if not feature_rows:
        return []
    patterns: list[tuple[str, Callable[[dict[str, str | float]], bool]]] = []
    category_fields = ("suffix", "primary_family", "candidate_slot")
    if numeric_fields is None:
        numeric_fields = (
            "candidate_index",
            "extra_tones",
            "extra_visible_hits",
            "extra_analysis_hits",
            "extra_smoothed_hits",
            "extra_visible_min",
            "extra_analysis_min",
            "extra_smoothed_min",
            "extra_probe_min",
            "extra_raw_min",
        )
    for field in category_fields:
        for value in sorted({str(row[field]) for row in feature_rows}):
            patterns.append(
                (
                    f"{field}={value}",
                    lambda row, field=field, value=value: str(row[field]) == value,
                )
            )
    for field in numeric_fields:
        values = sorted({float(row[field]) for row in feature_rows})
        for value in values:
            text = format_feature_value(value)
            patterns.append(
                (
                    f"{field}>={text}",
                    lambda row, field=field, value=value: float(row[field]) >= value,
                )
            )
            patterns.append(
                (
                    f"{field}<={text}",
                    lambda row, field=field, value=value: float(row[field]) <= value,
                )
            )
    deduped: list[tuple[str, callable]] = []
    seen: set[str] = set()
    for label, predicate in patterns:
        if label in seen:
            continue
        seen.add(label)
        deduped.append((label, predicate))
    return deduped


def print_extension_safe_rules(
    title: str,
    rescues: list[tuple[str, dict[str, str]]],
    protected_false: list[tuple[str, dict[str, str]]],
    neutral: list[tuple[str, dict[str, str]]],
    limit: int,
    numeric_fields: tuple[str, ...] | None = None,
) -> None:
    rescue_features = [extension_feature_row(promoted, row) for promoted, row in rescues]
    protected_features = [extension_feature_row(promoted, row) for promoted, row in protected_false]
    neutral_features = [extension_feature_row(promoted, row) for promoted, row in neutral]
    patterns = extension_feature_patterns(rescue_features, numeric_fields)
    results: list[tuple[int, int, int, int, str]] = []
    for left_index, (left_label, left_predicate) in enumerate(patterns):
        candidates = [(left_label, left_predicate)]
        for right_label, right_predicate in patterns[left_index + 1 :]:
            candidates.append(
                (
                    f"{left_label} AND {right_label}",
                    lambda row, left=left_predicate, right=right_predicate: left(row) and right(row),
                )
            )
        for label, predicate in candidates:
            rescue_count = sum(1 for row in rescue_features if predicate(row))
            if rescue_count <= 0:
                continue
            protected_count = sum(1 for row in protected_features if predicate(row))
            if protected_count > 0:
                continue
            neutral_count = sum(1 for row in neutral_features if predicate(row))
            condition_count = label.count(" AND ") + 1
            results.append((-rescue_count, neutral_count, condition_count, len(label), label))
    print(title)
    if not results:
        print("  --")
        return
    seen: set[str] = set()
    printed = 0
    for negative_rescues, neutral_count, _condition_count, _label_len, label in sorted(results):
        if label in seen:
            continue
        seen.add(label)
        print(f"  +{-negative_rescues} protected_false=0 neutral={neutral_count} :: {label}")
        printed += 1
        if printed >= limit:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--examples", type=int, default=12)
    args = parser.parse_args()

    with args.path.open(newline="", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    chord_rows = [row for row in rows if row.get("expected_chords", "--") not in ("", "--")]
    for field in ("guitar_chord", "guitar_raw_chord", "guitar_smoothed_chord"):
        primary_hits = 0
        later_hits = 0
        misses = 0
        for row in chord_rows:
            expected = expected_labels(row.get("expected_chords", ""))
            components = split_components(row.get(field, ""))
            if components and components[0] in expected:
                primary_hits += 1
            elif expected & set(components):
                later_hits += 1
            else:
                misses += 1
        print(
            f"{field}:",
            f"primary={primary_hits}/{len(chord_rows)}",
            f"later={later_hits}",
            f"miss={misses}",
        )

    relationship_buckets: collections.Counter[str] = collections.Counter()
    raw_rescues = []
    smoothed_rescues = []
    both_rescues = []
    raw_only_primary = []
    smoothed_only_primary = []
    extension_primary_candidates = []
    extension_primary_rescues = []
    extension_primary_protected_false = []
    extension_primary_neutral = []
    current_extension_primary_candidates = []
    current_extension_primary_rescues = []
    current_extension_primary_protected_false = []
    current_extension_primary_neutral = []
    same_root_quality_raw_promotions = []
    same_root_quality_raw_rescues = []
    same_root_quality_raw_protected_false = []
    same_root_quality_display_promotions = []
    same_root_quality_display_rescues = []
    same_root_quality_display_protected_false = []
    analysis_full_anchor_promotions = []
    analysis_full_anchor_rescues = []
    analysis_full_anchor_protected_false = []
    analysis_full_anchor_neutral = []
    score_promotion_candidates = []
    score_promotion_rescues = []
    score_promotion_protected_false = []
    score_promotion_neutral = []
    cpp_style_promotion_candidates = []
    cpp_style_promotion_rescues = []
    cpp_style_promotion_protected_false = []
    cpp_style_promotion_neutral = []
    for row in chord_rows:
        expected = expected_labels(row.get("expected_chords", ""))
        displayed_primary = primary_component(row.get("guitar_chord", ""))
        raw_primary = primary_component(row.get("guitar_raw_chord", ""))
        smoothed_primary = primary_component(row.get("guitar_smoothed_chord", ""))
        displayed_hit = displayed_primary in expected
        raw_hit = raw_primary in expected
        smoothed_hit = smoothed_primary in expected
        relationship_buckets[
            f"display{int(displayed_hit)}_raw{int(raw_hit)}_smooth{int(smoothed_hit)}"
        ] += 1
        if not displayed_hit and raw_hit:
            raw_rescues.append(row)
        if not displayed_hit and smoothed_hit:
            smoothed_rescues.append(row)
        if not displayed_hit and raw_hit and smoothed_hit:
            both_rescues.append(row)
        if raw_hit and not smoothed_hit:
            raw_only_primary.append(row)
        if smoothed_hit and not raw_hit:
            smoothed_only_primary.append(row)
        displayed_components = split_components(row.get("guitar_chord", ""))
        extension_candidate = same_root_extension_primary_candidate(displayed_components)
        if extension_candidate:
            extension_primary_candidates.append((extension_candidate, row))
            if not displayed_hit and extension_candidate in expected:
                extension_primary_rescues.append((extension_candidate, row))
            elif displayed_hit and extension_candidate not in expected:
                extension_primary_protected_false.append((extension_candidate, row))
            else:
                extension_primary_neutral.append((extension_candidate, row))
        current_extension = current_same_root_extension_primary(displayed_components)
        if current_extension:
            current_extension_primary_candidates.append((*current_extension, row))
            current_primary, plain_fallback = current_extension
            if current_primary in expected:
                current_extension_primary_rescues.append((*current_extension, row))
            elif plain_fallback in expected:
                current_extension_primary_protected_false.append((*current_extension, row))
            else:
                current_extension_primary_neutral.append((*current_extension, row))
        same_root_quality_raw = promoted_same_root_smoothed_quality(
            row, "raw_pitch_class_levels", 0.012, 1.35, 0.004
        )
        if same_root_quality_raw:
            same_root_quality_raw_promotions.append((same_root_quality_raw, row))
            if not displayed_hit and same_root_quality_raw in expected:
                same_root_quality_raw_rescues.append((same_root_quality_raw, row))
            if displayed_hit and same_root_quality_raw not in expected:
                same_root_quality_raw_protected_false.append((same_root_quality_raw, row))

        same_root_quality_display = promoted_same_root_smoothed_quality(
            row, "guitar_probe_pitch_class_levels", 0.012, 1.15, 0.002
        )
        if same_root_quality_display:
            same_root_quality_display_promotions.append((same_root_quality_display, row))
            if not displayed_hit and same_root_quality_display in expected:
                same_root_quality_display_rescues.append((same_root_quality_display, row))
            if displayed_hit and same_root_quality_display not in expected:
                same_root_quality_display_protected_false.append((same_root_quality_display, row))

        for promoted in analysis_full_anchor_plain_promotions(row):
            analysis_full_anchor_promotions.append((promoted, row))
            if not displayed_hit and promoted in expected:
                analysis_full_anchor_rescues.append((promoted, row))
            elif displayed_hit and promoted not in expected:
                analysis_full_anchor_protected_false.append((promoted, row))
            else:
                analysis_full_anchor_neutral.append((promoted, row))

        score_candidate = score_promotion_candidate(row)
        if score_candidate:
            gap, promoted, primary, primary_score, promoted_score = score_candidate
            scored_row = (gap, promoted, primary, primary_score, promoted_score, row)
            score_promotion_candidates.append(scored_row)
            if not displayed_hit and promoted in expected:
                score_promotion_rescues.append(scored_row)
            elif displayed_hit and promoted not in expected:
                score_promotion_protected_false.append(scored_row)
            else:
                score_promotion_neutral.append(scored_row)

        cpp_candidate = cpp_style_promotion_candidate(row)
        if cpp_candidate:
            gap, margin, promoted, primary, primary_score, promoted_score = cpp_candidate
            scored_row = (gap, margin, promoted, primary, primary_score, promoted_score, row)
            cpp_style_promotion_candidates.append(scored_row)
            if not displayed_hit and promoted in expected:
                cpp_style_promotion_rescues.append(scored_row)
            elif displayed_hit and promoted not in expected:
                cpp_style_promotion_protected_false.append(scored_row)
            else:
                cpp_style_promotion_neutral.append(scored_row)

    if relationship_buckets:
        print(
            "candidate primary relationships:",
            " ".join(
                f"{key}={relationship_buckets[key]}" for key in sorted(relationship_buckets)
            ),
        )
        print(
            "candidate primary rescues:",
            f"raw={len(raw_rescues)}",
            f"smoothed={len(smoothed_rescues)}",
            f"both={len(both_rescues)}",
        )

        def print_rescue_examples(title: str, rescue_rows: list[dict[str, str]]) -> None:
            if not rescue_rows:
                return
            print(title)
            for row in rescue_rows[: args.examples]:
                display = pitch_classes(row.get("guitar_pitch_classes", ""))
                analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
                display_levels = parse_cells(row.get("guitar_cells", ""))
                analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
                raw_primary = primary_component(row.get("guitar_raw_chord", ""))
                smoothed_primary = primary_component(row.get("guitar_smoothed_chord", ""))
                print(
                    f"  expected={row.get('expected_chords')}",
                    f"display={primary_component(row.get('guitar_chord', ''))}",
                    f"raw={raw_primary}",
                    f"smoothed={smoothed_primary}",
                    "score="
                    f"r:{component_score(raw_primary, display, analysis, display_levels, analysis_levels):.3f}/"
                    f"s:{component_score(smoothed_primary, display, analysis, display_levels, analysis_levels):.3f}",
                    "conf="
                    f"d:{confidence_value(row, 'guitar_chord_confidence')}/"
                    f"r:{confidence_value(row, 'guitar_raw_chord_confidence')}/"
                    f"s:{confidence_value(row, 'guitar_smoothed_chord_confidence')}",
                    pathlib.Path(row.get("audio_path", "")).name,
                )

        print_rescue_examples("raw primary rescue examples", raw_rescues)
        print_rescue_examples("smoothed primary rescue examples", smoothed_rescues)
        print_rescue_examples("raw-only primary examples", raw_only_primary)
        print_rescue_examples("smoothed-only primary examples", smoothed_only_primary)

    print(
        "same_root_extension_primary_probe:",
        f"candidates={len(extension_primary_candidates)}",
        f"rescues={len(extension_primary_rescues)}",
        f"protected_false={len(extension_primary_protected_false)}",
        f"neutral={len(extension_primary_neutral)}",
    )
    for promoted, row in extension_primary_rescues[: args.examples]:
        print(
            f"  rescue promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary_component(row.get('guitar_chord', ''))}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    for promoted, row in extension_primary_protected_false[: args.examples]:
        print(
            f"  protected_false promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary_component(row.get('guitar_chord', ''))}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    print_extension_safe_rules(
        "same_root_extension_primary_safe_rules:",
        extension_primary_rescues,
        extension_primary_protected_false,
        extension_primary_neutral,
        args.examples,
    )
    print_extension_safe_rules(
        "same_root_extension_primary_runtime_safe_rules:",
        extension_primary_rescues,
        extension_primary_protected_false,
        extension_primary_neutral,
        args.examples,
        (
            "candidate_index",
            "extra_tones",
            "extra_visible_hits",
            "extra_analysis_hits",
            "extra_smoothed_hits",
            "extra_visible_min",
            "extra_analysis_min",
            "extra_smoothed_min",
            "extra_probe_min",
        ),
    )
    print(
        "current_same_root_extension_primary:",
        f"candidates={len(current_extension_primary_candidates)}",
        f"expected_primary={len(current_extension_primary_rescues)}",
        f"protected_plain_false={len(current_extension_primary_protected_false)}",
        f"neutral={len(current_extension_primary_neutral)}",
    )
    for current_primary, plain_fallback, row in current_extension_primary_rescues[: args.examples]:
        print(
            f"  expected_primary current={current_primary}",
            f"plain={plain_fallback}",
            f"expected={row.get('expected_chords')}",
            f"features={compact_feature_summary(current_extension_feature_row(current_primary, plain_fallback, row))}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    for current_primary, plain_fallback, row in current_extension_primary_protected_false[: args.examples]:
        print(
            f"  protected_plain_false current={current_primary}",
            f"plain={plain_fallback}",
            f"expected={row.get('expected_chords')}",
            f"features={compact_feature_summary(current_extension_feature_row(current_primary, plain_fallback, row))}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )

    def print_same_root_quality(
        title: str,
        promotions: list[tuple[str, dict[str, str]]],
        rescues: list[tuple[str, dict[str, str]]],
        protected_false: list[tuple[str, dict[str, str]]],
    ) -> None:
        print(
            f"{title}:",
            f"candidates={len(promotions)}",
            f"rescues={len(rescues)}",
            f"protected_false={len(protected_false)}",
        )
        for promoted, row in rescues[: args.examples]:
            print(
                f"  rescue promote={promoted}",
                f"expected={row.get('expected_chords')}",
                f"display={primary_component(row.get('guitar_chord', ''))}",
                f"raw={primary_component(row.get('guitar_raw_chord', ''))}",
                f"smoothed={primary_component(row.get('guitar_smoothed_chord', ''))}",
                pathlib.Path(row.get("audio_path", "")).name,
            )
        for promoted, row in protected_false[: args.examples]:
            print(
                f"  protected_false promote={promoted}",
                f"expected={row.get('expected_chords')}",
                f"display={primary_component(row.get('guitar_chord', ''))}",
                f"raw={primary_component(row.get('guitar_raw_chord', ''))}",
                f"smoothed={primary_component(row.get('guitar_smoothed_chord', ''))}",
                pathlib.Path(row.get("audio_path", "")).name,
            )

    print_same_root_quality(
        "same_root_quality_raw_probe_promote",
        same_root_quality_raw_promotions,
        same_root_quality_raw_rescues,
        same_root_quality_raw_protected_false,
    )
    print_same_root_quality(
        "same_root_quality_display_probe_promote",
        same_root_quality_display_promotions,
        same_root_quality_display_rescues,
        same_root_quality_display_protected_false,
    )

    print(
        "analysis_full_anchor_plain_promote:",
        f"candidates={len(analysis_full_anchor_promotions)}",
        f"rescues={len(analysis_full_anchor_rescues)}",
        f"protected_false={len(analysis_full_anchor_protected_false)}",
        f"neutral={len(analysis_full_anchor_neutral)}",
    )
    for promoted, row in analysis_full_anchor_rescues[: args.examples]:
        print(
            f"  rescue promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"display={primary_component(row.get('guitar_chord', ''))}",
            f"raw={primary_component(row.get('guitar_raw_chord', ''))}",
            f"smoothed={primary_component(row.get('guitar_smoothed_chord', ''))}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    for promoted, row in analysis_full_anchor_protected_false[: args.examples]:
        print(
            f"  protected_false promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"display={primary_component(row.get('guitar_chord', ''))}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )

    print(
        "score_promotion_probe:",
        f"candidates={len(score_promotion_candidates)}",
        f"rescues={len(score_promotion_rescues)}",
        f"protected_false={len(score_promotion_protected_false)}",
        f"neutral={len(score_promotion_neutral)}",
    )
    for gap, promoted, primary, primary_score, promoted_score, row in sorted(
        score_promotion_rescues, key=lambda item: item[0], reverse=True
    )[: args.examples]:
        print(
            f"  rescue promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"gap={gap:.3f}",
            f"score=p:{primary_score:.3f}/c:{promoted_score:.3f}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    for gap, promoted, primary, primary_score, promoted_score, row in sorted(
        score_promotion_protected_false, key=lambda item: item[0], reverse=True
    )[: args.examples]:
        print(
            f"  protected_false promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"gap={gap:.3f}",
            f"score=p:{primary_score:.3f}/c:{promoted_score:.3f}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    print_score_safe_rules(
        score_promotion_rescues,
        score_promotion_protected_false,
        score_promotion_neutral,
        args.examples,
    )

    print(
        "cpp_style_promotion_probe:",
        f"candidates={len(cpp_style_promotion_candidates)}",
        f"rescues={len(cpp_style_promotion_rescues)}",
        f"protected_false={len(cpp_style_promotion_protected_false)}",
        f"neutral={len(cpp_style_promotion_neutral)}",
    )
    for gap, margin, promoted, primary, primary_score, promoted_score, row in sorted(
        cpp_style_promotion_rescues, key=lambda item: item[0], reverse=True
    )[: args.examples]:
        print(
            f"  rescue promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"gap={gap:.3f}",
            f"margin={margin:.3f}",
            f"score=p:{primary_score:.3f}/c:{promoted_score:.3f}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    for gap, margin, promoted, primary, primary_score, promoted_score, row in sorted(
        cpp_style_promotion_protected_false, key=lambda item: item[0], reverse=True
    )[: args.examples]:
        print(
            f"  protected_false promote={promoted}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"gap={gap:.3f}",
            f"margin={margin:.3f}",
            f"score=p:{primary_score:.3f}/c:{promoted_score:.3f}",
            f"label={row.get('guitar_chord', '--')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )

    primary_misses = []
    expected_later = []
    score_gaps: list[float] = []
    likely_promotable = []
    cpp_promotable = []
    miss_quality_buckets: collections.Counter[str] = collections.Counter()
    miss_evidence_buckets: collections.Counter[str] = collections.Counter()
    miss_tone_buckets: collections.Counter[str] = collections.Counter()
    miss_root_buckets: collections.Counter[str] = collections.Counter()

    for row in chord_rows:
        expected = expected_labels(row.get("expected_chords", ""))
        components = split_components(row.get("guitar_chord", ""))
        primary = components[0] if components else "--"
        if not components or primary in expected:
            continue
        primary_misses.append(row)
        expected_quality = compact_value(
            row.get("expected_quality_compact")
            or row.get("quality")
            or row.get("expected_chord_qualities")
        )
        miss_quality_buckets[
            "expected="
            + expected_quality
            + " primary="
            + primary_quality_bucket(primary)
            + " root="
            + root_relation(expected, primary)
        ] += 1
        miss_evidence_buckets[
            "match="
            + compact_value(row.get("guitar_match_kind"))
            + " evidence="
            + compact_value(row.get("evidence_class"))
            + "/"
            + compact_value(row.get("evidence_source"))
        ] += 1
        miss_tone_buckets[
            "visible="
            + compact_value(row.get("visible_missing_tones"))
            + " analysis="
            + compact_value(row.get("analysis_missing_tones"))
            + " smooth="
            + compact_value(row.get("smooth_missing_tones"))
        ] += 1
        miss_root_buckets[
            "rootvis="
            + compact_value(row.get("expected_root_in_display"))
            + " display="
            + compact_value(row.get("expected_label_in_display"))
            + " raw="
            + compact_value(row.get("expected_label_in_raw"))
            + " smooth="
            + compact_value(row.get("expected_label_in_smooth"))
        ] += 1
        if not expected & set(components):
            continue
        expected_later.append(row)

        display = pitch_classes(row.get("guitar_pitch_classes", ""))
        analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
        display_levels = parse_cells(row.get("guitar_cells", ""))
        analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
        primary_score = component_score(
            components[0], display, analysis, display_levels, analysis_levels
        )
        best_expected_score = max(
            component_score(label, display, analysis, display_levels, analysis_levels)
            for label in expected
        )
        score_gaps.append(best_expected_score - primary_score)
        if best_expected_score >= primary_score + 0.02:
            likely_promotable.append((best_expected_score - primary_score, row, components[0]))

        primary_plain = parse_plain(components[0])
        for label in sorted(expected & set(components)):
            parsed = parse_plain(label)
            if parsed is None:
                continue
            root, minor = parsed
            score = component_score(label, display, analysis, display_levels, analysis_levels)
            if score < 0.0:
                continue
            if any(is_power_for_root(component, root) for component in components):
                score += 0.72
            same_root_opposite = (
                primary_plain is not None
                and primary_plain[0] == root
                and primary_plain[1] != minor
            )
            different_root = primary_plain is None or primary_plain[0] != root
            has_power = any(is_power_for_root(component, root) for component in components)
            required_margin = (
                0.20
                if primary_plain is None
                else 0.18
                if has_power and different_root
                else 0.04
                if same_root_opposite
                else 0.48
            )
            if score >= primary_score + required_margin:
                cpp_promotable.append((score - primary_score, required_margin, row, components[0], label))
                break

    print(
        "guitar_primary_order:",
        f"rows={len(chord_rows)}",
        f"primary_misses={len(primary_misses)}",
        f"expected_later={len(expected_later)}",
        f"score_promotable={len(likely_promotable)}",
        f"cpp_promotable={len(cpp_promotable)}",
    )
    print_counter("primary_miss_quality_buckets:", miss_quality_buckets, args.examples)
    print_counter("primary_miss_evidence_buckets:", miss_evidence_buckets, args.examples)
    print_counter("primary_miss_tone_buckets:", miss_tone_buckets, args.examples)
    print_counter("primary_miss_root_buckets:", miss_root_buckets, args.examples)
    if score_gaps:
        buckets = collections.Counter()
        for gap in score_gaps:
            if gap >= 0.48:
                buckets[">=0.48"] += 1
            elif gap >= 0.18:
                buckets[">=0.18"] += 1
            elif gap >= 0.04:
                buckets[">=0.04"] += 1
            elif gap >= 0.0:
                buckets[">=0"] += 1
            else:
                buckets["<0"] += 1
        print("score_gap_buckets:", " ".join(f"{key}={value}" for key, value in buckets.items()))

    for gap, row, primary in sorted(
        likely_promotable, key=lambda item: item[0], reverse=True
    )[: args.examples]:
        print(
            f"  gap={gap:.3f}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"label={row.get('guitar_chord')}",
            f"pc={row.get('guitar_pitch_classes')}",
            f"analysis={row.get('guitar_analysis_pitch_classes')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    if cpp_promotable:
        print("cpp-style promotable expected-later rows")
        for gap, margin, row, primary, label in sorted(
            cpp_promotable, key=lambda item: item[0], reverse=True
        )[: args.examples]:
            print(
                f"  gap={gap:.3f}",
                f"margin={margin:.3f}",
                f"promote={label}",
                f"expected={row.get('expected_chords')}",
                f"primary={primary}",
                f"label={row.get('guitar_chord')}",
                pathlib.Path(row.get("audio_path", "")).name,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
