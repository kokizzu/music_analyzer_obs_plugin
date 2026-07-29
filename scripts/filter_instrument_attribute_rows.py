#!/usr/bin/env python3
"""Filter and print rows from the generated instrument attribute TSV."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re


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


DEFAULT_COLUMNS = [
    "family",
    "program_name",
    "note",
    "path",
    "status",
    "expected_level",
    "display_note",
    "display_midi",
    "display_delta",
    "display_pitch_quality",
    "primary_note",
    "primary_midi",
    "primary_delta",
    "primary_pitch_quality",
    "target_notes",
    "target_distinct_midis",
    "target_octave_duplicates",
    "target_expected_visible",
    "target_primary_visible",
    "target_lowest_same_pitch_delta",
    "vocal_label",
    "vocal_level",
    "debug_note",
    "debug_owner",
    "debug_delta",
    "pitch_quality",
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "centroid",
    "slope",
    "third_octave_ratio",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


ATTRIBUTE_COLUMNS = [
    "family",
    "program_name",
    "note",
    "status",
    "owner_status",
    "owner_target",
    "owner",
    "owner_source",
    "display_note",
    "display_midi",
    "display_delta",
    "display_pitch_quality",
    "primary_note",
    "primary_midi",
    "primary_delta",
    "primary_pitch_quality",
    "target_notes",
    "target_distinct_midis",
    "target_octave_duplicates",
    "target_expected_visible",
    "target_primary_visible",
    "target_lowest_same_pitch_midi",
    "target_lowest_same_pitch_delta",
    "debug_note",
    "debug_owner",
    "debug_delta",
    "pitch_quality",
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
    "centroid",
    "slope",
    "noise",
    "third_octave_ratio",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "debug_count",
    "debug_candidates",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_note",
    "raw_expected_rank",
]


def as_float(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "") or 0.0)
    except ValueError:
        return 0.0


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def debug_pitch_delta(row: dict[str, str]) -> int | None:
    expected = parse_int(row.get("midi", ""))
    actual = parse_int(row.get("debug_midi", ""))
    if actual is None and row.get("debug_note", ""):
        actual = midi_from_note(row["debug_note"])
    if expected is None or actual is None:
        return None
    return actual - expected


def display_pitch_delta(row: dict[str, str]) -> int | None:
    direct = parse_int(row.get("display_delta", ""))
    if direct is not None:
        return direct
    expected = parse_int(row.get("midi", ""))
    actual = parse_int(row.get("display_midi", ""))
    if actual is None and row.get("display_note", ""):
        actual = midi_from_note(row["display_note"])
    if expected is None or actual is None:
        return None
    return actual - expected


def primary_pitch_delta(row: dict[str, str]) -> int | None:
    direct = parse_int(row.get("primary_delta", ""))
    if direct is not None:
        return direct
    expected = parse_int(row.get("midi", ""))
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


def owner_target(row: dict[str, str]) -> str:
    family = row.get("family", "") or row.get("expected_family", "")
    if family == "piano":
        return "piano"
    if family == "guitar":
        return "guitar"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth"}:
        return "other"
    if family == "bass":
        return "bass"
    return family or "unknown"


DISPLAY_LEVEL_FIELDS = {
    "bass": "bass_level",
    "piano": "piano_level",
    "guitar": "guitar_level",
    "vocals": "vocal_level",
    "other": "other_level",
}

DISPLAY_NOTE_FIELDS = {
    "bass": "bass_notes",
    "piano": "piano_notes",
    "guitar": "guitar_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
}


def target_note_field(target: str) -> str | None:
    return DISPLAY_NOTE_FIELDS.get(target)


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
        by_pitch_class[((midi % 12) + 12) % 12].add(midi)
    return sum(1 for values in by_pitch_class.values() if len(values) > 1)


def midi_pitch_class(midi: int) -> int:
    return ((midi % 12) + 12) % 12


def row_primary_midi(row: dict[str, str]) -> int | None:
    actual = parse_int(row.get("primary_midi", ""))
    if actual is None and row.get("primary_note", ""):
        actual = midi_from_note(row["primary_note"])
    return actual


def target_display_hit(row: dict[str, str], target: str) -> bool:
    if row.get("status") != "hit" or row.get("detected_expected_row") != "1":
        return False
    field = DISPLAY_LEVEL_FIELDS.get(target)
    return field is not None and as_float(row, field) > 0.0


def owner_and_source(row: dict[str, str]) -> tuple[str, str]:
    target = owner_target(row)
    if target_display_hit(row, target):
        return target, "display"
    return row.get("debug_owner", "") or "none", "debug"


def owner_status(row: dict[str, str]) -> str:
    target = owner_target(row)
    owner, _source = owner_and_source(row)
    return "owner_hit" if owner == target else "owner_miss"


def enrich_row(row: dict[str, str]) -> dict[str, str]:
    row = dict(row)
    row["owner_target"] = owner_target(row)
    row["owner"], row["owner_source"] = owner_and_source(row)
    row["owner_status"] = owner_status(row)
    row["owner_bucket"] = f"{row['owner_status']}:{row.get('family', '')}->{row['owner']}"
    delta = debug_pitch_delta(row)
    row["debug_delta"] = "" if delta is None else str(delta)
    row["pitch_quality"] = pitch_quality(delta)
    delta = display_pitch_delta(row)
    row["display_delta"] = "" if delta is None else str(delta)
    row["display_pitch_quality"] = pitch_quality(delta)
    delta = primary_pitch_delta(row)
    row["primary_delta"] = "" if delta is None else str(delta)
    row["primary_pitch_quality"] = pitch_quality(delta)
    note_field = target_note_field(row["owner_target"])
    row["target_notes"] = row.get(note_field or "", "") if note_field else ""
    target_midis = note_cell_midis(row["target_notes"])
    row["target_distinct_midis"] = str(len(target_midis))
    row["target_octave_duplicates"] = str(octave_duplicate_count(target_midis))
    expected_midi = parse_int(row.get("midi", ""))
    actual_primary_midi = row_primary_midi(row)
    row["target_expected_visible"] = "1" if expected_midi is not None and expected_midi in target_midis else "0"
    row["target_primary_visible"] = (
        "1" if actual_primary_midi is not None and actual_primary_midi in target_midis else "0"
    )
    same_pitch_midis = (
        [midi for midi in target_midis if midi_pitch_class(midi) == midi_pitch_class(expected_midi)]
        if expected_midi is not None
        else []
    )
    lowest_same_pitch = min(same_pitch_midis) if same_pitch_midis else None
    row["target_lowest_same_pitch_midi"] = "" if lowest_same_pitch is None else str(lowest_same_pitch)
    row["target_lowest_same_pitch_delta"] = (
        "" if lowest_same_pitch is None or expected_midi is None else str(lowest_same_pitch - expected_midi)
    )
    return row


def field_matches(row: dict[str, str], specs: list[str], equal: bool) -> bool:
    for spec in specs:
        if "=" not in spec:
            raise SystemExit(f"invalid field filter `{spec}`; expected field=value")
        field, value = spec.split("=", 1)
        matched = row.get(field, "") == value
        if matched != equal:
            return False
    return True


def row_matches(row: dict[str, str], args: argparse.Namespace) -> bool:
    if args.kind and row.get("kind") != args.kind:
        return False
    if args.family and row.get("family") != args.family:
        return False
    if args.not_family and row.get("family") == args.not_family:
        return False
    if args.program_name and row.get("program_name") != args.program_name:
        return False
    if args.note and row.get("note") != args.note:
        return False
    if args.midi is not None and parse_int(row.get("midi", "")) != args.midi:
        return False
    if args.status and row.get("status") != args.status:
        return False
    if args.owner_status and row.get("owner_status") != args.owner_status:
        return False
    if args.owner_bucket and row.get("owner_bucket") != args.owner_bucket:
        return False
    if args.pitch_quality and row.get("pitch_quality") != args.pitch_quality:
        return False
    if args.display_pitch_quality and row.get("display_pitch_quality") != args.display_pitch_quality:
        return False
    if args.primary_pitch_quality and row.get("primary_pitch_quality") != args.primary_pitch_quality:
        return False
    if args.debug_owner and (row.get("debug_owner", "") or "none") != args.debug_owner:
        return False
    if args.not_debug_owner and (row.get("debug_owner", "") or "none") == args.not_debug_owner:
        return False
    if not field_matches(row, args.field, True):
        return False
    if not field_matches(row, args.not_field, False):
        return False
    for spec in args.min:
        field, raw = spec.split("=", 1)
        if as_float(row, field) < float(raw):
            return False
    for spec in args.max:
        field, raw = spec.split("=", 1)
        if as_float(row, field) > float(raw):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/instrument_sample_attributes.tsv")
    parser.add_argument("--kind", default="note")
    parser.add_argument("--family")
    parser.add_argument("--not-family")
    parser.add_argument("--program-name")
    parser.add_argument("--note")
    parser.add_argument("--midi", type=int)
    parser.add_argument("--status")
    parser.add_argument("--owner-status")
    parser.add_argument("--owner-bucket")
    parser.add_argument("--pitch-quality", choices=["exact", "octave_alias", "other_pitch", "unknown"])
    parser.add_argument("--display-pitch-quality", choices=["exact", "octave_alias", "other_pitch", "unknown"])
    parser.add_argument("--primary-pitch-quality", choices=["exact", "octave_alias", "other_pitch", "unknown"])
    parser.add_argument("--debug-owner")
    parser.add_argument("--not-debug-owner")
    parser.add_argument("--field", action="append", default=[])
    parser.add_argument("--not-field", action="append", default=[])
    parser.add_argument("--min", action="append", default=[], help="numeric field threshold, field=value")
    parser.add_argument("--max", action="append", default=[], help="numeric field threshold, field=value")
    parser.add_argument("--columns")
    parser.add_argument(
        "--preset",
        choices=["default", "attributes"],
        default="default",
        help="column preset to print when --columns is not supplied",
    )
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--count-by", action="append", default=[])
    args = parser.parse_args()

    rows = [
        enrich_row(row)
        for row in csv.DictReader(pathlib.Path(args.path).open(newline="", errors="replace"), delimiter="\t")
    ]
    matched = [row for row in rows if row_matches(row, args)]

    if args.count_by:
        counts: collections.Counter[tuple[str, ...]] = collections.Counter(
            tuple(row.get(field, "") for field in args.count_by) for row in matched
        )
        for key, count in counts.most_common(args.limit):
            print("\t".join(key), count, sep="\t")
        print("count", len(matched), sep="\t")
        return 0

    default_columns = ATTRIBUTE_COLUMNS if args.preset == "attributes" else DEFAULT_COLUMNS
    columns = [column for column in (args.columns or ",".join(default_columns)).split(",") if column]
    print("\t".join(columns))
    for row in matched[: args.limit]:
        print("\t".join(row.get(column, "") for column in columns))
    print("count", len(matched), sep="\t")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
