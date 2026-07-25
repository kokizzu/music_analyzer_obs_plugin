#!/usr/bin/env python3
"""Print compact measured detector attributes from analyzer TSV row dumps."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re


DRUMS = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
NOTE_ORDER = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
NOTE_BASE = {note: index for index, note in enumerate(NOTE_ORDER)}
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def cell(row: dict[str, str], field: str, default: str = "--") -> str:
    value = row.get(field, "")
    return value if value else default


def num(row: dict[str, str], field: str) -> str:
    value = row.get(field, "")
    if value == "":
        return "--"
    try:
        parsed = float(value)
    except ValueError:
        return value
    return f"{parsed:.3f}".rstrip("0").rstrip(".")


def compact(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def percent(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "--"
    return f"{(100.0 * numerator / denominator):.1f}%"


def midi_note_name(midi: int) -> str:
    return f"{NOTE_ORDER[midi % 12]}{midi // 12 - 1}"


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def midi_range(rows: list[dict[str, str]], field: str) -> str:
    values = [parsed for row in rows if (parsed := parse_int(row.get(field, ""))) is not None]
    if not values:
        return "--"
    low = min(values)
    high = max(values)
    if low == high:
        return f"{midi_note_name(low)}/{low}"
    return f"{midi_note_name(low)}-{midi_note_name(high)}/{low}-{high}"


def expected_debug_owner(family: str) -> str:
    if family == "piano":
        return "piano"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth", "other"}:
        return "other"
    return family


def owner_mismatches(rows: list[dict[str, str]], family_field: str) -> collections.Counter[str]:
    mismatches: collections.Counter[str] = collections.Counter()
    for row in rows:
        family = row.get(family_field, "")
        owner = row.get("debug_owner", "")
        if not family or not owner:
            continue
        expected = expected_debug_owner(family)
        if owner != expected:
            mismatches[f"{family}->{owner}"] += 1
    return mismatches


def debug_pitch_deltas(rows: list[dict[str, str]], midi_field: str, debug_field: str = "debug_midi") -> collections.Counter[str]:
    deltas: collections.Counter[str] = collections.Counter()
    for row in rows:
        if (direct_delta := debug_pitch_delta(row, midi_field, debug_field)) is not None:
            deltas[f"{direct_delta:+d}"] += 1
            continue

        expected = parse_int(row.get(midi_field, ""))
        actual = parse_int(row.get(debug_field, ""))
        if expected is None or actual is None:
            continue
        delta = actual - expected
        deltas[f"{delta:+d}"] += 1
    return deltas


def debug_pitch_delta(row: dict[str, str], midi_field: str, debug_field: str = "debug_midi") -> int | None:
    direct_delta = parse_int(row.get("debug_delta", ""))
    if direct_delta is not None:
        return direct_delta
    direct_delta = parse_int(row.get("nearest_debug_delta", ""))
    if direct_delta is not None:
        return direct_delta
    expected = parse_int(row.get(midi_field, ""))
    actual = parse_int(row.get(debug_field, ""))
    if expected is None or actual is None:
        return None
    return actual - expected


def display_pitch_delta(row: dict[str, str], midi_field: str) -> int | None:
    direct_delta = parse_int(row.get("display_delta", ""))
    if direct_delta is not None:
        return direct_delta
    expected = parse_int(row.get(midi_field, ""))
    actual = parse_int(row.get("display_midi", ""))
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


def octave_alias_buckets(
    rows: list[dict[str, str]],
    *,
    midi_field: str,
    expected_note_field: str,
    detected_note_field: str,
    source_field: str,
    delta_func,
) -> collections.Counter[tuple[str, str, str, str, str, str, str]]:
    buckets: collections.Counter[tuple[str, str, str, str, str, str, str]] = collections.Counter()
    for row in rows:
        delta = delta_func(row)
        if pitch_quality(delta) != "octave_alias":
            continue
        expected_midi = cell(row, midi_field)
        expected_note = cell(row, expected_note_field)
        detected_note = cell(row, detected_note_field)
        buckets[
            (
                cell(row, "family", "unknown"),
                cell(row, source_field, "--"),
                f"{expected_note}/{expected_midi}",
                detected_note,
                f"{delta:+d}" if delta is not None else "--",
                cell(row, "status", "unknown"),
                cell(row, "debug_owner", "--"),
            )
        ] += 1
    return buckets


def print_octave_alias_buckets(
    title: str,
    buckets: collections.Counter[tuple[str, str, str, str, str, str, str]],
    row_limit: int,
) -> None:
    if not buckets:
        print(f"  {title}=--")
        return

    limit = len(buckets) if row_limit == 0 else max(0, row_limit)
    print(f"  {title}:")
    for (family, source, expected, detected, delta, status, owner), count in buckets.most_common(limit):
        print(
            f"    {count} {family}/{source} expected={expected} "
            f"detected={detected}/{delta} status={status} owner={owner}"
        )


def midi_from_note_label(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def note_cell_midis(value: str) -> list[int]:
    midis: list[int] = []
    seen: set[int] = set()
    for part in (value or "").split(","):
        note = part.split(":", 1)[0].strip()
        if not note or note == "--":
            continue
        midi = midi_from_note_label(note)
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


def note_count(rows: list[dict[str, str]], midi_field: str, note_field: str) -> int:
	midi_values = {row.get(midi_field, "") for row in rows if row.get(midi_field, "")}
	if midi_values:
		return len(midi_values)
	return len({row.get(note_field, "") for row in rows if row.get(note_field, "")})


def status_fraction(rows: list[dict[str, str]], hit_value: str) -> str:
    hits = sum(1 for row in rows if row.get("status") == hit_value)
    return f"{hits}/{len(rows)} {percent(hits, len(rows))}"


def short_path(value: str, max_parts: int = 3) -> str:
    if not value:
        return "--"
    parts = pathlib.PurePath(value).parts
    if len(parts) <= max_parts:
        return value
    return "/".join(parts[-max_parts:])


def split_chord_labels(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [label for label in re.split(r"[=/]", value) if label and label != "--"]


def limited_rows(rows: list[dict[str, str]], limit: int, hit_values: set[str]) -> list[dict[str, str]]:
    if limit == 0:
        return rows
    ordered = sorted(
        rows,
        key=lambda row: (
            row.get("status", "") in hit_values,
            row.get("family", ""),
            row.get("source", ""),
            row.get("expected", ""),
            row.get("expected_chords", ""),
            row.get("sample_id", ""),
            row.get("recording_id", ""),
            row.get("path", ""),
            row.get("sample", ""),
        ),
    )
    return ordered[: max(0, limit)]


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


def note_cells(row: dict[str, str]) -> str:
    fields = (
        ("bass", "bass_notes"),
        ("gtr", "guitar_notes"),
        ("key", "piano_notes"),
        ("voc", "vocal_notes"),
        ("oth", "other_notes"),
        ("amb", "amb_notes"),
    )
    visible = [(label, cell(row, field, "")) for label, field in fields if row.get(field, "")]
    if not visible:
        return "--"
    return " ".join(f"{label}[{value}]" for label, value in visible)


def section(title: str) -> None:
    print()
    print(title)


def report_instrument_rows(path: pathlib.Path, row_limit: int) -> None:
    rows = [row for row in load_rows(path) if row.get("kind") == "note"]
    section("measured generated instrument note rows")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(
        f"  rows={len(rows)} status={compact(collections.Counter(row.get('status', 'unknown') for row in rows))} "
        f"families={compact(collections.Counter(row.get('family', 'unknown') for row in rows))}"
    )
    print(
        f"  miss reasons={compact(collections.Counter(cell(row, 'miss_reason') for row in rows if row.get('status') != 'hit'))}"
    )
    print(f"  debug owner mismatches={compact(owner_mismatches(rows, 'family'))}")
    print(f"  debug pitch deltas={compact(debug_pitch_deltas(rows, 'midi'))}")
    print(f"  pitch quality={compact(pitch_quality_counts(rows, 'midi'))}")
    print(f"  display pitch quality={compact(display_pitch_quality_counts(rows, 'midi'))}")
    print(f"  target octave duplicates={compact(target_octave_duplicate_counts(rows))}")
    print_octave_alias_buckets(
        "display octave alias buckets",
        octave_alias_buckets(
            rows,
            midi_field="midi",
            expected_note_field="note",
            detected_note_field="display_note",
            source_field="program_name",
            delta_func=lambda row: display_pitch_delta(row, "midi"),
        ),
        row_limit,
    )
    print("  family ranges:")
    for family in sorted({row.get("family", "unknown") for row in rows}):
        family_rows = [row for row in rows if row.get("family", "unknown") == family]
        print(
            f"    {family} rows={len(family_rows)} notes={note_count(family_rows, 'midi', 'note')} "
            f"range={midi_range(family_rows, 'midi')} hit={status_fraction(family_rows, 'hit')} "
            f"pitch={compact(pitch_quality_counts(family_rows, 'midi'), 4)} "
            f"display={compact(display_pitch_quality_counts(family_rows, 'midi'), 4)} "
            f"octdup={compact(collections.Counter(str(target_octave_duplicate_count(row)) for row in family_rows), 4)}"
        )
    for row in limited_rows(rows, row_limit, {"hit"}):
        print(
            f"    {cell(row, 'status')} {cell(row, 'family')} "
            f"expected={cell(row, 'note')}/{cell(row, 'midi')} "
            f"display={cell(row, 'display_note')}/{cell(row, 'display_delta')} "
            f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
            f"nearest={cell(row, 'nearest_debug_note')}/{cell(row, 'nearest_debug_delta')} "
            f"reason={cell(row, 'miss_reason')} "
            f"octdup={target_octave_duplicate_count(row)} "
            f"levels={level_cells(row, ('bass_level', 'piano_level', 'guitar_level', 'vocal_level', 'other_level', 'amb_level'))} "
            f"raw={num(row, 'raw_expected_ratio')}/{num(row, 'raw_tuned_ratio')} "
            f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
            f"scores={score_cells(row)} pitch={num(row, 'pitch_confidence')} "
            f"periodic={num(row, 'periodicity')} fit={num(row, 'fit_error')} "
            f"file={short_path(cell(row, 'path', ''))}"
        )


def report_real_note_rows(path: pathlib.Path, row_limit: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample_id")]
    section("measured real-note full-mix rows")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(
        f"  rows={len(rows)} samples={len({row.get('sample_id', '') for row in rows if row.get('sample_id')})} "
        f"status={compact(collections.Counter(row.get('status', 'unknown') for row in rows))}"
    )
    print(
        f"  miss reasons={compact(collections.Counter(cell(row, 'miss_reason') for row in rows if row.get('status') != 'hit'))}"
    )
    print(f"  debug owner mismatches={compact(owner_mismatches(rows, 'family'))}")
    print(f"  debug pitch deltas={compact(debug_pitch_deltas(rows, 'expected_midi'))}")
    print(f"  pitch quality={compact(pitch_quality_counts(rows, 'expected_midi'))}")
    print_octave_alias_buckets(
        "detected octave alias buckets",
        octave_alias_buckets(
            rows,
            midi_field="expected_midi",
            expected_note_field="expected_note",
            detected_note_field="debug_note",
            source_field="source",
            delta_func=lambda row: debug_pitch_delta(row, "expected_midi"),
        ),
        row_limit,
    )
    print("  family ranges:")
    for family in sorted({row.get("family", "unknown") for row in rows}):
        family_rows = [row for row in rows if row.get("family", "unknown") == family]
        samples = {row.get("sample_id", "") for row in family_rows if row.get("sample_id", "")}
        print(
            f"    {family} rows={len(family_rows)} samples={len(samples)} "
            f"notes={note_count(family_rows, 'expected_midi', 'expected_note')} "
            f"range={midi_range(family_rows, 'expected_midi')} hit={status_fraction(family_rows, 'hit')} "
            f"pitch={compact(pitch_quality_counts(family_rows, 'expected_midi'), 4)}"
        )
    for row in limited_rows(rows, row_limit, {"hit"}):
        print(
            f"    {cell(row, 'status')} {cell(row, 'family')}/{cell(row, 'source')} "
            f"expected={cell(row, 'expected_note')}/{cell(row, 'expected_midi')} "
            f"first={cell(row, 'first_row')} buffer={cell(row, 'buffer')} "
            f"row={cell(row, 'row_label')} strongest={cell(row, 'buffer_strongest_row')} "
            f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
            f"delta={cell(row, 'debug_delta')} reason={cell(row, 'miss_reason')} "
            f"levels={level_cells(row, ('bass_level', 'guitar_level', 'piano_level', 'vocal_level', 'other_level', 'amb_level'))} "
            f"raw={num(row, 'raw_expected_ratio')}/{num(row, 'raw_tuned_ratio')} "
            f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
            f"notes={note_cells(row)} "
            f"scores={score_cells(row)} pitch={num(row, 'pitch_confidence')} "
            f"periodic={num(row, 'periodicity')} fit={num(row, 'fit_error')} "
            f"sample={cell(row, 'sample_id')}"
        )


def report_guitar_chord_rows(path: pathlib.Path, row_limit: int) -> None:
    rows = [row for row in load_rows(path) if row.get("recording_id")]
    section("measured guitar chord rows")
    if not rows:
        print(f"  missing rows: {path}")
        return
    false_components: collections.Counter[str] = collections.Counter()
    false_components_on_hits: collections.Counter[str] = collections.Counter()
    for row in rows:
        expected = set(split_chord_labels(cell(row, "expected_chords", "")))
        detected = split_chord_labels(cell(row, "guitar_chord", ""))
        for part in detected:
            if part in expected:
                continue
            false_components[part] += 1
            if row.get("status") == "chord_hit":
                false_components_on_hits[part] += 1
    print(
        f"  rows={len(rows)} recordings={len({row.get('recording_id', '') for row in rows if row.get('recording_id')})} "
        f"status={compact(collections.Counter(row.get('status', 'unknown') for row in rows))} "
        f"quality={compact(collections.Counter(row.get('quality', 'unknown') for row in rows))}"
    )
    print(f"  false chord components={compact(false_components)}")
    print(f"  false components on chord hits={compact(false_components_on_hits)}")
    print(
        "  match kinds="
        f"{compact(collections.Counter(cell(row, 'guitar_match_kind') for row in rows))}"
    )
    miss_rows = [row for row in rows if row.get("status") == "chord_miss"]
    if miss_rows:
        print(
            f"  miss evidence={compact(collections.Counter(cell(row, 'evidence_class') for row in miss_rows))} "
            f"sources={compact(collections.Counter(cell(row, 'evidence_source') for row in miss_rows))}"
        )
        print(
            f"  miss match kinds={compact(collections.Counter(cell(row, 'guitar_match_kind') for row in miss_rows))}"
        )
        print(
            f"  miss visible missing={compact(collections.Counter(cell(row, 'visible_missing_tones') for row in miss_rows))} "
            f"analysis missing={compact(collections.Counter(cell(row, 'analysis_missing_tones') for row in miss_rows))} "
            f"smooth missing={compact(collections.Counter(cell(row, 'smooth_missing_tones') for row in miss_rows))}"
        )
    print("  quality recall:")
    for quality in sorted({row.get("quality", "unknown") for row in rows}):
        quality_rows = [row for row in rows if row.get("quality", "unknown") == quality]
        print(f"    {quality} chord_hit={status_fraction(quality_rows, 'chord_hit')}")
    for row in limited_rows(rows, row_limit, {"chord_hit", "no_chord"}):
        print(
            f"    {cell(row, 'status')} quality={cell(row, 'quality')} "
            f"expected={cell(row, 'expected_chords')} got={cell(row, 'guitar_chord')} "
            f"hits=c/s/g:{cell(row, 'chord_hit')}/{cell(row, 'simple_chord_hit')}/{cell(row, 'guitar_chord_hit')} "
            f"match={cell(row, 'guitar_match_kind')} "
            f"raw={cell(row, 'guitar_raw_chord')} smooth={cell(row, 'guitar_smoothed_chord')} "
            f"pc=e:{cell(row, 'expected_pitch_classes')} v:{cell(row, 'guitar_pitch_classes')} "
            f"a:{cell(row, 'guitar_analysis_pitch_classes')} s:{cell(row, 'guitar_smoothed_pitch_classes')} "
            f"missing=v:{cell(row, 'visible_missing_tones')} a:{cell(row, 'analysis_missing_tones')} "
            f"s:{cell(row, 'smooth_missing_tones')} "
            f"evidence={cell(row, 'evidence_class')}/{cell(row, 'evidence_source')} "
            f"tones=v({num(row, 'visible_root')},{num(row, 'visible_third')},{num(row, 'visible_fifth')}) "
            f"a({num(row, 'analysis_root')},{num(row, 'analysis_third')},{num(row, 'analysis_fifth')}) "
            f"raw({num(row, 'raw_root')},{num(row, 'raw_third')},{num(row, 'raw_fifth')}) "
            f"third_anchor={num(row, 'raw_third_anchor_ratio')} "
            f"third_margin={num(row, 'raw_third_opposite_margin')} "
            f"note_hits={cell(row, 'guitar_note_hits')} fp={cell(row, 'guitar_false_positive_pitch_classes')} "
            f"rms={num(row, 'rms')} rec={cell(row, 'recording_id')}"
        )


def drum_trigger_cells(row: dict[str, str]) -> str:
    return ",".join(f"{drum}:{num(row, drum + '_trigger')}/{num(row, drum + '_threshold')}" for drum in DRUMS)


def report_drum_rows(path: pathlib.Path, title: str, row_limit: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample")]
    section(title)
    if not rows:
        print(f"  missing rows: {path}")
        return
    routes = collections.Counter(f"{row.get('expected', '')}->{row.get('got', '')}" for row in rows)
    print(f"  rows={len(rows)} routes={compact(routes)}")
    ordered = sorted(
        rows,
        key=lambda row: (
            row.get("expected", "") == row.get("got", ""),
            row.get("expected", ""),
            row.get("got", ""),
            row.get("sample", ""),
        ),
    )
    for row in (ordered if row_limit == 0 else ordered[: max(0, row_limit)]):
        print(
            f"    {cell(row, 'expected')}->{cell(row, 'got')} "
            f"energy={num(row, 'energy_low')}/{num(row, 'energy_mid')}/{num(row, 'energy_high')} "
            f"body={num(row, 'kick_body')}/{num(row, 'snare_body')}/{num(row, 'tom_body')} "
            f"crack={num(row, 'snare_crack')} upper_tom={num(row, 'upper_tom_body')} "
            f"levels={level_cells(row, tuple(f'{drum}_level' for drum in DRUMS))} "
            f"triggers={drum_trigger_cells(row)} "
            f"sample={short_path(cell(row, 'sample', ''))}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument", type=pathlib.Path, default=pathlib.Path("build/instrument_detected_attribute_rows.tsv"))
    parser.add_argument("--real-note", type=pathlib.Path, default=pathlib.Path("build/real_note_detected_attribute_rows.tsv"))
    parser.add_argument("--guitar-chord", type=pathlib.Path, default=pathlib.Path("build/guitar_chord_detected_attribute_rows.tsv"))
    parser.add_argument("--drum-primary", type=pathlib.Path, default=pathlib.Path("build/drum_primary_miss_attribute_rows.tsv"))
    parser.add_argument("--drum-full", type=pathlib.Path, default=pathlib.Path("build/drum_full_attribute_rows.tsv"))
    parser.add_argument(
        "--rows",
        "--row-limit",
        dest="rows",
        type=int,
        default=12,
        help="rows to print per section; 0 prints all measured rows",
    )
    args = parser.parse_args()

    row_limit = max(0, args.rows)
    report_instrument_rows(args.instrument, row_limit)
    report_real_note_rows(args.real_note, row_limit)
    report_guitar_chord_rows(args.guitar_chord, row_limit)
    report_drum_rows(args.drum_primary, "measured drum primary rows", row_limit)
    report_drum_rows(args.drum_full, "measured protected drum full rows", row_limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
