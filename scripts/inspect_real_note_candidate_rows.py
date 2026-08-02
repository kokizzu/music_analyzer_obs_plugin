#!/usr/bin/env python3
"""Inspect real-note TSV rows matching candidate rule conditions."""

from __future__ import annotations

import argparse
import collections
import csv
import operator
import pathlib
import re
from statistics import median

from filter_instrument_attribute_rows import enrich_row
from inspect_real_note_attribute_buckets import derive_row


Condition = tuple[str, str, str]

CONDITION_RE = re.compile(r"^([A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)?)(!=|>=|<=|==|=|<|>|:)(.+)$")
NUMERIC_OPS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

DEFAULT_FIELDS = [
    "expected_row_score",
    "first_row_score",
    "visual_first_row_score",
    "expected_first_score_ratio",
    "expected_visual_first_score_ratio",
    "first_expected_score_margin",
    "visual_first_expected_score_margin",
    "expected_row_exact_level",
    "expected_row_pitch_level",
    "expected_row_visual_exact_level",
    "expected_row_visual_pitch_level",
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
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
]

DEFAULT_EXAMPLE_FIELDS = [
    "sample_id",
    "path",
    "status",
    "family",
    "source",
    "expected_note",
    "note",
    "expected_midi",
    "midi",
    "first_row",
    "visual_first_row",
    "debug_note",
    "debug_owner",
    "owner_status",
    "miss_reason",
]


def parse_condition(text: str) -> Condition:
    match = CONDITION_RE.fullmatch(text)
    if not match:
        raise argparse.ArgumentTypeError(
            f"condition must look like field=value, field>=1.23, or a/b<0.9, got {text!r}"
        )
    return match.group(1), match.group(2), match.group(3)


def parse_rule(text: str) -> list[Condition]:
    parts = [part.strip() for part in text.split(" AND ") if part.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("rule must include at least one condition")
    return [parse_condition(part) for part in parts]


def as_float(value: str | None) -> float | None:
    try:
        return float(value or "")
    except ValueError:
        return None


def sample_key(row: dict[str, str]) -> str:
    return row.get("sample_id", "") or row.get("sample", "") or row.get("path", "")


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    if not normalized.get("expected_note") and normalized.get("note"):
        normalized["expected_note"] = normalized["note"]
    if not normalized.get("expected_midi") and normalized.get("midi"):
        normalized["expected_midi"] = normalized["midi"]
    return enrich_row(derive_row(normalized))


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return [
            normalize_row({key: value for key, value in row.items() if key and value is not None})
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def numeric_value(row: dict[str, str], expression: str) -> float | None:
    if "/" not in expression:
        return as_float(row.get(expression))
    numerator, denominator = expression.split("/", 1)
    numerator_value = as_float(row.get(numerator))
    denominator_value = as_float(row.get(denominator))
    if numerator_value is None or denominator_value is None:
        return None
    if abs(denominator_value) < 1.0e-9:
        return float("inf") if numerator_value > 0.0 else 0.0
    return numerator_value / denominator_value


def matches_condition(row: dict[str, str], condition: Condition) -> bool:
    field, op_name, expected = condition
    if op_name in {"=", "==", "!="} and "/" not in field:
        matched = row.get(field, "") == expected
        return not matched if op_name == "!=" else matched

    actual_number = numeric_value(row, field)
    if actual_number is None:
        return False

    if op_name == ":":
        try:
            low, high = (float(part) for part in expected.split(":", 1))
        except ValueError as exc:
            raise SystemExit(f"invalid range condition `{field}:{expected}`") from exc
        return low <= actual_number <= high

    expected_number = as_float(expected)
    if expected_number is None:
        raise SystemExit(f"invalid numeric condition `{field}{op_name}{expected}`")
    if op_name in {"=", "=="}:
        return actual_number == expected_number
    if op_name == "!=":
        return actual_number != expected_number
    return NUMERIC_OPS[op_name](actual_number, expected_number)


def row_matches(row: dict[str, str], conditions: list[Condition]) -> bool:
    return all(matches_condition(row, condition) for condition in conditions)


def summarize_numeric(rows: list[dict[str, str]], field: str) -> str:
    values = [
        value
        for value in (numeric_value(row, field) for row in rows)
        if value is not None and value != float("inf") and value != float("-inf")
    ]
    if not values:
        return "--"
    return f"min={min(values):.3f} med={median(values):.3f} max={max(values):.3f}"


def print_groups(rows: list[dict[str, str]], fields: list[str], top: int) -> None:
    grouped: collections.Counter[tuple[str, ...]] = collections.Counter()
    samples: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    for row in rows:
        key = tuple(row.get(field, "") for field in fields)
        grouped[key] += 1
        key_sample = sample_key(row)
        if key_sample:
            samples[key].add(key_sample)

    print(f"  groups {'/'.join(fields)}")
    for key, count in grouped.most_common(max(0, top)):
        label = "/".join(value or "-" for value in key)
        print(f"    {label} rows={count} samples={len(samples[key])}")


def print_examples(rows: list[dict[str, str]], fields: list[str], examples: int) -> None:
    for row in rows[: max(0, examples)]:
        parts = []
        for field in fields:
            value = row.get(field, "")
            if value:
                parts.append(f"{field}={value}")
        print("  example " + " ".join(parts))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", type=pathlib.Path)
    parser.add_argument("--condition", action="append", type=parse_condition, default=[])
    parser.add_argument(
        "--rule",
        action="append",
        type=parse_rule,
        default=[],
        help="candidate rule using ` AND ` between conditions, matching route-summary output",
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="numeric field or ratio expression to summarize; may be repeated",
    )
    parser.add_argument(
        "--group-by",
        action="append",
        default=None,
        help="field to group selected rows by; may be repeated",
    )
    parser.add_argument(
        "--example-field",
        action="append",
        default=[],
        help="field to include in example rows; may be repeated",
    )
    parser.add_argument("--examples", type=int, default=8)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    fields = args.field or DEFAULT_FIELDS
    group_by = args.group_by or ["status", "family", "source", "first_row", "visual_first_row"]
    example_fields = args.example_field or DEFAULT_EXAMPLE_FIELDS
    conditions = list(args.condition)
    for rule in args.rule:
        conditions.extend(rule)

    for path in args.rows:
        rows = read_rows(path)
        selected = [row for row in rows if row_matches(row, conditions)]
        selected_samples = {sample_key(row) for row in selected if sample_key(row)}
        print(f"{path}: rows={len(rows)} selected={len(selected)} samples={len(selected_samples)}")
        print_groups(selected, group_by, args.top)
        for field in fields:
            print(f"  {field}: {summarize_numeric(selected, field)}")
        print_examples(selected, example_fields, args.examples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
