#!/usr/bin/env python3
"""Summarize GuitarSet-style note/chord attribute TSV exports."""

from __future__ import annotations

import collections
import csv
import pathlib
import re
import statistics
import sys


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

QUALITY_INTERVALS = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "pow": (0, 7),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "dim7": (0, 3, 6, 9),
    "m7b5": (0, 3, 6, 10),
    "add9": (0, 2, 4, 7),
    "9": (0, 2, 4, 7, 10),
    "maj9": (0, 2, 4, 7, 11),
    "m9": (0, 2, 3, 7, 10),
}


def as_int(row: dict[str, str], field: str) -> int:
    try:
        return int(row.get(field, "") or "0")
    except ValueError:
        return 0


def as_float(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "") or "0")
    except ValueError:
        return 0.0


def ratio_text(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0/0 0.00%"
    return f"{numerator}/{denominator} {numerator * 100.0 / denominator:.2f}%"


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact_counter(counter: collections.Counter[str], limit: int = 12) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def split_labels(text: str) -> list[str]:
    if not text or text == "--":
        return []
    return [item for item in text.split("/") if item and item != "--"]


def chord_root(label: str) -> str:
    if not label:
        return ""
    if len(label) >= 2 and label[1] == "#":
        return label[:2]
    return label[:1]


def chord_quality(label: str) -> str:
    root = chord_root(label)
    return label[len(root) :]


def chord_tones(label: str) -> list[tuple[str, int]]:
    root = chord_root(label)
    intervals = QUALITY_INTERVALS.get(chord_quality(label))
    if root not in NOTE_TO_PC or intervals is None:
        return []
    root_pc = NOTE_TO_PC[root]
    tones = []
    for interval in intervals:
        if interval == 0:
            name = "root"
        elif interval == 3:
            name = "minor_third"
        elif interval == 4:
            name = "major_third"
        elif interval == 7:
            name = "fifth"
        elif interval in {10, 11}:
            name = "seventh"
        else:
            name = "extension"
        tones.append((name, (root_pc + interval) % 12))
    return tones


def chord_pitch_classes(label: str) -> set[int]:
    return {pitch_class for _name, pitch_class in chord_tones(label)}


def parse_pitch_classes(text: str) -> set[int]:
    if not text or text == "--":
        return set()
    return {NOTE_TO_PC[item] for item in text.split(",") if item in NOTE_TO_PC}


CELL_RE = re.compile(r"([A-G]#?)-?\d+:([-+0-9.eE]+)")


def parse_cell_levels(text: str) -> dict[int, float]:
    levels: dict[int, float] = {}
    if not text or text == "--":
        return levels
    for match in CELL_RE.finditer(text):
        note = match.group(1)
        if note not in NOTE_TO_PC:
            continue
        try:
            level = float(match.group(2))
        except ValueError:
            continue
        pitch_class = NOTE_TO_PC[note]
        levels[pitch_class] = max(levels.get(pitch_class, 0.0), level)
    return levels


def best_chord_coverage(expected_chords: str, pitch_classes: str) -> tuple[float, bool]:
    visible = parse_pitch_classes(pitch_classes)
    best = 0.0
    full = False
    for label in split_labels(expected_chords):
        expected = chord_pitch_classes(label)
        if not expected:
            continue
        coverage = len(expected & visible) / len(expected)
        best = max(best, coverage)
        full = full or expected <= visible
    return best, full


def best_expected_chord(expected_chords: str, pitch_classes: str) -> str:
    visible = parse_pitch_classes(pitch_classes)
    best_label = ""
    best_coverage = -1.0
    for label in split_labels(expected_chords):
        expected = chord_pitch_classes(label)
        if not expected:
            continue
        coverage = len(expected & visible) / len(expected)
        if coverage > best_coverage:
            best_coverage = coverage
            best_label = label
    if best_label:
        return best_label
    labels = split_labels(expected_chords)
    return labels[0] if labels else ""


def coverage_bucket(coverage: float) -> str:
    if coverage >= 1.0:
        return "100%"
    if coverage >= 0.75:
        return "75-99%"
    if coverage >= 0.50:
        return "50-74%"
    if coverage > 0.0:
        return "1-49%"
    return "0%"


def compact_level_summary(values_by_tone: dict[str, list[float]], limit: int = 8) -> str:
    items = []
    for tone, values in sorted(values_by_tone.items()):
        if not values:
            continue
        items.append((len(values), tone, statistics.median(values)))
    items.sort(key=lambda item: (-item[0], item[1]))
    if not items:
        return "--"
    return " ".join(f"{tone}={count}@{median:.2f}" for count, tone, median in items[:limit])


def note_recall_bucket(row: dict[str, str]) -> str:
    expected = as_int(row, "expected_note_count")
    hits = as_int(row, "guitar_note_hits")
    if expected <= 0:
        return "none"
    if hits >= expected:
        return "100%"
    if hits * 4 >= expected * 3:
        return "75-99%"
    if hits * 2 >= expected:
        return "50-74%"
    if hits > 0:
        return "1-49%"
    return "0%"


def example_text(row: dict[str, str]) -> str:
    return (
        f"{row.get('recording_id', '')}@{as_float(row, 'center_seconds'):.3f}s "
        f"expected={row.get('expected_chords', '--')} pc={row.get('expected_pitch_classes', '--')} "
        f"guitar={row.get('guitar_chord', '--')} guitar_pc={row.get('guitar_pitch_classes', '--')} "
        f"analysis_pc={row.get('guitar_analysis_pitch_classes', '--')} "
        f"smooth_pc={row.get('guitar_smoothed_pitch_classes', '--')}"
    )


def summarize(path: pathlib.Path) -> list[str]:
    rows = load_rows(path)
    recordings = {row.get("recording_id", "") for row in rows if row.get("recording_id", "")}
    status = collections.Counter(row.get("status", "") or "unknown" for row in rows)
    quality_status = collections.Counter(
        f"{row.get('expected_chord_qualities', '--')}:{row.get('status', 'unknown')}"
        for row in rows
    )
    note_recall = collections.Counter(note_recall_bucket(row) for row in rows)
    visible_chord_coverage: collections.Counter[str] = collections.Counter()
    analysis_chord_coverage: collections.Counter[str] = collections.Counter()
    smooth_chord_coverage: collections.Counter[str] = collections.Counter()
    visible_missing_tones: collections.Counter[str] = collections.Counter()
    analysis_missing_tones: collections.Counter[str] = collections.Counter()
    smooth_missing_tones: collections.Counter[str] = collections.Counter()
    visible_missing_analysis_present: collections.Counter[str] = collections.Counter()
    visible_missing_smooth_present: collections.Counter[str] = collections.Counter()
    analysis_missing_smooth_present: collections.Counter[str] = collections.Counter()
    chord_miss_support: collections.Counter[str] = collections.Counter()
    visible_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    analysis_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    smooth_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    raw_expected_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    visible_missing_raw_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    analysis_missing_raw_tone_levels: dict[str, list[float]] = collections.defaultdict(list)
    smooth_missing_raw_tone_levels: dict[str, list[float]] = collections.defaultdict(list)

    expected_notes = sum(as_int(row, "expected_note_count") for row in rows)
    guitar_hits = sum(as_int(row, "guitar_note_hits") for row in rows)
    false_positives = sum(as_int(row, "guitar_false_positive_pitch_classes") for row in rows)
    contamination = sum(as_int(row, "cross_row_expected_hits") for row in rows)
    chord_rows = [row for row in rows if row.get("expected_chords", "--") not in ("", "--")]
    chord_hits = sum(1 for row in chord_rows if row.get("chord_hit") == "1")
    simple_chord_hits = sum(1 for row in chord_rows if row.get("simple_chord_hit") == "1")
    guitar_chord_hits = sum(1 for row in chord_rows if row.get("guitar_chord_hit") == "1")
    visible_full_chord_misses = 0
    analysis_full_chord_misses = 0
    smooth_full_chord_misses = 0
    for row in chord_rows:
        visible_coverage, visible_full = best_chord_coverage(
            row.get("expected_chords", ""), row.get("guitar_pitch_classes", "")
        )
        analysis_coverage, analysis_full = best_chord_coverage(
            row.get("expected_chords", ""), row.get("guitar_analysis_pitch_classes", "")
        )
        smooth_coverage, smooth_full = best_chord_coverage(
            row.get("expected_chords", ""), row.get("guitar_smoothed_pitch_classes", "")
        )
        expected_label = best_expected_chord(
            row.get("expected_chords", ""), row.get("guitar_analysis_pitch_classes", "")
        )
        visible_pitch_classes = parse_pitch_classes(row.get("guitar_pitch_classes", ""))
        analysis_pitch_classes = parse_pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
        smooth_pitch_classes = parse_pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
        visible_levels = parse_cell_levels(row.get("guitar_cells", ""))
        analysis_levels = parse_cell_levels(row.get("guitar_analysis_cells", ""))
        smooth_levels = parse_cell_levels(row.get("guitar_smoothed_cells", ""))
        raw_levels = parse_cell_levels(row.get("expected_raw_cells", ""))
        expected_tones = chord_pitch_classes(expected_label)
        expected_root = chord_root(expected_label)
        expected_root_pc = NOTE_TO_PC.get(expected_root, -1)
        if row.get("status") == "chord_miss" and expected_tones:
            visible_tones = len(expected_tones & visible_pitch_classes)
            analysis_tones = len(expected_tones & analysis_pitch_classes)
            smooth_tones = len(expected_tones & smooth_pitch_classes)
            root_visible = expected_root_pc in visible_pitch_classes
            chord_miss_support[
                f"visible{visible_tones}_analysis{analysis_tones}_"
                f"smooth{smooth_tones}_rootvis{int(root_visible)}"
            ] += 1
        for tone_name, pitch_class in chord_tones(expected_label):
            visible_present = pitch_class in visible_pitch_classes
            analysis_present = pitch_class in analysis_pitch_classes
            smooth_present = pitch_class in smooth_pitch_classes
            if not visible_present:
                visible_missing_tones[tone_name] += 1
                if analysis_present:
                    visible_missing_analysis_present[tone_name] += 1
                if smooth_present:
                    visible_missing_smooth_present[tone_name] += 1
            if not analysis_present:
                analysis_missing_tones[tone_name] += 1
                if smooth_present:
                    analysis_missing_smooth_present[tone_name] += 1
            if not smooth_present:
                smooth_missing_tones[tone_name] += 1
            if visible_present:
                visible_tone_levels[tone_name].append(visible_levels.get(pitch_class, 0.0))
            if analysis_present:
                analysis_tone_levels[tone_name].append(analysis_levels.get(pitch_class, 0.0))
            if smooth_present:
                smooth_tone_levels[tone_name].append(smooth_levels.get(pitch_class, 0.0))
            raw_level = raw_levels.get(pitch_class)
            if raw_level is not None:
                raw_expected_tone_levels[tone_name].append(raw_level)
                if not visible_present:
                    visible_missing_raw_tone_levels[tone_name].append(raw_level)
                if not analysis_present:
                    analysis_missing_raw_tone_levels[tone_name].append(raw_level)
                if not smooth_present:
                    smooth_missing_raw_tone_levels[tone_name].append(raw_level)
        visible_chord_coverage[coverage_bucket(visible_coverage)] += 1
        analysis_chord_coverage[coverage_bucket(analysis_coverage)] += 1
        smooth_chord_coverage[coverage_bucket(smooth_coverage)] += 1
        if row.get("status") == "chord_miss":
            visible_full_chord_misses += 1 if visible_full else 0
            analysis_full_chord_misses += 1 if analysis_full else 0
            smooth_full_chord_misses += 1 if smooth_full else 0

    rms_values = [as_float(row, "rms") for row in rows]
    median_rms = statistics.median(rms_values) if rms_values else 0.0

    lines = [
        f"summarize_guitarset_attributes: rows {len(rows)} recordings {len(recordings)}",
        "status " + compact_counter(status),
        "note recall buckets " + compact_counter(note_recall, 8),
        "quality/status " + compact_counter(quality_status, 16),
        "guitar note recall " + ratio_text(guitar_hits, expected_notes),
        "guitar false-positive pitch classes " + str(false_positives),
        "cross-row expected hits " + str(contamination),
        "chord exact/global recall " + ratio_text(chord_hits, len(chord_rows)),
        "chord simplified recall " + ratio_text(simple_chord_hits, len(chord_rows)),
        "guitar chord exact recall " + ratio_text(guitar_chord_hits, len(chord_rows)),
        "visible chord-tone coverage " + compact_counter(visible_chord_coverage, 8),
        "analysis chord-tone coverage " + compact_counter(analysis_chord_coverage, 8),
        "smoothed chord-tone coverage " + compact_counter(smooth_chord_coverage, 8),
        "visible missing chord tones " + compact_counter(visible_missing_tones, 8),
        "analysis missing chord tones " + compact_counter(analysis_missing_tones, 8),
        "smoothed missing chord tones " + compact_counter(smooth_missing_tones, 8),
        "visible-missing but analysis-present tones "
        + compact_counter(visible_missing_analysis_present, 8),
        "visible-missing but smoothed-present tones "
        + compact_counter(visible_missing_smooth_present, 8),
        "analysis-missing but smoothed-present tones "
        + compact_counter(analysis_missing_smooth_present, 8),
        "chord miss support buckets " + compact_counter(chord_miss_support, 12),
        "visible present tone levels " + compact_level_summary(visible_tone_levels, 8),
        "analysis present tone levels " + compact_level_summary(analysis_tone_levels, 8),
        "smoothed present tone levels " + compact_level_summary(smooth_tone_levels, 8),
        "raw expected tone levels " + compact_level_summary(raw_expected_tone_levels, 8),
        "visible-missing raw tone levels " + compact_level_summary(visible_missing_raw_tone_levels, 8),
        "analysis-missing raw tone levels " + compact_level_summary(analysis_missing_raw_tone_levels, 8),
        "smoothed-missing raw tone levels " + compact_level_summary(smooth_missing_raw_tone_levels, 8),
        "full-tone chord misses visible/analysis/smoothed "
        + f"{visible_full_chord_misses}/{analysis_full_chord_misses}/{smooth_full_chord_misses}",
        f"median rms {median_rms:.6f}",
    ]

    missed = [row for row in rows if row.get("status") == "chord_miss"]
    if missed:
        lines.append("chord miss examples")
        for row in missed[:12]:
            lines.append("  " + example_text(row))

    weak_notes = [row for row in rows if note_recall_bucket(row) in {"0%", "1-49%", "50-74%"}]
    if weak_notes:
        lines.append("weak guitar-note examples")
        for row in weak_notes[:12]:
            lines.append("  " + example_text(row))

    return lines


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/guitarset_attributes.tsv")
    for line in summarize(path):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
