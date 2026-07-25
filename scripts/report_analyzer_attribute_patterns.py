#!/usr/bin/env python3
"""Print a compact pattern report from analyzer attribute row dumps."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics


NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")
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
DRUMS = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def float_or(row: dict[str, str], field: str, default: float) -> float:
    value = as_float(row, field)
    return default if value is None else value


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def compact(counter: collections.Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def unique_sample_count(rows: list[dict[str, str]], field: str) -> int:
    return len({row.get(field, "") for row in rows if row.get(field, "")})


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def debug_pitch_delta(row: dict[str, str], midi_field: str, debug_field: str = "debug_midi") -> int | None:
    direct_delta = parse_int(row.get("debug_delta", ""))
    if direct_delta is not None:
        return direct_delta
    direct_delta = parse_int(row.get("nearest_debug_delta", ""))
    if direct_delta is not None:
        return direct_delta
    expected = parse_int(row.get(midi_field, ""))
    actual = parse_int(row.get(debug_field, ""))
    if actual is None and row.get("debug_note", ""):
        actual = midi_from_note(row["debug_note"])
    if expected is None or actual is None:
        return None
    return actual - expected


def display_pitch_delta(row: dict[str, str], midi_field: str) -> int | None:
    direct_delta = parse_int(row.get("display_delta", ""))
    if direct_delta is not None:
        return direct_delta
    expected = parse_int(row.get(midi_field, ""))
    actual = parse_int(row.get("display_midi", ""))
    if actual is None and row.get("display_note", ""):
        actual = midi_from_note(row["display_note"])
    if expected is None or actual is None:
        return None
    return actual - expected


def primary_pitch_delta(row: dict[str, str], midi_field: str) -> int | None:
    direct_delta = parse_int(row.get("primary_delta", ""))
    if direct_delta is not None:
        return direct_delta
    expected = parse_int(row.get(midi_field, ""))
    actual = parse_int(row.get("primary_midi", ""))
    if actual is None and row.get("primary_note", ""):
        actual = midi_from_note(row["primary_note"])
    if expected is None or actual is None:
        return None
    return actual - expected


def pitch_quality(delta: int | None) -> str:
    if delta is None:
        return "unknown"
    if delta == 0:
        return "exact"
    if delta % 12 == 0:
        return "octave_alias"
    return "other_pitch"


def pitch_quality_counts(rows: list[dict[str, str]], midi_field: str, debug_field: str = "debug_midi") -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        counts[pitch_quality(debug_pitch_delta(row, midi_field, debug_field))] += 1
    return counts


def display_pitch_quality_counts(rows: list[dict[str, str]], midi_field: str) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        counts[pitch_quality(display_pitch_delta(row, midi_field))] += 1
    return counts


def primary_pitch_quality_counts(rows: list[dict[str, str]], midi_field: str) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        counts[pitch_quality(primary_pitch_delta(row, midi_field))] += 1
    return counts


def note_cell_midis(value: str) -> list[int]:
    midis: list[int] = []
    seen: set[int] = set()
    for part in (value or "").split(","):
        note = part.split(":", 1)[0].strip()
        if not note or note == "--":
            continue
        midi = midi_from_note(note)
        if midi is None or midi in seen:
            continue
        seen.add(midi)
        midis.append(midi)
    return midis


def octave_duplicate_count(midis: list[int]) -> int:
    by_pitch_class: dict[int, set[int]] = collections.defaultdict(set)
    for midi in midis:
        by_pitch_class[midi % 12].add(midi)
    return sum(1 for values in by_pitch_class.values() if len(values) > 1)


def target_note_field(family: str) -> str:
    if family == "bass":
        return "bass_notes"
    if family == "guitar":
        return "guitar_notes"
    if family == "piano":
        return "piano_notes"
    if family == "vocals":
        return "vocal_notes"
    return "other_notes"


def target_octave_duplicate_count(row: dict[str, str], family_field: str = "family") -> int:
    return octave_duplicate_count(note_cell_midis(row.get(target_note_field(row.get(family_field, "")), "")))


def target_octave_duplicate_counts(rows: list[dict[str, str]], family_field: str = "family") -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        duplicate_count = target_octave_duplicate_count(row, family_field)
        if duplicate_count > 0:
            counts[f"{row.get(family_field, 'unknown')}:dup{duplicate_count}"] += 1
    return counts


def ratio(count: int, total: int) -> str:
    if total <= 0:
        return "0/0"
    return f"{count}/{total} ({count * 100.0 / total:.1f}%)"


def median(values: list[float]) -> str:
    if not values:
        return "--"
    return f"{statistics.median(values):.3f}".rstrip("0").rstrip(".")


def signed_median(values: list[float]) -> str:
    if not values:
        return "--"
    value = statistics.median(values)
    return f"{value:+.3f}".rstrip("0").rstrip(".")


def short_path(value: str, max_parts: int = 3) -> str:
    if not value:
        return "--"
    parts = pathlib.PurePath(value).parts
    if len(parts) <= max_parts:
        return value
    return "/".join(parts[-max_parts:])


def num(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "--"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def cell(row: dict[str, str], field: str, default: str = "--") -> str:
    value = row.get(field, "")
    return value if value else default


def level_cells(row: dict[str, str], fields: tuple[str, ...]) -> str:
    return ",".join(f"{field.removesuffix('_level')}:{num(row, field)}" for field in fields)


def score_cells(row: dict[str, str]) -> str:
    return ",".join(
        f"{label}:{num(row, field)}"
        for label, field in (
            ("bass", "bass_score"),
            ("key", "keyboard_score"),
            ("gtr", "guitar_score"),
            ("voc", "vocal_score"),
            ("oth", "other_score"),
        )
    )


def trigger_cells(row: dict[str, str]) -> str:
	parts = []
	for drum in DRUMS:
		parts.append(f"{drum}:{num(row, drum + '_trigger')}/{num(row, drum + '_threshold')}")
	return ",".join(parts)


def trigger_ratio(row: dict[str, str], drum: str) -> float | None:
	trigger = as_float(row, f"{drum}_trigger")
	threshold = as_float(row, f"{drum}_threshold")
	if trigger is None or threshold is None:
		return None
	return trigger / (threshold + 1.0e-6)


def drum_level_margin(row: dict[str, str], expected: str, got: str) -> float | None:
	if expected not in DRUMS or got not in DRUMS:
		return None
	expected_level = as_float(row, f"{expected}_level")
	got_level = as_float(row, f"{got}_level")
	if expected_level is None or got_level is None:
		return None
	return got_level - expected_level


def drum_trigger_ratio_margin(row: dict[str, str], expected: str, got: str) -> float | None:
	if expected not in DRUMS or got not in DRUMS:
		return None
	expected_ratio = trigger_ratio(row, expected)
	got_ratio = trigger_ratio(row, got)
	if expected_ratio is None or got_ratio is None:
		return None
	return got_ratio - expected_ratio


def representative_rows(
    rows: list[dict[str, str]],
    group_fields: tuple[str, ...],
    limit: int,
    *,
    prefer_non_hit: bool = True,
) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    ordered = sorted(
        rows,
        key=lambda row: (
            (row.get("status", "") == "hit") if prefer_non_hit else False,
            *(row.get(field, "") for field in group_fields),
            cell(row, "sample_id"),
            cell(row, "recording_id"),
            cell(row, "sample"),
            cell(row, "path"),
        ),
    )
    selected: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for row in ordered:
        key = tuple(row.get(field, "") for field in group_fields)
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def section(title: str) -> None:
    print()
    print(title)


def report_instruments(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("kind") == "note"]
    section("instrument sample attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(f"  note rows={len(rows)}")
    family_counts = collections.Counter(row.get("family", "unknown") for row in rows)
    print(f"  families {compact(family_counts, limit)}")
    print(f"  pitch quality {compact(pitch_quality_counts(rows, 'midi'), limit)}")
    print(f"  display pitch quality {compact(display_pitch_quality_counts(rows, 'midi'), limit)}")
    print(f"  primary pitch quality {compact(primary_pitch_quality_counts(rows, 'midi'), limit)}")
    print(f"  target octave duplicates {compact(target_octave_duplicate_counts(rows), limit)}")
    non_hit_rows = [row for row in rows if row.get("status") != "hit"]
    if non_hit_rows:
        print(f"  miss reasons {compact(collections.Counter(row.get('miss_reason', '--') or '--' for row in non_hit_rows), limit)}")
    for family, _count in family_counts.most_common(limit):
        family_rows = [row for row in rows if row.get("family") == family]
        owners = collections.Counter(row.get("debug_owner", "none") or "none" for row in family_rows)
        raw_rank1 = sum(1 for row in family_rows if float_or(row, "raw_expected_rank", 99.0) <= 1.0)
        tuned = sum(1 for row in family_rows if float_or(row, "raw_tuned_abs_cent_offset", 99.0) <= 9.0)
        print(
            f"  {family}: rows={len(family_rows)} owners={compact(owners, 5)} "
            f"pitch={compact(pitch_quality_counts(family_rows, 'midi'), 4)} "
            f"display={compact(display_pitch_quality_counts(family_rows, 'midi'), 4)} "
            f"primary={compact(primary_pitch_quality_counts(family_rows, 'midi'), 4)} "
            f"octdup={compact(collections.Counter(str(target_octave_duplicate_count(row)) for row in family_rows), 4)} "
            f"raw_rank1={ratio(raw_rank1, len(family_rows))} tuned<=9c={ratio(tuned, len(family_rows))}"
        )
    examples = representative_rows(rows, ("status", "family", "debug_owner"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} {cell(row, 'family')} "
                f"expected={cell(row, 'note')}/{cell(row, 'midi')} "
                f"display={cell(row, 'display_note')}/{cell(row, 'display_delta')} "
                f"primary={cell(row, 'primary_note')}/{cell(row, 'primary_delta')} "
                f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
                f"nearest={cell(row, 'nearest_debug_note')}/{cell(row, 'nearest_debug_delta')} "
                f"reason={cell(row, 'miss_reason')} "
                f"octdup={target_octave_duplicate_count(row)} "
                f"notes=b[{cell(row, 'bass_notes')}] g[{cell(row, 'guitar_notes')}] "
                f"k[{cell(row, 'piano_notes')}] v[{cell(row, 'vocal_notes')}] "
                f"o[{cell(row, 'other_notes')}] a[{cell(row, 'amb_notes')}] "
                f"debug_count={num(row, 'debug_count')} candidates={cell(row, 'debug_candidates')} "
                f"levels={level_cells(row, ('bass_level', 'piano_level', 'guitar_level', 'vocal_level', 'other_level', 'amb_level'))} "
                f"raw_ratio={num(row, 'raw_expected_ratio')} tuned_ratio={num(row, 'raw_tuned_ratio')} "
                f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
                f"scores={score_cells(row)} file={short_path(cell(row, 'path', ''))}"
            )


def real_note_bucket(row: dict[str, str]) -> str:
    return (
        f"{row.get('status', '')}:{row.get('family', '')}/"
        f"{row.get('source', '')}->{row.get('first_row', '')}"
    )


def report_real_notes(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample_id")]
    section("real-note full-mix attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    by_sample_status: dict[str, str] = {}
    for row in rows:
        by_sample_status.setdefault(row["sample_id"], row.get("status", "unknown"))
    print(f"  rows={len(rows)} samples={len(by_sample_status)} status={compact(collections.Counter(by_sample_status.values()), limit)}")
    print(f"  row pitch quality {compact(pitch_quality_counts(rows, 'expected_midi'), limit)}")
    miss_rows = [row for row in rows if row.get("status") == "ownership_miss" and row.get("debug_note")]
    print(f"  ownership miss rows={len(miss_rows)} samples={unique_sample_count(miss_rows, 'sample_id')}")
    if miss_rows:
        print(f"  miss reasons {compact(collections.Counter(row.get('miss_reason', '--') or '--' for row in miss_rows), limit)}")
    raw_rank1 = sum(1 for row in miss_rows if float_or(row, "raw_expected_rank", 99.0) <= 1.0)
    raw_strong = sum(1 for row in miss_rows if float_or(row, "raw_expected_ratio", 0.0) >= 0.90)
    tuned = sum(1 for row in miss_rows if float_or(row, "raw_tuned_abs_cent_offset", 99.0) <= 9.0)
    print(
        f"  miss raw evidence raw_rank1={ratio(raw_rank1, len(miss_rows))} "
        f"raw_ratio>=0.90={ratio(raw_strong, len(miss_rows))} tuned<=9c={ratio(tuned, len(miss_rows))}"
    )
    deltas: collections.Counter[str] = collections.Counter()
    for row in miss_rows:
        expected = as_float(row, "expected_midi")
        debug_midi = midi_from_note(row.get("debug_note", ""))
        if expected is None or debug_midi is None:
            continue
        deltas[str(int(debug_midi - expected))] += 1
    print(f"  debug-midi deltas {compact(deltas, limit)}")
    bucket_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in miss_rows:
        bucket_rows[real_note_bucket(row)].append(row)
    for bucket, bucket_group in sorted(bucket_rows.items(), key=lambda item: (-len(item[1]), item[0]))[:limit]:
        print(
            f"  {bucket}: rows={len(bucket_group)} samples={unique_sample_count(bucket_group, 'sample_id')} "
            f"debug_owner={compact(collections.Counter(row.get('debug_owner', 'none') or 'none' for row in bucket_group), 4)} "
            f"strongest={compact(collections.Counter(row.get('buffer_strongest_row', 'none') or 'none' for row in bucket_group), 4)} "
            f"raw_best={compact(collections.Counter(row.get('raw_local_best_note', '') for row in bucket_group), 4)}"
        )
    examples = representative_rows(rows, ("status", "family", "source", "first_row", "debug_owner"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} {cell(row, 'family')}/{cell(row, 'source')} "
                f"expected={cell(row, 'expected_note')}/{cell(row, 'expected_midi')} "
                f"first={cell(row, 'first_row')} buffer={cell(row, 'buffer')} "
                f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
                f"delta={cell(row, 'debug_delta')} reason={cell(row, 'miss_reason')} "
                f"levels={level_cells(row, ('bass_level', 'guitar_level', 'piano_level', 'vocal_level', 'other_level', 'amb_level'))} "
                f"raw={num(row, 'raw_expected_ratio')}/{num(row, 'raw_tuned_ratio')} "
                f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
                f"notes=b[{cell(row, 'bass_notes')}] g[{cell(row, 'guitar_notes')}] "
                f"k[{cell(row, 'piano_notes')}] v[{cell(row, 'vocal_notes')}] "
                f"o[{cell(row, 'other_notes')}] a[{cell(row, 'amb_notes')}] "
                f"scores={score_cells(row)} sample={cell(row, 'sample_id')}"
            )


def split_list_cell(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [item for item in value.split(",") if item]


def split_label_cell(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [item for item in re.split(r"[=/]", value) if item and item != "--"]


def label_cell_has_any(value: str, expected: list[str]) -> bool:
    if not expected:
        return False
    labels = set(split_label_cell(value))
    return any(label in labels for label in expected)


def guitar_full_tone_label_gaps(
    rows: list[dict[str, str]], missing_field: str, label_field: str
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for row in rows:
        if row.get(missing_field, "") != "--":
            continue
        expected = split_label_cell(row.get("expected_chords", ""))
        if not label_cell_has_any(row.get(label_field, ""), expected):
            gaps.append(row)
    return gaps


def report_guitar_chords(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("recording_id")]
    section("guitar chord attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(f"  rows={len(rows)} recordings={unique_sample_count(rows, 'recording_id')} status={compact(collections.Counter(row.get('status', 'unknown') for row in rows), limit)}")
    miss_rows = [row for row in rows if row.get("status") == "chord_miss"]
    print(f"  chord miss rows={len(miss_rows)} recordings={unique_sample_count(miss_rows, 'recording_id')}")
    print(f"  miss support {compact(collections.Counter(row.get('support', '') for row in miss_rows), limit)}")
    print(
        f"  miss match kinds {compact(collections.Counter(row.get('guitar_match_kind', '--') or '--' for row in miss_rows), limit)}"
    )
    print(
        f"  miss evidence classes {compact(collections.Counter(row.get('evidence_class', '--') or '--' for row in miss_rows), limit)}"
    )
    print(
        f"  miss evidence sources {compact(collections.Counter(row.get('evidence_source', '--') or '--' for row in miss_rows), limit)}"
    )
    tone_counts: collections.Counter[str] = collections.Counter()
    for row in miss_rows:
        for field in ("visible_missing_tones", "analysis_missing_tones", "smooth_missing_tones"):
            for tone in split_list_cell(row.get(field, "")):
                tone_counts[tone] += 1
    print(f"  missing tones {compact(tone_counts, limit)}")
    full_tone_gaps = {
        "visible": guitar_full_tone_label_gaps(miss_rows, "visible_missing_tones", "guitar_chord"),
        "analysis": guitar_full_tone_label_gaps(miss_rows, "analysis_missing_tones", "guitar_raw_chord"),
        "smoothed": guitar_full_tone_label_gaps(miss_rows, "smooth_missing_tones", "guitar_smoothed_chord"),
    }
    raw_or_smoothed_expected = [
        row
        for row in miss_rows
        if label_cell_has_any(row.get("guitar_raw_chord", ""), split_label_cell(row.get("expected_chords", "")))
        or label_cell_has_any(row.get("guitar_smoothed_chord", ""), split_label_cell(row.get("expected_chords", "")))
    ]
    print(
        "  full-tone expected-label gaps "
        + " ".join(
            f"{name}={len(gaps)}/{unique_sample_count(gaps, 'recording_id')}"
            for name, gaps in full_tone_gaps.items()
        )
        + f" raw_or_smoothed_expected={len(raw_or_smoothed_expected)}/"
        f"{unique_sample_count(raw_or_smoothed_expected, 'recording_id')}"
    )
    print(
        "  raw tone medians "
        f"root={median([value for row in miss_rows if (value := as_float(row, 'raw_root')) is not None])} "
        f"third={median([value for row in miss_rows if (value := as_float(row, 'raw_third')) is not None])} "
        f"fifth={median([value for row in miss_rows if (value := as_float(row, 'raw_fifth')) is not None])} "
        f"third_anchor={median([value for row in miss_rows if (value := as_float(row, 'raw_third_anchor_ratio')) is not None])} "
        f"third_margin={median([value for row in miss_rows if (value := as_float(row, 'raw_third_opposite_margin')) is not None])}"
    )
    support_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in miss_rows:
        support_rows[f"{row.get('status', '')}:{row.get('quality', '')}:{row.get('support', '')}"].append(row)
    for bucket, bucket_group in sorted(support_rows.items(), key=lambda item: (-len(item[1]), item[0]))[:limit]:
        print(
            f"  {bucket}: rows={len(bucket_group)} recs={unique_sample_count(bucket_group, 'recording_id')} "
            f"expected={compact(collections.Counter(row.get('expected_chords', '') for row in bucket_group), 5)} "
            f"pred={compact(collections.Counter(row.get('guitar_chord', '') for row in bucket_group), 5)} "
            f"match={compact(collections.Counter(row.get('guitar_match_kind', '--') or '--' for row in bucket_group), 5)} "
            f"evidence={compact(collections.Counter(row.get('evidence_class', '--') or '--' for row in bucket_group), 5)} "
            f"raw={compact(collections.Counter(row.get('guitar_raw_chord', '') for row in bucket_group), 5)} "
            f"smooth={compact(collections.Counter(row.get('guitar_smoothed_chord', '') for row in bucket_group), 5)}"
        )
    gap_examples: list[tuple[str, dict[str, str]]] = []
    seen_gap_examples: set[tuple[str, str]] = set()
    for name, gaps in full_tone_gaps.items():
        for row in representative_rows(gaps, ("quality", "support", "expected_chords"), row_examples):
            key = (name, row.get("recording_id", ""))
            if key in seen_gap_examples:
                continue
            seen_gap_examples.add(key)
            gap_examples.append((name, row))
    if gap_examples:
        print("  full-tone expected-label gap examples")
        for name, row in gap_examples[: max(0, row_examples)]:
            print(
                f"    {name} expected={cell(row, 'expected_chords')} got={cell(row, 'guitar_chord')} "
                f"raw={cell(row, 'guitar_raw_chord')} smooth={cell(row, 'guitar_smoothed_chord')} "
                f"pc={cell(row, 'guitar_pitch_classes')} analysis_pc={cell(row, 'guitar_analysis_pitch_classes')} "
                f"smooth_pc={cell(row, 'guitar_smoothed_pitch_classes')} "
                f"missing=v:{cell(row, 'visible_missing_tones')} a:{cell(row, 'analysis_missing_tones')} "
                f"s:{cell(row, 'smooth_missing_tones')} "
                f"match={cell(row, 'guitar_match_kind')} "
                f"evidence={cell(row, 'evidence_class')}/{cell(row, 'evidence_source')} "
                f"third_anchor={num(row, 'raw_third_anchor_ratio')} "
                f"third_margin={num(row, 'raw_third_opposite_margin')} "
                f"quality_raw={cell(row, 'quality_raw', cell(row, 'expected_quality_raw_profile'))} "
                f"rec={cell(row, 'recording_id')}"
            )
    examples = representative_rows(rows, ("status", "quality", "support"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} quality={cell(row, 'quality')} "
                f"expected={cell(row, 'expected_chords')} got={cell(row, 'guitar_chord')} "
                f"raw={cell(row, 'guitar_raw_chord')} smooth={cell(row, 'guitar_smoothed_chord')} "
                f"pc={cell(row, 'guitar_pitch_classes')} analysis_pc={cell(row, 'guitar_analysis_pitch_classes')} "
                f"smooth_pc={cell(row, 'guitar_smoothed_pitch_classes')} "
                f"missing=v:{cell(row, 'visible_missing_tones')} a:{cell(row, 'analysis_missing_tones')} s:{cell(row, 'smooth_missing_tones')} "
                f"tones=root:{num(row, 'raw_root')} third:{num(row, 'raw_third')} fifth:{num(row, 'raw_fifth')} "
                f"match={cell(row, 'guitar_match_kind')} "
                f"evidence={cell(row, 'evidence_class')}/{cell(row, 'evidence_source')} "
                f"third_anchor={num(row, 'raw_third_anchor_ratio')} "
                f"third_margin={num(row, 'raw_third_opposite_margin')} "
                f"quality_raw={cell(row, 'quality_raw', cell(row, 'expected_quality_raw_profile'))} "
                f"rms={num(row, 'rms')} rec={cell(row, 'recording_id')}"
            )


def report_drums(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample")]
    section("drum primary attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    routes = collections.Counter(f"{row.get('expected', '')}->{row.get('got', '')}" for row in rows)
    print(f"  rows={len(rows)} routes={compact(routes, limit)}")
    for route, _count in routes.most_common(limit):
        expected, got = route.split("->", 1)
        route_rows = [row for row in rows if row.get("expected") == expected and row.get("got") == got]
        expected_levels = [
            value for row in route_rows if (value := as_float(row, f"{expected}_level")) is not None
        ]
        got_levels = [value for row in route_rows if (value := as_float(row, f"{got}_level")) is not None]
        level_margins = [
            value
            for row in route_rows
            if (value := drum_level_margin(row, expected, got)) is not None
        ]
        trigger_ratio_margins = [
            value
            for row in route_rows
            if (value := drum_trigger_ratio_margin(row, expected, got)) is not None
        ]
        active = sum(1 for value in expected_levels if value > 0.30)
        print(
            f"  {route}: rows={len(route_rows)} expected_level_med={median(expected_levels)} "
            f"got_level_med={median(got_levels)} level_margin_med={signed_median(level_margins)} "
            f"trigger_ratio_margin_med={signed_median(trigger_ratio_margins)} "
            f"expected_active={ratio(active, len(route_rows))} "
            f"body_shape={compact(collections.Counter(row.get('body_shape', '') or '--' for row in route_rows), 4)} "
            f"energy_med={median([value for row in route_rows if (value := as_float(row, 'energy_low')) is not None])}/"
            f"{median([value for row in route_rows if (value := as_float(row, 'energy_mid')) is not None])}/"
            f"{median([value for row in route_rows if (value := as_float(row, 'energy_high')) is not None])}"
        )
    examples = representative_rows(rows, ("expected", "got"), row_examples, prefer_non_hit=False)
    if examples:
        print("  representative detected rows")
        for row in examples:
            expected = row.get("expected", "")
            got = row.get("got", "")
            level_margin = drum_level_margin(row, expected, got)
            trigger_margin = drum_trigger_ratio_margin(row, expected, got)
            print(
                f"    {cell(row, 'expected')}->{cell(row, 'got')} "
                f"energy={num(row, 'energy_low')}/{num(row, 'energy_mid')}/{num(row, 'energy_high')} "
                f"body={num(row, 'kick_body')}/{num(row, 'snare_body')}/{num(row, 'tom_body')} "
                f"crack={num(row, 'snare_crack')} upper_tom={num(row, 'upper_tom_body')} "
                f"level_margin={signed_median([level_margin] if level_margin is not None else [])} "
                f"trigger_ratio_margin={signed_median([trigger_margin] if trigger_margin is not None else [])} "
                f"levels={level_cells(row, tuple(f'{drum}_level' for drum in DRUMS))} "
                f"triggers={trigger_cells(row)} "
                f"sample={short_path(cell(row, 'sample', ''))}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument", type=pathlib.Path, default=pathlib.Path("build/instrument_detected_attribute_rows.tsv"))
    parser.add_argument("--real-note", type=pathlib.Path, default=pathlib.Path("build/real_note_detected_attribute_rows.tsv"))
    parser.add_argument("--guitar-chord", type=pathlib.Path, default=pathlib.Path("build/guitar_chord_detected_attribute_rows.tsv"))
    parser.add_argument("--drum", type=pathlib.Path, default=pathlib.Path("build/drum_primary_miss_attribute_rows.tsv"))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument(
        "--row-examples",
        type=int,
        default=4,
        help="print representative row-level detector attributes per section",
    )
    args = parser.parse_args()

    limit = max(1, args.limit)
    row_examples = max(0, args.row_examples)
    report_instruments(args.instrument, limit, row_examples)
    report_real_notes(args.real_note, limit, row_examples)
    report_guitar_chords(args.guitar_chord, limit, row_examples)
    report_drums(args.drum, limit, row_examples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
