#!/usr/bin/env python3
"""Print feature ranges for selected GuitarSet chord attribute buckets."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics

from summarize_guitarset_attributes import (
    NOTE_TO_PC,
    as_float,
    as_int,
    chord_quality,
    chord_root,
    chord_tones,
    load_rows,
    parse_cell_levels,
    parse_pitch_classes,
)


NUMERIC_FIELDS = [
    "expected_note_count",
    "expected_pitch_class_count",
    "expected_chord_tone_count",
    "guitar_note_hits",
    "guitar_false_positive_pitch_classes",
    "cross_row_expected_hits",
    "expected_raw_peak",
    "rms",
    "low",
    "mid",
    "high",
    "guitar_pc_count",
    "analysis_pc_count",
    "smooth_pc_count",
    "visible_tones",
    "analysis_tones",
    "smooth_tones",
    "root_visible",
    "visible_root",
    "visible_third",
    "visible_fifth",
    "analysis_root",
    "analysis_third",
    "analysis_fifth",
    "smooth_root",
    "smooth_third",
    "smooth_fifth",
    "raw_root",
    "raw_third",
    "raw_fifth",
    "raw_opposite_third",
    "raw_third_anchor_ratio",
    "raw_third_opposite_margin",
    "probe_root",
    "probe_third",
    "probe_fifth",
    "probe_opposite_third",
    "probe_third_anchor_ratio",
    "probe_third_opposite_margin",
    "melodic_probe_root",
    "melodic_probe_third",
    "melodic_probe_fifth",
    "melodic_probe_opposite_third",
    "melodic_probe_third_anchor_ratio",
    "melodic_probe_third_opposite_margin",
    "guitar_chord_confidence",
    "guitar_raw_chord_confidence",
    "guitar_smoothed_chord_confidence",
    "chord_hit",
    "simple_chord_hit",
    "guitar_chord_hit",
    "expected_label_in_display",
    "expected_label_in_raw",
    "expected_label_in_smooth",
    "expected_root_in_display",
]

CATEGORY_FIELDS = [
    "expected_chords",
    "expected_chord_qualities",
    "expected_label",
    "expected_root",
    "expected_quality_compact",
    "guitar_chord",
    "guitar_raw_chord",
    "guitar_smoothed_chord",
    "global_chord",
    "guitar_match_kind",
    "expected_pitch_classes",
    "guitar_pitch_classes",
    "guitar_analysis_pitch_classes",
    "guitar_smoothed_pitch_classes",
    "visible_missing_tones",
    "analysis_missing_tones",
    "smooth_missing_tones",
    "support",
    "evidence_class",
    "evidence_source",
    "quality_raw",
]

ROW_DUMP_FIELDS = [
    "recording_id",
    "status",
    "expected_chords",
    "expected_chord_qualities",
    "quality",
    "expected_label",
    "expected_root",
    "expected_quality_compact",
    "guitar_match_kind",
    "chord_hit",
    "simple_chord_hit",
    "guitar_chord_hit",
    "expected_label_in_display",
    "expected_label_in_raw",
    "expected_label_in_smooth",
    "expected_root_in_display",
    "guitar_chord",
    "guitar_raw_chord",
    "guitar_smoothed_chord",
    "guitar_chord_confidence",
    "guitar_raw_chord_confidence",
    "guitar_smoothed_chord_confidence",
    "global_chord",
    "support",
    "expected_pitch_classes",
    "guitar_pitch_classes",
    "guitar_cells",
    "guitar_analysis_pitch_classes",
    "guitar_analysis_cells",
    "guitar_smoothed_pitch_classes",
    "guitar_smoothed_cells",
    "visible_missing_tones",
    "analysis_missing_tones",
    "smooth_missing_tones",
    "evidence_class",
    "evidence_source",
    "visible_root",
    "visible_third",
    "visible_fifth",
    "analysis_root",
    "analysis_third",
    "analysis_fifth",
    "smooth_root",
    "smooth_third",
    "smooth_fifth",
    "raw_root",
    "raw_third",
    "raw_fifth",
    "raw_opposite_third",
    "raw_third_anchor_ratio",
    "raw_third_opposite_margin",
    "probe_root",
    "probe_third",
    "probe_fifth",
    "probe_opposite_third",
    "probe_third_anchor_ratio",
    "probe_third_opposite_margin",
    "melodic_probe_root",
    "melodic_probe_third",
    "melodic_probe_fifth",
    "melodic_probe_opposite_third",
    "melodic_probe_third_anchor_ratio",
    "melodic_probe_third_opposite_margin",
    "quality_raw",
    "raw_pitch_class_levels",
    "guitar_probe_pitch_class_levels",
    "guitar_melodic_probe_pitch_class_levels",
    "guitar_note_hits",
    "guitar_false_positive_pitch_classes",
    "cross_row_expected_hits",
    "rms",
    "low",
    "mid",
    "high",
    "audio_path",
]

BUCKET_RE = re.compile(r"([^:]+):([^:]+):(.+)")


def normalized_quality(row: dict[str, str], expected_label: str) -> str:
    quality = row.get("expected_chord_qualities", "")
    if quality and quality != "--":
        if quality in {"min", "minor"}:
            return "m"
        if quality in {"major"}:
            return "maj"
        return quality
    if expected_label.endswith("m"):
        return "m"
    return "maj" if expected_label else "--"


def split_chord_labels(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [label for label in re.split(r"[=/]", value) if label and label != "--"]


def compact_quality(label: str) -> str:
    quality = chord_quality(label)
    return "maj" if quality == "" and label else quality or "--"


def label_pitch_classes(label: str) -> set[int]:
    return {pitch_class for _name, pitch_class in chord_tones(label)}


def best_expected_label(expected_chords: str, analysis_pitch_classes: str) -> str:
    labels = split_chord_labels(expected_chords)
    if not labels:
        return ""
    analysis = parse_pitch_classes(analysis_pitch_classes)
    best_label = labels[0]
    best_score = -1.0
    for label in labels:
        expected = label_pitch_classes(label)
        if not expected:
            continue
        score = len(expected & analysis) / len(expected)
        if score > best_score:
            best_score = score
            best_label = label
    return best_label


def expected_root_name(label: str) -> str:
    root = chord_root(label)
    return root if root in NOTE_TO_PC else "--"


def same_root_labels(labels: list[str], root: str) -> list[str]:
    if root == "--":
        return []
    return [label for label in labels if chord_root(label) == root]


def guitar_match_kind(
    expected_labels: list[str],
    expected_label: str,
    displayed_value: str,
    raw_value: str,
    smooth_value: str,
) -> str:
    displayed = split_chord_labels(displayed_value)
    raw = split_chord_labels(raw_value)
    smooth = split_chord_labels(smooth_value)
    expected = set(expected_labels or ([expected_label] if expected_label else []))
    if expected and any(label in displayed for label in expected):
        return "display_exact"
    if expected and any(label in raw for label in expected):
        return "raw_exact"
    if expected and any(label in smooth for label in expected):
        return "smooth_exact"
    root = expected_root_name(expected_label)
    same_root = same_root_labels(displayed, root)
    if any(chord_quality(label) == "pow" for label in same_root):
        return "display_same_root_power"
    if same_root:
        return "display_same_root_other"
    if displayed:
        return "display_different_root"
    return "no_display_label"


def label_cell_contains(value: str, labels: list[str]) -> int:
    detected = set(split_chord_labels(value))
    return int(any(label in detected for label in labels))


def root_cell_contains(value: str, root: str) -> int:
    if root == "--":
        return 0
    return int(any(chord_root(label) == root for label in split_chord_labels(value)))


def opposite_third_pitch_class(expected_label: str) -> int | None:
    root = expected_root_name(expected_label)
    if root not in NOTE_TO_PC:
        return None
    quality = chord_quality(expected_label)
    if quality in {"", "7", "maj7", "6", "add9", "9", "maj9", "aug"}:
        return (NOTE_TO_PC[root] + 3) % 12
    if quality in {"m", "m7", "m6", "m9", "dim", "dim7", "m7b5"}:
        return (NOTE_TO_PC[root] + 4) % 12
    return None


def tone_key(name: str) -> str:
    if name in {"major_third", "minor_third"}:
        return "third"
    return name


def compact_missing(missing: list[str]) -> str:
    return ",".join(sorted(set(missing))) or "--"


def max_level(levels: dict[int, float], pitch_classes: list[int]) -> float:
    value = 0.0
    for pitch_class in pitch_classes:
        value = max(value, levels.get(pitch_class, 0.0))
    return value


def tone_present(tone_classes: dict[str, list[int]], pitch_classes: set[int], key: str) -> bool:
    return any(pitch_class in pitch_classes for pitch_class in tone_classes.get(key, []))


def strong_third_evidence(source_values: list[tuple[str, float, float]]) -> tuple[str, str]:
    thresholds = {
        "raw": (0.030, 0.020),
        "probe": (0.100, 0.030),
        "melodic": (0.120, 0.040),
    }
    for source, anchor_ratio, margin in source_values:
        min_ratio, min_margin = thresholds[source]
        if anchor_ratio >= min_ratio and margin >= min_margin:
            if source == "raw":
                return "raw_quality_gap", source
            if source == "melodic":
                return "melodic_probe_quality_gap", source
            return "direct_probe_quality_gap", source
    return "", ""


def derive_row(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    expected_labels = split_chord_labels(row.get("expected_chords", ""))
    expected_label = best_expected_label(
        row.get("expected_chords", ""), row.get("guitar_analysis_pitch_classes", "")
    )
    if not expected_label and row.get("status") == "single_note_false_chord":
        detected_labels = split_chord_labels(row.get("guitar_chord", ""))
        if detected_labels:
            expected_label = detected_labels[0]
    quality = normalized_quality(row, expected_label)
    tone_classes: dict[str, list[int]] = collections.defaultdict(list)
    for name, pitch_class in chord_tones(expected_label):
        tone_classes[tone_key(name)].append(pitch_class)

    visible = parse_pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = parse_pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smooth = parse_pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    visible_levels = parse_cell_levels(row.get("guitar_cells", ""))
    analysis_levels = parse_cell_levels(row.get("guitar_analysis_cells", ""))
    smooth_levels = parse_cell_levels(row.get("guitar_smoothed_cells", ""))
    raw_levels = parse_cell_levels(row.get("raw_pitch_class_levels", ""))
    if not raw_levels:
        raw_levels = parse_cell_levels(row.get("expected_raw_cells", ""))
    probe_levels = parse_cell_levels(row.get("guitar_probe_pitch_class_levels", ""))
    melodic_probe_levels = parse_cell_levels(row.get("guitar_melodic_probe_pitch_class_levels", ""))

    expected_pitch_classes = set()
    for pitch_classes in tone_classes.values():
        expected_pitch_classes.update(pitch_classes)

    def support_count(pitch_classes: set[int]) -> int:
        return len(expected_pitch_classes & pitch_classes)

    def missing_tones(pitch_classes: set[int]) -> str:
        missing = [
            key
            for key, tone_pitch_classes in tone_classes.items()
            if not any(pitch_class in pitch_classes for pitch_class in tone_pitch_classes)
        ]
        return compact_missing(missing)

    visible_tones = support_count(visible)
    analysis_tones = support_count(analysis)
    smooth_tones = support_count(smooth)
    root_visible = int(any(pitch_class in visible for pitch_class in tone_classes.get("root", [])))
    support = (
        f"visible{visible_tones}_analysis{analysis_tones}_"
        f"smooth{smooth_tones}_rootvis{root_visible}"
    )
    root_name = expected_root_name(expected_label)
    expected_labels_for_match = expected_labels or (
        [expected_label] if expected_label and row.get("status") != "single_note_false_chord" else []
    )

    result.update(
        {
            "expected_label": expected_label,
            "expected_root": root_name,
            "expected_quality_compact": compact_quality(expected_label),
            "quality": quality,
            "support": support,
            "guitar_match_kind": guitar_match_kind(
                expected_labels_for_match,
                expected_label,
                row.get("guitar_chord", ""),
                row.get("guitar_raw_chord", ""),
                row.get("guitar_smoothed_chord", ""),
            ),
            "expected_label_in_display": str(
                label_cell_contains(row.get("guitar_chord", ""), expected_labels_for_match)
            ),
            "expected_label_in_raw": str(
                label_cell_contains(row.get("guitar_raw_chord", ""), expected_labels_for_match)
            ),
            "expected_label_in_smooth": str(
                label_cell_contains(row.get("guitar_smoothed_chord", ""), expected_labels_for_match)
            ),
            "expected_root_in_display": str(root_cell_contains(row.get("guitar_chord", ""), root_name)),
            "guitar_pc_count": str(len(visible)),
            "analysis_pc_count": str(len(analysis)),
            "smooth_pc_count": str(len(smooth)),
            "visible_tones": str(visible_tones),
            "analysis_tones": str(analysis_tones),
            "smooth_tones": str(smooth_tones),
            "root_visible": str(root_visible),
            "visible_missing_tones": missing_tones(visible),
            "analysis_missing_tones": missing_tones(analysis),
            "smooth_missing_tones": missing_tones(smooth),
        }
    )

    for key in ("root", "third", "fifth"):
        pitch_classes = tone_classes.get(key, [])
        result[f"visible_{key}"] = f"{max_level(visible_levels, pitch_classes):.6f}"
        result[f"analysis_{key}"] = f"{max_level(analysis_levels, pitch_classes):.6f}"
        result[f"smooth_{key}"] = f"{max_level(smooth_levels, pitch_classes):.6f}"
        result[f"raw_{key}"] = f"{max_level(raw_levels, pitch_classes):.6f}"
        result[f"probe_{key}"] = f"{max_level(probe_levels, pitch_classes):.6f}"
        result[f"melodic_probe_{key}"] = f"{max_level(melodic_probe_levels, pitch_classes):.6f}"
    opposite_third = opposite_third_pitch_class(expected_label)
    raw_opposite_third = raw_levels.get(opposite_third, 0.0) if opposite_third is not None else 0.0
    probe_opposite_third = probe_levels.get(opposite_third, 0.0) if opposite_third is not None else 0.0
    melodic_probe_opposite_third = (
        melodic_probe_levels.get(opposite_third, 0.0) if opposite_third is not None else 0.0
    )
    raw_root = max_level(raw_levels, tone_classes.get("root", []))
    raw_third = max_level(raw_levels, tone_classes.get("third", []))
    raw_fifth = max_level(raw_levels, tone_classes.get("fifth", []))
    raw_anchor = max(raw_root, raw_fifth)
    probe_root = max_level(probe_levels, tone_classes.get("root", []))
    probe_third = max_level(probe_levels, tone_classes.get("third", []))
    probe_fifth = max_level(probe_levels, tone_classes.get("fifth", []))
    probe_anchor = max(probe_root, probe_fifth)
    melodic_probe_root = max_level(melodic_probe_levels, tone_classes.get("root", []))
    melodic_probe_third = max_level(melodic_probe_levels, tone_classes.get("third", []))
    melodic_probe_fifth = max_level(melodic_probe_levels, tone_classes.get("fifth", []))
    melodic_probe_anchor = max(melodic_probe_root, melodic_probe_fifth)
    result["raw_opposite_third"] = f"{raw_opposite_third:.6f}"
    raw_third_anchor_ratio = raw_third / raw_anchor if raw_anchor > 1.0e-6 else 0.0
    raw_third_margin = raw_third - raw_opposite_third
    result["raw_third_anchor_ratio"] = f"{raw_third_anchor_ratio:.6f}"
    result["raw_third_opposite_margin"] = f"{raw_third_margin:.6f}"
    result["probe_opposite_third"] = f"{probe_opposite_third:.6f}"
    probe_third_anchor_ratio = probe_third / probe_anchor if probe_anchor > 1.0e-6 else 0.0
    probe_third_margin = probe_third - probe_opposite_third
    result["probe_third_anchor_ratio"] = f"{probe_third_anchor_ratio:.6f}"
    result["probe_third_opposite_margin"] = f"{probe_third_margin:.6f}"
    result["melodic_probe_opposite_third"] = f"{melodic_probe_opposite_third:.6f}"
    melodic_probe_third_anchor_ratio = (
        melodic_probe_third / melodic_probe_anchor if melodic_probe_anchor > 1.0e-6 else 0.0
    )
    melodic_probe_third_margin = melodic_probe_third - melodic_probe_opposite_third
    result["melodic_probe_third_anchor_ratio"] = (
        f"{melodic_probe_third_anchor_ratio:.6f}"
    )
    result["melodic_probe_third_opposite_margin"] = f"{melodic_probe_third_margin:.6f}"

    display_exact = result["expected_label_in_display"] == "1"
    raw_exact = result["expected_label_in_raw"] == "1"
    smooth_exact = result["expected_label_in_smooth"] == "1"
    root_any = any(tone_present(tone_classes, pitch_classes, "root") for pitch_classes in (visible, analysis, smooth))
    third_any = any(tone_present(tone_classes, pitch_classes, "third") for pitch_classes in (visible, analysis, smooth))
    fifth_any = any(tone_present(tone_classes, pitch_classes, "fifth") for pitch_classes in (visible, analysis, smooth))
    quality_gap, quality_source = strong_third_evidence(
        [
            ("raw", raw_third_anchor_ratio, raw_third_margin),
            ("probe", probe_third_anchor_ratio, probe_third_margin),
            ("melodic", melodic_probe_third_anchor_ratio, melodic_probe_third_margin),
        ]
    )
    if display_exact:
        evidence_class, evidence_source = "display_exact", "display"
    elif raw_exact:
        evidence_class, evidence_source = "raw_exact_not_displayed", "raw"
    elif smooth_exact:
        evidence_class, evidence_source = "smooth_exact_not_displayed", "smooth"
    elif result["visible_missing_tones"] == "--":
        evidence_class, evidence_source = "visible_full_tone_label_gap", "visible"
    elif result["analysis_missing_tones"] == "--":
        evidence_class, evidence_source = "analysis_full_tone_label_gap", "analysis"
    elif result["smooth_missing_tones"] == "--":
        evidence_class, evidence_source = "smooth_full_tone_label_gap", "smooth"
    elif quality_gap and root_any and fifth_any:
        evidence_class, evidence_source = quality_gap, quality_source
    elif root_any and fifth_any and not third_any:
        evidence_class, evidence_source = "power_only_ambiguous", "root_fifth"
    elif not root_any:
        evidence_class, evidence_source = "expected_root_absent", "grid"
    elif not third_any:
        evidence_class, evidence_source = "third_missing", "grid"
    elif not fifth_any:
        evidence_class, evidence_source = "fifth_missing", "grid"
    else:
        evidence_class, evidence_source = "partial_or_wrong_label", "grid"
    result["evidence_class"] = evidence_class
    result["evidence_source"] = evidence_source
    result["quality_raw"] = row.get("expected_quality_raw_profile", "--") or "--"
    result["raw_pitch_class_levels"] = row.get("raw_pitch_class_levels", "--") or "--"
    result["guitar_probe_pitch_class_levels"] = row.get("guitar_probe_pitch_class_levels", "--") or "--"
    result["guitar_melodic_probe_pitch_class_levels"] = (
        row.get("guitar_melodic_probe_pitch_class_levels", "--") or "--"
    )
    return result


def derive_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        derive_row(row)
        for row in rows
        if row.get("expected_chords", "--") not in {"", "--"}
        or row.get("status") in {"single_note_false_chord", "no_chord"}
    ]


def parse_bucket_spec(spec: str) -> tuple[str, str, str]:
    match = BUCKET_RE.fullmatch(spec)
    if not match:
        raise SystemExit(
            f"invalid bucket `{spec}`; expected format status:quality:support, e.g. "
            "chord_miss:maj:visible2_analysis3_smooth3_rootvis1"
        )
    return match.group(1), match.group(2), match.group(3)


def bucket_label(bucket: tuple[str, str, str]) -> str:
    return f"{bucket[0]}:{bucket[1]}:{bucket[2]}"


def bucket_matches(row: dict[str, str], bucket: tuple[str, str, str]) -> bool:
    status, quality, support = bucket
    if status not in {"all", "any"} and row.get("status") != status:
        return False
    if quality not in {"all", "any"} and row.get("quality") != quality:
        return False
    return support in {"all", "any"} or row.get("support") == support


def bucket_rows(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> list[dict[str, str]]:
    return [row for row in rows if bucket_matches(row, bucket)]


def bucket_recording_count(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> int:
    return len({row.get("recording_id", "") for row in rows if bucket_matches(row, bucket)})


def top_bucket_keys(
    rows: list[dict[str, str]],
    top_misses: int,
    *,
    include_comparisons: bool,
) -> list[tuple[str, str, str]]:
    counts: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for row in rows:
        if row.get("status") != "chord_miss":
            continue
        counts[(row.get("status", ""), row.get("quality", ""), row.get("support", ""))] += 1

    keys: list[tuple[str, str, str]] = []
    for key, _count in counts.most_common(max(0, top_misses)):
        keys.append(key)
        if not include_comparisons:
            continue
        quality = key[1]
        for comparison in (("chord_hit", quality, key[2]), ("chord_hit", quality, "all")):
            if bucket_recording_count(rows, comparison) > 0:
                keys.append(comparison)

    deduped: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        if bucket_recording_count(rows, key) <= 0:
            continue
        deduped.append(key)
    return deduped


def as_float_opt(row: dict[str, str], field: str) -> float | None:
    try:
        value = row[field]
    except KeyError:
        return None
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def compact_counts(rows: list[dict[str, str]], field: str, limit: int = 8) -> str:
    counts = collections.Counter(row.get(field, "") for row in rows if row.get(field, ""))
    if not counts:
        return ""
    return " ".join(f"{key}={value}" for key, value in counts.most_common(limit))


def print_bucket(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    *,
    example_limit: int,
    summary_only: bool,
) -> None:
    rows_for_bucket = bucket_rows(rows, bucket)
    recordings = sorted({row.get("recording_id", "") for row in rows_for_bucket})
    examples = ", ".join(recordings[: max(0, example_limit)])
    print()
    print(
        f"{bucket_label(bucket)} rows={len(rows_for_bucket)} recordings={len(recordings)} "
        f"examples={examples}"
    )
    for field in CATEGORY_FIELDS:
        counts = compact_counts(rows_for_bucket, field)
        if counts:
            print(f"  {field:31s} {counts}")
    if summary_only:
        return
    for field in NUMERIC_FIELDS:
        values = sorted(value for row in rows_for_bucket if (value := as_float_opt(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:31s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )


def format_score(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def print_recording(rows: list[dict[str, str]], recording_id: str) -> None:
    sample_rows = [row for row in rows if row.get("recording_id") == recording_id]
    print()
    if not sample_rows:
        print(f"recording {recording_id}: no rows")
        return
    for row in sample_rows:
        print(
            f"recording {recording_id}: status={row.get('status', '')} "
            f"expected={row.get('expected_chords', '')} quality={row.get('quality', '')} "
            f"guitar={row.get('guitar_chord', '')} support={row.get('support', '')} "
            f"match={row.get('guitar_match_kind', '--')} "
            f"evidence={row.get('evidence_class', '--')}/{row.get('evidence_source', '--')}"
        )
        print(
            f"  pc visible={row.get('guitar_pitch_classes', '--')} "
            f"analysis={row.get('guitar_analysis_pitch_classes', '--')} "
            f"smooth={row.get('guitar_smoothed_pitch_classes', '--')}"
        )
        print(
            "  levels raw(root/third/fifth)="
            f"{format_score(as_float_opt(row, 'raw_root'))}/"
            f"{format_score(as_float_opt(row, 'raw_third'))}/"
            f"{format_score(as_float_opt(row, 'raw_fifth'))} "
            "opposite/anchor/margin="
            f"{format_score(as_float_opt(row, 'raw_opposite_third'))}/"
            f"{format_score(as_float_opt(row, 'raw_third_anchor_ratio'))}/"
            f"{format_score(as_float_opt(row, 'raw_third_opposite_margin'))} "
            "analysis="
            f"{format_score(as_float_opt(row, 'analysis_root'))}/"
            f"{format_score(as_float_opt(row, 'analysis_third'))}/"
            f"{format_score(as_float_opt(row, 'analysis_fifth'))} "
            "visible="
            f"{format_score(as_float_opt(row, 'visible_root'))}/"
            f"{format_score(as_float_opt(row, 'visible_third'))}/"
            f"{format_score(as_float_opt(row, 'visible_fifth'))}"
        )


def dump_rows(
    rows: list[dict[str, str]],
    *,
    buckets: list[tuple[str, str, str]],
    recording_ids: list[str],
    misses_only: bool,
    limit: int,
) -> None:
    bucket_filter = set(buckets)
    recording_filter = set(recording_ids)
    printed = 0
    print("\t".join(ROW_DUMP_FIELDS))
    for row in rows:
        if misses_only and row.get("status") != "chord_miss":
            continue
        if bucket_filter and not any(bucket_matches(row, bucket) for bucket in bucket_filter):
            continue
        if recording_filter and row.get("recording_id", "") not in recording_filter:
            continue
        print("\t".join(row.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--top-misses", type=int, default=8)
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="print only this bucket, formatted as status:quality:support; repeatable",
    )
    parser.add_argument(
        "--recording-id",
        action="append",
        default=[],
        help="print detailed derived attributes for this recording id; repeatable",
    )
    parser.add_argument("--examples", type=int, default=12)
    parser.add_argument(
        "--misses-only",
        action="store_true",
        help="print only largest chord-miss buckets, without chord-hit comparisons",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print bucket counts and categorical summaries without numeric feature ranges",
    )
    parser.add_argument(
        "--dump-rows",
        action="store_true",
        help="print compact per-recording chord attributes as TSV and skip bucket summaries",
    )
    parser.add_argument(
        "--dump-limit",
        type=int,
        default=0,
        help="maximum rows to print in --dump-rows mode; 0 means all",
    )
    args = parser.parse_args()

    rows = derive_rows(load_rows(pathlib.Path(args.path)))
    explicit_buckets = [parse_bucket_spec(spec) for spec in args.bucket]
    if args.dump_rows:
        dump_rows(
            rows,
            buckets=explicit_buckets,
            recording_ids=args.recording_id,
            misses_only=args.misses_only,
            limit=max(0, args.dump_limit),
        )
        return 0

    if explicit_buckets:
        buckets = explicit_buckets
    elif args.recording_id:
        buckets = []
    else:
        buckets = top_bucket_keys(rows, args.top_misses, include_comparisons=not args.misses_only)

    for bucket in buckets:
        print_bucket(
            rows,
            bucket,
            example_limit=args.examples,
            summary_only=args.summary_only,
        )
    for recording_id in args.recording_id:
        print_recording(rows, recording_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
