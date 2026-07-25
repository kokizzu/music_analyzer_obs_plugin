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
    if args.status and row.get("status") != args.status:
        return False
    if args.owner_status and row.get("owner_status") != args.owner_status:
        return False
    if args.owner_bucket and row.get("owner_bucket") != args.owner_bucket:
        return False
    if args.pitch_quality and row.get("pitch_quality") != args.pitch_quality:
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
    parser.add_argument("--status")
    parser.add_argument("--owner-status")
    parser.add_argument("--owner-bucket")
    parser.add_argument("--pitch-quality", choices=["exact", "octave_alias", "other_pitch", "unknown"])
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
