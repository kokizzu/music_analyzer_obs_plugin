#!/usr/bin/env python3
"""Summarize real-note per-buffer detector attribute TSV exports."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics

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
    "partial2",
    "partial3",
    "partial4",
    "partial5",
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


def note_row_levels(row: dict[str, str], row_name: str, target_midi: int) -> tuple[float, float, int | None]:
    field = ALL_ROW_NOTE_FIELDS.get(row_name)
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
    args = parser.parse_args()

    for line in summarize(
        pathlib.Path(args.path),
        detail_limit=max(0, args.detail_limit),
        sample_limit=max(0, args.sample_limit),
    ):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
