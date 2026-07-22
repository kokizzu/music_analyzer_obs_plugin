#!/usr/bin/env python3
"""Filter and print rows from the generated instrument attribute TSV."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib


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
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "centroid",
    "slope",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


def as_float(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "") or 0.0)
    except ValueError:
        return 0.0


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
    parser.add_argument("--debug-owner")
    parser.add_argument("--not-debug-owner")
    parser.add_argument("--field", action="append", default=[])
    parser.add_argument("--not-field", action="append", default=[])
    parser.add_argument("--min", action="append", default=[], help="numeric field threshold, field=value")
    parser.add_argument("--max", action="append", default=[], help="numeric field threshold, field=value")
    parser.add_argument("--columns", default=",".join(DEFAULT_COLUMNS))
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--count-by", action="append", default=[])
    args = parser.parse_args()

    rows = list(csv.DictReader(pathlib.Path(args.path).open(newline="", errors="replace"), delimiter="\t"))
    matched = [row for row in rows if row_matches(row, args)]

    if args.count_by:
        counts: collections.Counter[tuple[str, ...]] = collections.Counter(
            tuple(row.get(field, "") for field in args.count_by) for row in matched
        )
        for key, count in counts.most_common(args.limit):
            print("\t".join(key), count, sep="\t")
        print("count", len(matched), sep="\t")
        return 0

    columns = [column for column in args.columns.split(",") if column]
    print("\t".join(columns))
    for row in matched[: args.limit]:
        print("\t".join(row.get(column, "") for column in columns))
    print("count", len(matched), sep="\t")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
