#!/usr/bin/env python3
"""Summarize real-note per-buffer detector attribute TSV exports."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics
import sys

NOTE_BASE = {
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
NOTE_CELL_RE = re.compile(r"([A-G]#?-?\d+):([0-9.]+)")

ROW_FOR_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}
ROW_NOTE_FIELDS = {
    "bass": "bass_notes",
    "guitar": "guitar_notes",
    "piano": "piano_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
}
ROW_VISUAL_NOTE_FIELDS = {
    "bass": "bass_visual_notes",
    "guitar": "guitar_visual_notes",
    "piano": "piano_visual_notes",
    "vocals": "vocal_visual_notes",
    "other": "other_visual_notes",
}
ALL_ROW_NOTE_FIELDS = {
    **ROW_NOTE_FIELDS,
    "amb": "amb_notes",
}
ROW_LEVEL_FIELDS = {
    "bass": "bass_level",
    "guitar": "guitar_level",
    "piano": "piano_level",
    "vocals": "vocal_level",
    "other": "other_level",
    "amb": "amb_level",
}


NUMERIC_FIELDS = [
    "row_conf",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "raw_expected_peak",
    "raw_expected_ratio",
    "raw_tuned_peak",
    "raw_tuned_ratio",
    "raw_tuned_cent_offset",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_midi",
    "raw_local_best_peak",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
    "rms",
    "low",
    "mid",
    "high",
    "kick",
    "snare",
    "hihat",
    "crash",
    "tom",
    "ride",
    "rim",
    "debug_conf",
    "onset_strength",
    "decay_rate",
    "pitch_stability",
    "simultaneous_onset",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


CONTEXT_SUMMARY_FIELDS = [
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
]


SUMMARY_FIELDS = [
    "debug_conf",
    "onset_strength",
    "decay_rate",
    "pitch_stability",
    "simultaneous_onset",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
]


SAMPLE_FIELDS = [
    "debug_conf",
    "onset_strength",
    "decay_rate",
    "pitch_stability",
    "simultaneous_onset",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_expected_rank",
    "partial2",
    "partial3",
    "partial4",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
]


CONFUSION_PROFILE_FIELDS = [
    "expected_row_level",
    "observed_row_level",
    "expected_row_exact_level",
    "expected_row_pitch_level",
    "observed_row_exact_level",
    "observed_row_pitch_level",
    "debug_exact_match",
    "debug_pitch_match",
    "debug_abs_delta",
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


WEAK_BUCKET_PROFILE_FIELDS = [
    "weak_exact_level",
    "weak_pitch_level",
    "weak_pitch_abs_delta",
    "rms",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "expected_row_score",
    "first_row_score",
    "visual_first_row_score",
    "expected_visual_first_score_ratio",
    "expected_visual_strongest_score_ratio",
]


def source_key(row: dict[str, str]) -> str:
    source = row.get("source") or row.get("nsynth_family") or "unknown"
    return f"{row.get('family', 'unknown')}/{source}"


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def median_text(rows: list[dict[str, str]], field: str) -> str:
    values = [value for row in rows if (value := as_float(row, field)) is not None]
    if not values:
        return "--"
    return f"{statistics.median(values):.3f}"


def compact_counter(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def fraction_text(count: int, total: int) -> str:
    if total <= 0:
        return f"{count}/{total} 0.0%"
    return f"{count}/{total} {count * 100.0 / total:.1f}%"


def percent_value(count: int, total: int) -> float:
    return count * 100.0 / total if total > 0 else 0.0


def parse_percent_spec(spec: str) -> tuple[str, float]:
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"invalid threshold `{spec}`; expected family=percent")
    family, percent_text_value = spec.split("=", 1)
    family = family.strip()
    if family not in ROW_FOR_FAMILY:
        raise argparse.ArgumentTypeError(f"invalid family `{family}` in threshold `{spec}`")
    try:
        value = float(percent_text_value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid percent `{percent_text_value}`") from exc
    if value < 0.0 or value > 100.0:
        raise argparse.ArgumentTypeError(f"percent out of range in threshold `{spec}`")
    return family, value


EXPECTED_ROW_STATES = ("lit_exact", "dim_exact", "lit_octave", "dim_octave", "absent")


def expected_row_state(exact_level: float, pitch_level: float, lit_threshold: float) -> str:
    if exact_level >= lit_threshold:
        return "lit_exact"
    if exact_level > 0.0:
        return "dim_exact"
    if pitch_level >= lit_threshold:
        return "lit_octave"
    if pitch_level > 0.0:
        return "dim_octave"
    return "absent"


def best_expected_row_sample_state(state: dict[str, bool]) -> str:
    if state["lit_exact"]:
        return "lit_exact"
    if state["exact"]:
        return "dim_exact"
    if state["lit_pitch"]:
        return "lit_octave"
    if state["pitch"]:
        return "dim_octave"
    return "absent"


def compact_state_counts(counter: collections.Counter[str], total: int) -> str:
    return " ".join(f"{state}={fraction_text(counter[state], total)}" for state in EXPECTED_ROW_STATES)


def expected_pitch_class(row: dict[str, str]) -> str:
    match = re.fullmatch(r"([A-G]#?)-?\d+", row.get("expected_note", ""))
    if match:
        return match.group(1)
    return row.get("expected_note", "--") or "--"


def expected_octave(row: dict[str, str]) -> str:
    try:
        midi = int(row.get("expected_midi", ""))
    except ValueError:
        return "--"
    return str(midi // 12 - 1)


def midi_from_note_label(note: str) -> int | None:
    match = re.fullmatch(r"([A-G]#?)(-?\d+)", note or "")
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def note_row_cells(value: str) -> list[tuple[int, float]]:
    cells: list[tuple[int, float]] = []
    for note, level in NOTE_CELL_RE.findall(value or ""):
        midi = midi_from_note_label(note)
        if midi is None:
            continue
        try:
            cells.append((midi, float(level)))
        except ValueError:
            continue
    return cells


def note_field_levels(row: dict[str, str], field: str, target_midi: int) -> tuple[float, float, int | None]:
    if not field:
        return 0.0, 0.0, None

    target_pitch = target_midi % 12
    exact_level = 0.0
    pitch_level = 0.0
    pitch_delta: int | None = None
    for midi, level in note_row_cells(row.get(field, "")):
        if midi == target_midi:
            exact_level = max(exact_level, level)
        if midi % 12 != target_pitch:
            continue
        if level > pitch_level:
            pitch_level = level
            pitch_delta = midi - target_midi
    return exact_level, pitch_level, pitch_delta


def note_row_levels(row: dict[str, str], row_name: str, target_midi: int) -> tuple[float, float, int | None]:
    return note_field_levels(row, ALL_ROW_NOTE_FIELDS.get(row_name, ""), target_midi)


def expected_midi(row: dict[str, str]) -> int | None:
    try:
        return int(row.get("expected_midi", ""))
    except ValueError:
        return None


def delta_label(delta: int) -> str:
    return f"{delta:+d}"


def note_range(samples: dict[str, dict[str, str]]) -> str:
    midis = []
    for row in samples.values():
        try:
            midis.append(int(row["expected_midi"]))
        except (KeyError, ValueError):
            pass
    if not midis:
        return "--"
    return f"{min(midis)}-{max(midis)}"


def median_parts(rows: list[dict[str, str]], fields: list[str]) -> str:
    return " ".join(f"{field}={median_text(rows, field)}" for field in fields)


def context_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("sample_id", ""), row.get("buffer", "")


def format_float(value: float) -> str:
    return f"{value:.3f}"


def debug_midi(row: dict[str, str]) -> int | None:
    value = as_float(row, "debug_midi")
    if value is not None:
        return int(round(value))
    return midi_from_note_label(row.get("debug_note", ""))


def select_confusion_debug_row(
    rows: list[dict[str, str]], target_midi: int, observed_row: str
) -> dict[str, str]:
    candidates = [row for row in rows if row.get("debug_note") or row.get("debug_midi")]
    if not candidates:
        return rows[0] if rows else {}

    target_pitch = target_midi % 12

    def score(row: dict[str, str]) -> tuple[int, int, int, int, float]:
        midi = debug_midi(row)
        exact = midi == target_midi
        pitch = midi is not None and midi % 12 == target_pitch
        abs_delta = abs(midi - target_midi) if midi is not None else 999
        return (
            int(row.get("debug_owner", "") == observed_row),
            int(exact),
            int(pitch),
            -min(abs_delta, 999),
            as_float(row, "debug_conf") or 0.0,
        )

    return max(candidates, key=score)


def confusion_profile_row(
    context_row: dict[str, str],
    selected_debug_row: dict[str, str],
    *,
    expected_row: str,
    observed_row: str,
    target_midi: int,
) -> dict[str, str]:
    profile = dict(selected_debug_row or context_row)
    profile["sample_id"] = context_row.get("sample_id", "")

    expected_level_field = ROW_LEVEL_FIELDS.get(expected_row, "")
    observed_level_field = ROW_LEVEL_FIELDS.get(observed_row, "")
    profile["expected_row_level"] = format_float(as_float(context_row, expected_level_field) or 0.0)
    profile["observed_row_level"] = format_float(as_float(context_row, observed_level_field) or 0.0)

    expected_exact, expected_pitch, _expected_delta = note_row_levels(context_row, expected_row, target_midi)
    observed_exact, observed_pitch, _observed_delta = note_row_levels(context_row, observed_row, target_midi)
    profile["expected_row_exact_level"] = format_float(expected_exact)
    profile["expected_row_pitch_level"] = format_float(expected_pitch)
    profile["observed_row_exact_level"] = format_float(observed_exact)
    profile["observed_row_pitch_level"] = format_float(observed_pitch)

    midi = debug_midi(profile)
    if midi is None:
        profile["debug_exact_match"] = "0"
        profile["debug_pitch_match"] = "0"
        profile["debug_abs_delta"] = ""
    else:
        profile["debug_exact_match"] = "1" if midi == target_midi else "0"
        profile["debug_pitch_match"] = "1" if midi % 12 == target_midi % 12 else "0"
        profile["debug_abs_delta"] = str(abs(midi - target_midi))
    return profile


def debug_rows_for_sample_ids(
    rows_by_sample: dict[str, list[dict[str, str]]], sample_ids: set[str]
) -> list[dict[str, str]]:
    debug_rows = []
    for sample_id in sample_ids:
        debug_rows.extend(row for row in rows_by_sample.get(sample_id, []) if row.get("debug_note"))
    return debug_rows


def unique_context_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row.get("sample_id", ""), row.get("buffer", ""))
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
    return selected


def extra_note_summary_for_fields(
    context_rows: list[dict[str, str]], note_fields: dict[str, str]
) -> dict[str, object]:
    extra_pitch_buffers = 0
    extra_exact_buffers = 0
    extra_pitch_rows = 0
    extra_exact_rows = 0
    extra_pitch_by_source_row: collections.Counter[str] = collections.Counter()
    extra_exact_by_source_row: collections.Counter[str] = collections.Counter()
    extra_exact_examples: dict[str, list[str]] = collections.defaultdict(list)
    extra_note_cells = 0
    extra_same_pitch_cells = 0
    extra_exact_cells = 0
    extra_note_delta_by_source_row: collections.Counter[str] = collections.Counter()
    extra_same_pitch_delta_by_source_row: collections.Counter[str] = collections.Counter()
    sample_pitch_buffers: collections.Counter[str] = collections.Counter()
    sample_exact_buffers: collections.Counter[str] = collections.Counter()
    sample_extra_rows: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)

    for row in context_rows:
        midi = expected_midi(row)
        expected_row = ROW_FOR_FAMILY.get(row.get("family", ""))
        sample_id = row.get("sample_id", "")
        if midi is None or not expected_row or not sample_id:
            continue

        target_pitch = midi % 12
        source = source_key(row)
        pitch_rows: list[str] = []
        exact_rows: list[str] = []
        for row_name, field in note_fields.items():
            if row_name == expected_row:
                continue
            cells_by_midi: dict[int, float] = {}
            for candidate_midi, level in note_row_cells(row.get(field, "")):
                cells_by_midi[candidate_midi] = max(cells_by_midi.get(candidate_midi, 0.0), level)
            has_pitch = any(candidate_midi % 12 == target_pitch for candidate_midi in cells_by_midi)
            exact_level = cells_by_midi.get(midi, 0.0)
            has_exact = exact_level > 0.0

            for candidate_midi in cells_by_midi:
                delta = candidate_midi - midi
                key = f"{source}->{row_name}:{delta_label(delta)}"
                extra_note_cells += 1
                extra_note_delta_by_source_row[key] += 1
                if candidate_midi % 12 == target_pitch:
                    extra_same_pitch_cells += 1
                    extra_same_pitch_delta_by_source_row[key] += 1
                if candidate_midi == midi:
                    extra_exact_cells += 1

            if has_pitch:
                pitch_rows.append(row_name)
            if has_exact:
                exact_rows.append(row_name)
                key = f"{source}->{row_name}"
                extra_exact_examples[key].append(
                    f"{sample_id}@{row.get('buffer', '')} "
                    f"expected={row.get('expected_note', '')}/{midi} "
                    f"level={exact_level:.2f} first={row.get('first_row', '')} "
                    f"strongest={row.get('buffer_strongest_row', '')}"
                )

        if pitch_rows:
            extra_pitch_buffers += 1
            sample_pitch_buffers[sample_id] += 1
        if exact_rows:
            extra_exact_buffers += 1
            sample_exact_buffers[sample_id] += 1

        for row_name in pitch_rows:
            extra_pitch_rows += 1
            key = f"{source}->{row_name}"
            extra_pitch_by_source_row[key] += 1
            sample_extra_rows[sample_id][row_name] += 1
        for row_name in exact_rows:
            extra_exact_rows += 1
            extra_exact_by_source_row[f"{source}->{row_name}"] += 1

    sample_count = len({row.get("sample_id", "") for row in context_rows if row.get("sample_id")})
    return {
        "buffers": len(context_rows),
        "samples": sample_count,
        "extra_pitch_buffers": extra_pitch_buffers,
        "extra_pitch_rows": extra_pitch_rows,
        "extra_exact_buffers": extra_exact_buffers,
        "extra_exact_rows": extra_exact_rows,
        "extra_pitch_by_source_row": extra_pitch_by_source_row,
        "extra_exact_by_source_row": extra_exact_by_source_row,
        "extra_exact_examples": extra_exact_examples,
        "extra_note_cells": extra_note_cells,
        "extra_same_pitch_cells": extra_same_pitch_cells,
        "extra_exact_cells": extra_exact_cells,
        "extra_note_delta_by_source_row": extra_note_delta_by_source_row,
        "extra_same_pitch_delta_by_source_row": extra_same_pitch_delta_by_source_row,
        "sample_pitch_buffers": sample_pitch_buffers,
        "sample_exact_buffers": sample_exact_buffers,
        "sample_extra_rows": sample_extra_rows,
    }


def append_extra_note_summary_lines(
    lines: list[str], label: str, summary: dict[str, object], sample_limit: int
) -> None:
    extra_pitch_by_source_row = summary["extra_pitch_by_source_row"]
    extra_exact_by_source_row = summary["extra_exact_by_source_row"]
    extra_note_delta_by_source_row = summary["extra_note_delta_by_source_row"]
    extra_same_pitch_delta_by_source_row = summary["extra_same_pitch_delta_by_source_row"]
    limit = max(8, sample_limit if sample_limit > 0 else 8)
    lines.append(
        f"{label} note-row summary "
        f"buffers={summary['buffers']} samples={summary['samples']} "
        f"extra_pitch_buffers={summary['extra_pitch_buffers']} "
        f"extra_pitch_rows={summary['extra_pitch_rows']} "
        f"extra_exact_buffers={summary['extra_exact_buffers']} "
        f"extra_exact_rows={summary['extra_exact_rows']}"
    )
    lines.append(
        f"top {label} pitch source/row "
        + compact_counter(extra_pitch_by_source_row, limit)
    )
    lines.append(
        f"top {label} exact source/row "
        + compact_counter(extra_exact_by_source_row, limit)
    )
    lines.append(
        f"{label} note-cell intervals "
        f"cells={summary['extra_note_cells']} "
        f"same_pitch_class={summary['extra_same_pitch_cells']} "
        f"exact={summary['extra_exact_cells']}"
    )
    lines.append(
        f"top {label} note-cell delta "
        + compact_counter(extra_note_delta_by_source_row, limit)
    )
    lines.append(
        f"top {label} same-pitch/octave delta "
        + compact_counter(extra_same_pitch_delta_by_source_row, limit)
    )


def append_extra_note_row_summary(
    lines: list[str], rows: list[dict[str, str]], sample_limit: int
) -> None:
    context_rows = unique_context_rows(rows)
    summary = extra_note_summary_for_fields(context_rows, ROW_NOTE_FIELDS)
    append_extra_note_summary_lines(lines, "extra", summary, sample_limit)

    if context_rows and all(field in context_rows[0] for field in ROW_VISUAL_NOTE_FIELDS.values()):
        visual_summary = extra_note_summary_for_fields(context_rows, ROW_VISUAL_NOTE_FIELDS)
        append_extra_note_summary_lines(lines, "visible extra", visual_summary, sample_limit)

    sample_pitch_buffers = summary["sample_pitch_buffers"]
    sample_exact_buffers = summary["sample_exact_buffers"]
    sample_extra_rows = summary["sample_extra_rows"]
    extra_exact_by_source_row = summary["extra_exact_by_source_row"]
    extra_exact_examples = summary["extra_exact_examples"]

    if sample_limit <= 0 or not sample_pitch_buffers:
        return

    lines.append("top extra-row samples")
    for sample_id, count in sample_pitch_buffers.most_common(sample_limit):
        rows_text = compact_counter(sample_extra_rows.get(sample_id, collections.Counter()), 5)
        exact = sample_exact_buffers.get(sample_id, 0)
        lines.append(
            f"  {sample_id} pitch_buffers={count} exact_buffers={exact} rows={rows_text}"
        )

    if extra_exact_by_source_row:
        lines.append("top extra exact examples")
        for key, _count in extra_exact_by_source_row.most_common(sample_limit):
            examples = " | ".join(extra_exact_examples.get(key, [])[:sample_limit])
            lines.append(f"  {key} {examples}")


def expected_row_coverage_for_fields(
    context_rows: list[dict[str, str]],
    note_fields: dict[str, str],
    *,
    lit_threshold: float = 0.25,
) -> dict[str, object]:
    sample_states: dict[str, dict[str, bool]] = collections.defaultdict(
        lambda: {"exact": False, "pitch": False, "lit_exact": False, "lit_pitch": False}
    )
    family_sample_states: dict[str, dict[str, dict[str, bool]]] = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: {"exact": False, "pitch": False, "lit_exact": False, "lit_pitch": False}
        )
    )
    family_samples: dict[str, set[str]] = collections.defaultdict(set)
    exact_levels: list[float] = []
    pitch_levels: list[float] = []
    exact_buffers = 0
    pitch_buffers = 0
    lit_exact_buffers = 0
    lit_pitch_buffers = 0
    total_buffers = 0
    buffer_states: collections.Counter[str] = collections.Counter()
    family_buffer_states: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)

    for row in context_rows:
        sample_id = row.get("sample_id", "")
        family = row.get("family", "")
        expected_row = ROW_FOR_FAMILY.get(family, "")
        field = note_fields.get(expected_row, "")
        midi = expected_midi(row)
        if not sample_id or not family or not field or midi is None:
            continue

        total_buffers += 1
        family_samples[family].add(sample_id)
        exact_level, pitch_level, _pitch_delta = note_field_levels(row, field, midi)
        exact_levels.append(exact_level)
        pitch_levels.append(pitch_level)
        row_state = expected_row_state(exact_level, pitch_level, lit_threshold)
        buffer_states[row_state] += 1
        family_buffer_states[family][row_state] += 1

        exact = exact_level > 0.0
        pitch = pitch_level > 0.0
        lit_exact = exact_level >= lit_threshold
        lit_pitch = pitch_level >= lit_threshold
        if exact:
            exact_buffers += 1
        if pitch:
            pitch_buffers += 1
        if lit_exact:
            lit_exact_buffers += 1
        if lit_pitch:
            lit_pitch_buffers += 1

        state = sample_states[sample_id]
        family_state = family_sample_states[family][sample_id]
        for key, value in (
            ("exact", exact),
            ("pitch", pitch),
            ("lit_exact", lit_exact),
            ("lit_pitch", lit_pitch),
        ):
            state[key] = state[key] or value
            family_state[key] = family_state[key] or value

    def sample_hit_count(key: str) -> int:
        return sum(1 for state in sample_states.values() if state[key])

    return {
        "buffers": total_buffers,
        "samples": len(sample_states),
        "exact_buffers": exact_buffers,
        "pitch_buffers": pitch_buffers,
        "lit_exact_buffers": lit_exact_buffers,
        "lit_pitch_buffers": lit_pitch_buffers,
        "exact_samples": sample_hit_count("exact"),
        "pitch_samples": sample_hit_count("pitch"),
        "lit_exact_samples": sample_hit_count("lit_exact"),
        "lit_pitch_samples": sample_hit_count("lit_pitch"),
        "exact_level_median": statistics.median(exact_levels) if exact_levels else 0.0,
        "pitch_level_median": statistics.median(pitch_levels) if pitch_levels else 0.0,
        "buffer_states": buffer_states,
        "family_buffer_states": family_buffer_states,
        "family_sample_states": family_sample_states,
        "family_samples": family_samples,
    }


def append_expected_row_coverage(
    lines: list[str], rows: list[dict[str, str]], sample_limit: int
) -> None:
    context_rows = unique_context_rows(rows)
    for label, note_fields in (("expected-row", ROW_NOTE_FIELDS), ("visible expected-row", ROW_VISUAL_NOTE_FIELDS)):
        if label.startswith("visible") and (
            not context_rows or not all(field in context_rows[0] for field in ROW_VISUAL_NOTE_FIELDS.values())
        ):
            continue
        coverage = expected_row_coverage_for_fields(context_rows, note_fields)
        lines.append(
            f"{label} coverage buffers "
            f"exact={fraction_text(coverage['exact_buffers'], coverage['buffers'])} "
            f"pitch={fraction_text(coverage['pitch_buffers'], coverage['buffers'])} "
            f"lit_exact>=0.25={fraction_text(coverage['lit_exact_buffers'], coverage['buffers'])} "
            f"lit_pitch>=0.25={fraction_text(coverage['lit_pitch_buffers'], coverage['buffers'])} "
            f"samples exact={fraction_text(coverage['exact_samples'], coverage['samples'])} "
            f"pitch={fraction_text(coverage['pitch_samples'], coverage['samples'])} "
            f"lit_exact>=0.25={fraction_text(coverage['lit_exact_samples'], coverage['samples'])} "
            f"lit_pitch>=0.25={fraction_text(coverage['lit_pitch_samples'], coverage['samples'])} "
            f"median_exact_level={coverage['exact_level_median']:.3f} "
            f"median_pitch_level={coverage['pitch_level_median']:.3f}"
        )

        family_samples = coverage["family_samples"]
        family_sample_states = coverage["family_sample_states"]
        if not family_samples:
            continue
        limit = max(8, sample_limit if sample_limit > 0 else 8)
        buffer_states = coverage["buffer_states"]
        family_buffer_states = coverage["family_buffer_states"]
        lines.append(
            f"{label} buffer states "
            + compact_state_counts(buffer_states, coverage["buffers"])
        )
        family_buffer_parts = []
        for family in sorted(family_samples):
            total_buffers = sum(family_buffer_states[family].values())
            family_buffer_parts.append(
                f"{family}[{compact_state_counts(family_buffer_states[family], total_buffers)}]"
            )
        lines.append(f"{label} buffer states by family " + " ".join(family_buffer_parts[:limit]))

        sample_states: collections.Counter[str] = collections.Counter()
        for states in family_sample_states.values():
            for state in states.values():
                sample_states[best_expected_row_sample_state(state)] += 1
        lines.append(
            f"{label} sample states "
            + compact_state_counts(sample_states, coverage["samples"])
        )
        family_state_parts = []
        for family in sorted(family_samples):
            total = len(family_samples[family])
            states = collections.Counter(
                best_expected_row_sample_state(state)
                for state in coverage["family_sample_states"][family].values()
            )
            family_state_parts.append(f"{family}[{compact_state_counts(states, total)}]")
        lines.append(f"{label} sample states by family " + " ".join(family_state_parts[:limit]))

        parts = []
        for family in sorted(family_samples):
            total = len(family_samples[family])
            states = family_sample_states[family]
            exact = sum(1 for state in states.values() if state["exact"])
            lit_exact = sum(1 for state in states.values() if state["lit_exact"])
            parts.append(f"{family}=exact:{fraction_text(exact, total)},lit:{fraction_text(lit_exact, total)}")
        lines.append(f"{label} sample coverage by family " + " ".join(parts[:limit]))
        append_expected_row_weak_bucket_summary(
            lines, label, context_rows, note_fields, sample_limit
        )


def validate_visible_lit_exact_samples(
    rows: list[dict[str, str]],
    *,
    min_sample_percent: float | None,
    min_family_sample_percent: list[tuple[str, float]],
) -> list[str]:
    if min_sample_percent is None and not min_family_sample_percent:
        return []

    context_rows = unique_context_rows(rows)
    if not context_rows:
        return ["visible expected-row lit_exact validation has no rows"]
    missing_fields = [
        field for field in ROW_VISUAL_NOTE_FIELDS.values() if field not in context_rows[0]
    ]
    if missing_fields:
        return [
            "visible expected-row lit_exact validation missing fields "
            + ",".join(sorted(missing_fields))
        ]

    coverage = expected_row_coverage_for_fields(context_rows, ROW_VISUAL_NOTE_FIELDS)
    failures: list[str] = []
    total_samples = int(coverage["samples"])
    lit_samples = int(coverage["lit_exact_samples"])
    if min_sample_percent is not None:
        actual = percent_value(lit_samples, total_samples)
        if actual + 1e-9 < min_sample_percent:
            failures.append(
                "visible expected-row lit_exact samples "
                f"{fraction_text(lit_samples, total_samples)} below {min_sample_percent:.1f}%"
            )

    family_samples = coverage["family_samples"]
    family_sample_states = coverage["family_sample_states"]
    for family, threshold in min_family_sample_percent:
        total = len(family_samples.get(family, set()))
        states = family_sample_states.get(family, {})
        lit = sum(1 for state in states.values() if state["lit_exact"])
        actual = percent_value(lit, total)
        if total <= 0:
            failures.append(f"visible expected-row lit_exact {family} has no samples")
        elif actual + 1e-9 < threshold:
            failures.append(
                f"visible expected-row lit_exact {family} samples "
                f"{fraction_text(lit, total)} below {threshold:.1f}%"
            )
    return failures


def append_expected_row_weak_bucket_summary(
    lines: list[str],
    label: str,
    context_rows: list[dict[str, str]],
    note_fields: dict[str, str],
    sample_limit: int,
) -> None:
    sample_states: dict[
        tuple[str, str], dict[str, dict[str, bool]]
    ] = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: {
                "exact": False,
                "pitch": False,
                "lit_exact": False,
                "lit_pitch": False,
            }
        )
    )
    weak_first_rows: dict[
        tuple[str, str], collections.Counter[str]
    ] = collections.defaultdict(collections.Counter)
    weak_pitch_classes: dict[
        tuple[str, str], collections.Counter[str]
    ] = collections.defaultdict(collections.Counter)
    weak_examples: dict[
        tuple[str, str], dict[str, tuple[tuple[int, float, float, str, str], str]]
    ] = collections.defaultdict(dict)
    weak_profiles: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
    weak_buffer_states: dict[tuple[str, str], collections.Counter[str]] = collections.defaultdict(collections.Counter)

    weak_state_rank = {
        "absent": 0,
        "dim_octave": 1,
        "lit_octave": 2,
        "dim_exact": 3,
        "lit_exact": 4,
    }

    for row in context_rows:
        sample_id = row.get("sample_id", "")
        expected_row = ROW_FOR_FAMILY.get(row.get("family", ""))
        field = note_fields.get(expected_row, "")
        midi = expected_midi(row)
        if not sample_id or not expected_row or not field or midi is None:
            continue

        bucket = (source_key(row), expected_octave(row))
        exact_level, pitch_level, _pitch_delta = note_field_levels(row, field, midi)

        state = sample_states[bucket][sample_id]
        exact = exact_level > 0.0
        pitch = pitch_level > 0.0
        lit_exact = exact_level >= 0.25
        lit_pitch = pitch_level >= 0.25
        state["exact"] = state["exact"] or exact
        state["pitch"] = state["pitch"] or pitch
        state["lit_exact"] = state["lit_exact"] or lit_exact
        state["lit_pitch"] = state["lit_pitch"] or lit_pitch

        if not lit_exact:
            first_row = row.get("first_row", "") or row.get("buffer_strongest_row", "") or "none"
            weak_first_rows[bucket][first_row] += 1
            weak_pitch_classes[bucket][expected_pitch_class(row)] += 1
            row_state = expected_row_state(exact_level, pitch_level, 0.25)
            weak_buffer_states[bucket][row_state] += 1
            pitch_delta_text = "none" if _pitch_delta is None else delta_label(_pitch_delta)
            strongest = row.get("buffer_strongest_row", "") or "none"
            visual = row.get("buffer_visual_strongest_row", "") or "none"
            profile = dict(row)
            profile["weak_exact_level"] = format_float(exact_level)
            profile["weak_pitch_level"] = format_float(pitch_level)
            profile["weak_pitch_abs_delta"] = (
                "" if _pitch_delta is None else str(abs(_pitch_delta))
            )
            weak_profiles[bucket].append(profile)
            score = (
                weak_state_rank[row_state],
                exact_level,
                -pitch_level,
                sample_id,
                row.get("buffer", ""),
            )
            text = (
                f"{sample_id}@{row.get('buffer', '')} "
                f"expected={row.get('expected_note', '')}/{midi} "
                f"state={row_state} exact={exact_level:.2f} "
                f"pitch={pitch_level:.2f} delta={pitch_delta_text} "
                f"first={first_row} strongest={strongest} visual={visual}"
            )
            current = weak_examples[bucket].get(sample_id)
            if current is None or score < current[0]:
                weak_examples[bucket][sample_id] = (score, text)

    records = []
    for bucket, states_by_sample in sample_states.items():
        total = len(states_by_sample)
        if total <= 0:
            continue
        lit_exact = sum(1 for state in states_by_sample.values() if state["lit_exact"])
        exact = sum(1 for state in states_by_sample.values() if state["exact"])
        state_counts = collections.Counter(
            best_expected_row_sample_state(state) for state in states_by_sample.values()
        )
        absent = state_counts["absent"]
        records.append(
            (
                lit_exact / total,
                exact / total,
                -absent,
                -total,
                bucket,
                total,
                lit_exact,
                exact,
                absent,
            )
        )

    if not records:
        return

    limit = max(8, sample_limit if sample_limit > 0 else 8)
    lines.append(f"{label} weak sample buckets")
    for (
        _lit_ratio,
        _exact_ratio,
        _neg_absent,
        _neg_total,
        bucket,
        total,
        lit_exact,
        exact,
        absent,
    ) in sorted(records)[:limit]:
        source, octave = bucket
        lines.append(
            f"  {source} octave={octave} samples={total} "
            f"lit_exact={fraction_text(lit_exact, total)} "
            f"exact={fraction_text(exact, total)} "
            f"absent={fraction_text(absent, total)} "
            f"weak_first_rows={compact_counter(weak_first_rows[bucket], 5)} "
            f"weak_pitch_classes={compact_counter(weak_pitch_classes[bucket], 5)}"
        )
        if weak_profiles.get(bucket):
            lines.append(
                "    weak_medians "
                + median_parts(weak_profiles[bucket], WEAK_BUCKET_PROFILE_FIELDS)
                + " states="
                + compact_counter(weak_buffer_states[bucket], 5)
            )
        if sample_limit > 0 and weak_examples.get(bucket):
            example_limit = min(4, sample_limit)
            examples = [
                text
                for _score, text in sorted(weak_examples[bucket].values(), key=lambda item: item[0])[
                    :example_limit
                ]
            ]
            lines.append("    weak_examples " + " | ".join(examples))


def append_row_confusion_pitch_summary(
    lines: list[str], rows: list[dict[str, str]], sample_limit: int
) -> None:
    context_rows = unique_context_rows(rows)
    rows_by_context: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        rows_by_context[context_key(row)].append(row)

    for label, observed_field in [
        ("strongest-row", "buffer_strongest_row"),
        ("visual-row", "buffer_visual_strongest_row"),
    ]:
        bucket_counts: collections.Counter[str] = collections.Counter()
        route_counts: collections.Counter[str] = collections.Counter()
        pitch_route_counts: collections.Counter[str] = collections.Counter()
        sample_ids: set[str] = set()
        bucket_samples: dict[str, set[str]] = collections.defaultdict(set)
        bucket_profiles: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
        route_profiles: dict[str, list[dict[str, str]]] = collections.defaultdict(list)

        for row in context_rows:
            expected_row = ROW_FOR_FAMILY.get(row.get("family", ""))
            observed_row = row.get(observed_field, "")
            sample_id = row.get("sample_id", "")
            target_midi = expected_midi(row)
            if not expected_row or not observed_row or observed_row == expected_row or target_midi is None:
                continue
            source = source_key(row)
            note = expected_pitch_class(row) + expected_octave(row)
            bucket = f"{source} {note}->{observed_row}"
            route = f"{source}->{observed_row}"
            pitch_route = f"{source} {expected_pitch_class(row)}->{observed_row}"
            bucket_counts[bucket] += 1
            route_counts[route] += 1
            pitch_route_counts[pitch_route] += 1
            if sample_id:
                sample_ids.add(sample_id)
                bucket_samples[bucket].add(sample_id)

            selected_debug_row = select_confusion_debug_row(
                rows_by_context.get(context_key(row), [row]), target_midi, observed_row
            )
            profile = confusion_profile_row(
                row,
                selected_debug_row,
                expected_row=expected_row,
                observed_row=observed_row,
                target_midi=target_midi,
            )
            bucket_profiles[bucket].append(profile)
            route_profiles[route].append(profile)

        limit = max(8, sample_limit if sample_limit > 0 else 8)
        lines.append(
            f"{label} confusion note buckets rows={sum(bucket_counts.values())} "
            f"samples={len(sample_ids)} "
            + compact_counter(bucket_counts, limit)
        )
        lines.append(
            f"{label} confusion routes " + compact_counter(route_counts, limit)
        )
        lines.append(
            f"{label} confusion pitch-class routes "
            + compact_counter(pitch_route_counts, limit)
        )
        if route_counts:
            lines.append(f"{label} confusion route medians")
            for route, row_count in route_counts.most_common(min(limit, 8)):
                profile_rows = route_profiles.get(route, [])
                samples = len({row.get("sample_id", "") for row in profile_rows if row.get("sample_id", "")})
                owners = collections.Counter(
                    row.get("debug_owner", "") for row in profile_rows if row.get("debug_owner", "")
                )
                lines.append(
                    f"  {route} rows={row_count} samples={samples} "
                    f"debug_owners={compact_counter(owners, 5)} "
                    + median_parts(profile_rows, CONFUSION_PROFILE_FIELDS)
                )

        if sample_limit <= 0 or not bucket_counts:
            continue
        lines.append(f"{label} confusion bucket samples")
        for bucket, row_count in bucket_counts.most_common(sample_limit):
            samples = sorted(bucket_samples.get(bucket, set()))[:sample_limit]
            lines.append(
                f"  {bucket} rows={row_count} samples={len(bucket_samples.get(bucket, set()))} "
                + " ".join(samples)
            )
        lines.append(f"{label} confusion bucket medians")
        for bucket, row_count in bucket_counts.most_common(sample_limit):
            profile_rows = bucket_profiles.get(bucket, [])
            samples = len({row.get("sample_id", "") for row in profile_rows if row.get("sample_id", "")})
            owners = collections.Counter(
                row.get("debug_owner", "") for row in profile_rows if row.get("debug_owner", "")
            )
            lines.append(
                f"  {bucket} rows={row_count} samples={samples} "
                f"debug_owners={compact_counter(owners, 5)} "
                + median_parts(profile_rows, CONFUSION_PROFILE_FIELDS)
            )


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader)


def append_detailed_breakdown(
    lines: list[str],
    rows: list[dict[str, str]],
    samples: dict[str, dict[str, str]],
    detail_limit: int,
    sample_limit: int,
) -> None:
    if detail_limit <= 0 and sample_limit <= 0:
        return

    rows_by_sample: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        rows_by_sample[row.get("sample_id", "")].append(row)

    if detail_limit > 0:
        samples_by_source: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
        for sample in samples.values():
            samples_by_source[source_key(sample)].append(sample)

        lines.append("source detail")
        for source, source_samples in sorted(samples_by_source.items()):
            source_sample_map = {row.get("sample_id", ""): row for row in source_samples}
            source_debug_rows = debug_rows_for_sample_ids(
                rows_by_sample, set(source_sample_map.keys())
            )
            status = collections.Counter(row.get("status", "unknown") for row in source_samples)
            first_rows = collections.Counter(row.get("first_row", "none") for row in source_samples)
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in source_debug_rows if row.get("debug_owner")
            )
            lines.append(
                f"  {source} samples={len(source_samples)} midi={note_range(source_sample_map)} "
                f"status={compact_counter(status)} first_rows={compact_counter(first_rows)} "
                f"debug_owners={compact_counter(owners)} {median_parts(source_debug_rows, SAMPLE_FIELDS)}"
            )

        pitch_bucket_ids: dict[tuple[str, str, str, str, str], set[str]] = collections.defaultdict(set)
        octave_bucket_ids: dict[tuple[str, str, str, str], set[str]] = collections.defaultdict(set)
        for sample_id, sample in samples.items():
            status = sample.get("status", "unknown")
            if status == "hit":
                continue
            source = source_key(sample)
            first_row = sample.get("first_row", "none")
            pitch_bucket_ids[
                (status, source, expected_pitch_class(sample), expected_octave(sample), first_row)
            ].add(sample_id)
            octave_bucket_ids[(status, source, expected_octave(sample), first_row)].add(sample_id)

        lines.append("non-hit pitch buckets")
        for (status, source, pitch_class, octave, first_row), sample_ids in sorted(
            pitch_bucket_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )[:detail_limit]:
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, sample_ids)
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            debug_notes = collections.Counter(
                row.get("debug_note", "none") for row in debug_rows if row.get("debug_note")
            )
            lines.append(
                f"  {status}:{source} note={pitch_class}{octave}->"
                f"{first_row} samples={len(sample_ids)} debug_owners={compact_counter(owners)} "
                f"debug_notes={compact_counter(debug_notes, 5)} {median_parts(debug_rows, SAMPLE_FIELDS)}"
            )

        lines.append("non-hit octave buckets")
        for (status, source, octave, first_row), sample_ids in sorted(
            octave_bucket_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )[:detail_limit]:
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, sample_ids)
            expected_notes = collections.Counter(
                samples[sample_id].get("expected_note", "--") for sample_id in sample_ids
            )
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            lines.append(
                f"  {status}:{source} octave={octave}->{first_row} samples={len(sample_ids)} "
                f"expected={compact_counter(expected_notes, 6)} debug_owners={compact_counter(owners)} "
                f"{median_parts(debug_rows, SAMPLE_FIELDS)}"
            )

    if sample_limit > 0:
        non_hit_samples = [
            sample for sample in samples.values() if sample.get("status", "hit") != "hit"
        ]
        non_hit_samples.sort(
            key=lambda row: (
                row.get("status", ""),
                source_key(row),
                int(row.get("expected_midi", "0") or "0"),
                row.get("sample_id", ""),
            )
        )
        lines.append("non-hit sample attributes")
        for sample in non_hit_samples[:sample_limit]:
            sample_id = sample.get("sample_id", "")
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, {sample_id})
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            debug_notes = collections.Counter(
                row.get("debug_note", "none") for row in debug_rows if row.get("debug_note")
            )
            strongest = collections.Counter(
                row.get("buffer_strongest_row", "none")
                for row in rows_by_sample.get(sample_id, [])
                if row.get("buffer_strongest_row")
            )
            lines.append(
                f"  {sample_id} status={sample.get('status', '')} source={source_key(sample)} "
                f"expected={sample.get('expected_note', '')}/{sample.get('expected_midi', '')} "
                f"first_row={sample.get('first_row', '')} strongest={compact_counter(strongest, 4)} "
                f"debug_owners={compact_counter(owners, 4)} debug_notes={compact_counter(debug_notes, 5)} "
                f"{median_parts(debug_rows, SAMPLE_FIELDS)}"
            )


def summarize(path: pathlib.Path, detail_limit: int = 0, sample_limit: int = 0) -> list[str]:
    rows = load_rows(path)
    samples: dict[str, dict[str, str]] = {}
    for row in rows:
        samples.setdefault(row["sample_id"], row)

    status_counts = collections.Counter(row["status"] for row in samples.values())
    group_counts = collections.Counter(
        (row["status"], source_key(row), row.get("first_row", "none")) for row in samples.values()
    )
    source_counts = collections.Counter(source_key(row) for row in samples.values())

    lines = [
        f"summarize_real_note_attributes: rows {len(rows)} samples {len(samples)} note-midi-range {note_range(samples)}",
        "sample status " + " ".join(f"{key}={value}" for key, value in status_counts.most_common()),
        "sample sources " + " ".join(f"{key}={value}" for key, value in source_counts.most_common(10)),
    ]

    if group_counts:
        non_hit_groups = [
            (key, count) for key, count in group_counts.most_common() if key[0] != "hit"
        ]
        if non_hit_groups:
            lines.append(
                "top non-hit status/source/first-row "
                + " ".join(
                    f"{status}:{source}->{row_name}={count}"
                    for (status, source, row_name), count in non_hit_groups[:12]
                )
            )
        lines.append(
            "top hit status/source/first-row "
            + " ".join(
                f"{status}:{source}->{row_name}={count}"
                for (status, source, row_name), count in group_counts.most_common(12)
                if status == "hit"
            )
        )

    rows_by_group: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        if not row.get("debug_note"):
            continue
        rows_by_group[(row["status"], source_key(row), row.get("first_row", "none"))].append(row)

    context_rows_by_group: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in unique_context_rows(rows):
        context_rows_by_group[(row["status"], source_key(row), row.get("first_row", "none"))].append(row)

    median_keys = [key for key, _count in group_counts.most_common() if key[0] != "hit"][:8]
    median_keys += [key for key, _count in group_counts.most_common() if key[0] == "hit"][:5]
    seen_median_keys = set()
    for key in median_keys:
        if key in seen_median_keys:
            continue
        seen_median_keys.add(key)
        count = group_counts[key]
        debug_rows = rows_by_group.get(key, [])
        status, source, row_name = key
        if debug_rows:
            parts = [f"{field}={median_text(debug_rows, field)}" for field in SUMMARY_FIELDS]
            lines.append(
                f"debug medians {status}:{source}->{row_name} samples={count} debug_rows={len(debug_rows)} "
                + " ".join(parts)
            )
        context_rows = context_rows_by_group.get(key, [])
        if context_rows:
            context_parts = [f"{field}={median_text(context_rows, field)}" for field in CONTEXT_SUMMARY_FIELDS]
            lines.append(
                f"context medians {status}:{source}->{row_name} samples={count} "
                f"buffers={len(context_rows)} " + " ".join(context_parts)
            )

    append_extra_note_row_summary(lines, rows, sample_limit)
    append_expected_row_coverage(lines, rows, sample_limit)
    append_row_confusion_pitch_summary(lines, rows, sample_limit)
    append_detailed_breakdown(lines, rows, samples, detail_limit, sample_limit)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=0,
        help="print this many non-hit pitch and octave buckets plus per-source attribute summaries",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=0,
        help="print this many individual non-hit sample attribute summaries",
    )
    parser.add_argument(
        "--min-visible-lit-exact-sample-percent",
        type=float,
        default=None,
        help="fail when visible expected-row exact-note sample coverage is below this percent",
    )
    parser.add_argument(
        "--min-visible-lit-exact-family-sample-percent",
        action="append",
        type=parse_percent_spec,
        default=[],
        metavar="FAMILY=PERCENT",
        help="fail when a family's visible expected-row exact-note sample coverage is below this percent",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="only run validation checks instead of printing the full summary",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    rows = load_rows(path)
    failures = validate_visible_lit_exact_samples(
        rows,
        min_sample_percent=args.min_visible_lit_exact_sample_percent,
        min_family_sample_percent=args.min_visible_lit_exact_family_sample_percent,
    )

    if not args.check_only:
        for line in summarize(
            path,
            detail_limit=max(0, args.detail_limit),
            sample_limit=max(0, args.sample_limit),
        ):
            print(line)

    if failures:
        for failure in failures:
            print(f"summarize_real_note_attributes: {failure}", file=sys.stderr)
        return 1

    if args.check_only:
        print("summarize_real_note_attributes: visual strength checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
