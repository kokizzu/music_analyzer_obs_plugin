#!/usr/bin/env python3
"""Measure a hand-written rule against real-note attribute rows."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
from decimal import Decimal, InvalidOperation, ROUND_FLOOR

from inspect_real_note_attribute_buckets import derive_row


Condition = tuple[str, str, str]
NumericBucket = tuple[str, Decimal, int]

CONDITION_RE = re.compile(r"^([^!<>=:]+)(!=|>=|<=|=|>|<|:)(.+)$")


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def parse_condition(spec: str) -> Condition:
    match = CONDITION_RE.fullmatch(spec)
    if not match:
        raise SystemExit(f"invalid condition `{spec}`")
    return match.group(1), match.group(2), match.group(3)


def parse_numeric_bucket(spec: str) -> NumericBucket:
    try:
        field, width_spec = spec.split(":", 1)
    except ValueError as exc:
        raise SystemExit(f"invalid numeric bucket `{spec}`; expected FIELD:WIDTH") from exc
    if not field:
        raise SystemExit(f"invalid numeric bucket `{spec}`; missing field")
    try:
        width = Decimal(width_spec)
    except InvalidOperation as exc:
        raise SystemExit(f"invalid numeric bucket width `{width_spec}`") from exc
    if width <= 0:
        raise SystemExit(f"invalid numeric bucket width `{width_spec}`; must be positive")
    places = max(0, -width.as_tuple().exponent)
    return field, width, places


def format_decimal(value: Decimal, places: int) -> str:
    return f"{value:.{places}f}"


def apply_numeric_buckets(row: dict[str, str], buckets: list[NumericBucket]) -> dict[str, str]:
    if not buckets:
        return row
    result = dict(row)
    for field, width, places in buckets:
        value_spec = result.get(field, "")
        bucket_field = f"{field}_bucket"
        if not value_spec:
            result[bucket_field] = ""
            continue
        try:
            value = Decimal(value_spec)
        except InvalidOperation:
            result[bucket_field] = ""
            continue
        bucket_index = (value / width).to_integral_value(rounding=ROUND_FLOOR)
        low = bucket_index * width
        high = low + width
        result[bucket_field] = f"{format_decimal(low, places)}-{format_decimal(high, places)}"
    return result


def matches_condition(row: dict[str, str], condition: Condition) -> bool:
    field, op, expected = condition
    actual = row.get(field, "")
    if op == "=":
        return actual == expected
    if op == "!=":
        return actual != expected

    actual_number = as_float(actual)
    if actual_number is None:
        return False

    if op == ":":
        try:
            low, high = (float(part) for part in expected.split(":", 1))
        except ValueError as exc:
            raise SystemExit(f"invalid range condition `{field}:{expected}`") from exc
        return low <= actual_number <= high

    expected_number = as_float(expected)
    if expected_number is None:
        raise SystemExit(f"invalid numeric condition `{field}{op}{expected}`")
    if op == ">=":
        return actual_number >= expected_number
    if op == "<=":
        return actual_number <= expected_number
    if op == ">":
        return actual_number > expected_number
    if op == "<":
        return actual_number < expected_number
    raise AssertionError(op)


def load_rows(path: pathlib.Path, buckets: list[NumericBucket]) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return [
            apply_numeric_buckets(derive_row(row), buckets)
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def matching_rows(
    path: pathlib.Path,
    conditions: list[Condition],
    buckets: list[NumericBucket],
) -> list[dict[str, str]]:
    return [
        row
        for row in load_rows(path, buckets)
        if all(matches_condition(row, condition) for condition in conditions)
    ]


def print_row_summary(
    label: str,
    path: pathlib.Path,
    rows: list[dict[str, str]],
    condition_specs: list[str],
    group_by: list[str],
    examples: int,
    top: int,
) -> None:
    sample_ids = sorted({row.get("sample_id", "") for row in rows if row.get("sample_id", "")})

    if label == "matched":
        print(f"matched rows={len(rows)} samples={len(sample_ids)}")
    else:
        print(f"{label} rows={len(rows)} samples={len(sample_ids)} path={path}")
    if condition_specs:
        print(f"{label} conditions " + " ".join(condition_specs))
    if sample_ids:
        print(f"{label} examples " + " ".join(sample_ids[: max(0, examples)]))

    grouped: collections.Counter[tuple[str, ...]] = collections.Counter()
    grouped_samples: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    for row in rows:
        key = tuple(row.get(field, "") for field in group_by)
        grouped[key] += 1
        sample_id = row.get("sample_id", "")
        if sample_id:
            grouped_samples[key].add(sample_id)

    if grouped:
        print(f"{label} groups " + "/".join(group_by))
        for key, count in grouped.most_common(max(0, top)):
            bucket_label = "/".join(value or "-" for value in key)
            print(f"  {bucket_label} rows={count} samples={len(grouped_samples[key])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help=(
            "rule condition applied to the primary path and every --compare-path: "
            "field=value, field!=value, field>=number, field<=number, or field:min:max"
        ),
    )
    parser.add_argument(
        "--primary-condition",
        action="append",
        default=[],
        help="additional condition applied only to the primary path",
    )
    parser.add_argument(
        "--compare-path",
        action="append",
        default=[],
        help="additional TSV path to measure with the same --condition rule",
    )
    parser.add_argument(
        "--compare-condition",
        action="append",
        default=[],
        help="additional condition applied only to --compare-path rows",
    )
    parser.add_argument("--examples", type=int, default=16, help="number of sample ids to print")
    parser.add_argument("--top", type=int, default=20, help="number of grouped buckets to print")
    parser.add_argument(
        "--group-by",
        action="append",
        default=None,
        help="field to group matches by; repeatable; defaults to family/source/first_row",
    )
    parser.add_argument(
        "--numeric-bucket",
        action="append",
        default=[],
        help=(
            "derive FIELD_bucket from numeric FIELD using WIDTH-sized ranges, e.g. "
            "slope:0.001 then --group-by slope_bucket; repeatable"
        ),
    )
    parser.add_argument(
        "--compare-group-by",
        action="append",
        default=None,
        help="field to group compare matches by; repeatable; defaults to --group-by",
    )
    args = parser.parse_args()

    group_by = args.group_by or ["family", "source", "first_row"]
    compare_group_by = args.compare_group_by or group_by
    numeric_buckets = [parse_numeric_bucket(spec) for spec in args.numeric_bucket]
    rule_conditions = [parse_condition(spec) for spec in args.condition]
    primary_condition_specs = args.condition + args.primary_condition
    primary_conditions = rule_conditions + [
        parse_condition(spec) for spec in args.primary_condition
    ]
    primary_path = pathlib.Path(args.path)
    rows = matching_rows(primary_path, primary_conditions, numeric_buckets)
    print_row_summary(
        "matched",
        primary_path,
        rows,
        primary_condition_specs,
        group_by,
        args.examples,
        args.top,
    )

    compare_condition_specs = args.condition + args.compare_condition
    compare_conditions = rule_conditions + [
        parse_condition(spec) for spec in args.compare_condition
    ]
    compare_paths = args.compare_path
    if args.compare_condition and not compare_paths:
        compare_paths = [str(primary_path)]
    for compare_path_spec in compare_paths:
        compare_path = pathlib.Path(compare_path_spec)
        compare_rows = matching_rows(compare_path, compare_conditions, numeric_buckets)
        print_row_summary(
            "compare",
            compare_path,
            compare_rows,
            compare_condition_specs,
            compare_group_by,
            args.examples,
            args.top,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
