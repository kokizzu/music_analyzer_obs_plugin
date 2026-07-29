#!/usr/bin/env python3
"""Filter and print rows from drum attribute TSV dumps."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")

DEFAULT_COLUMNS = [
    "sample",
    "expected",
    "got",
    "status",
    "expected_level",
    "got_level",
    "expected_trigger_ratio",
    "got_trigger_ratio",
    "expected_shape",
    "got_shape",
    "energy_low",
    "energy_mid",
    "energy_high",
    "tom_snare_body_ratio",
    "tom_kick_body_ratio",
    "snare_kick_body_ratio",
    "snare_crack_ratio",
    "upper_tom_crack_ratio",
    "body_shape",
    "merged_expected",
]


def as_float(value: str) -> float:
    try:
        return float(value or 0.0)
    except ValueError:
        return 0.0


def ratio(numerator: float, denominator: float) -> str:
    if abs(denominator) < 1.0e-9:
        return ""
    return f"{numerator / denominator:.6f}"


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return [augment_row(row) for row in csv.DictReader(handle, delimiter="\t")]


def augment_row(row: dict[str, str]) -> dict[str, str]:
    row = dict(row)
    expected = row.get("expected", "")
    got = row.get("got", "")
    row["status"] = "hit" if expected and expected == got else "miss"

    for label, category in (("expected", expected), ("got", got)):
        if category not in CATEGORIES:
            row[f"{label}_level"] = ""
            row[f"{label}_trigger_ratio"] = ""
            row[f"{label}_shape"] = ""
            row[f"{label}_band"] = ""
            row[f"{label}_seg"] = ""
            row[f"{label}_shape_score"] = ""
            continue
        row[f"{label}_level"] = row.get(f"{category}_level", "")
        row[f"{label}_shape"] = row.get(f"{category}_shape", "")
        row[f"{label}_band"] = row.get(f"{category}_band", "")
        row[f"{label}_seg"] = row.get(f"{category}_seg", "")
        row[f"{label}_shape_score"] = row.get(f"{category}_shape_score", "")
        trigger = as_float(row.get(f"{category}_trigger", ""))
        threshold = as_float(row.get(f"{category}_threshold", ""))
        row[f"{label}_trigger_ratio"] = ratio(trigger, threshold)

    kick_body = as_float(row.get("kick_body", ""))
    snare_body = as_float(row.get("snare_body", ""))
    tom_body = as_float(row.get("tom_body", ""))
    snare_crack = as_float(row.get("snare_crack", ""))
    upper_tom = as_float(row.get("upper_tom_body", ""))
    row["tom_snare_body_ratio"] = ratio(tom_body, snare_body)
    row["tom_kick_body_ratio"] = ratio(tom_body, kick_body)
    row["snare_kick_body_ratio"] = ratio(snare_body, kick_body)
    row["snare_crack_ratio"] = ratio(snare_crack, snare_body)
    row["upper_tom_crack_ratio"] = ratio(upper_tom, snare_crack)
    return row


def split_route(route: str) -> tuple[str, str]:
    delimiter = "->" if "->" in route else ":"
    if delimiter not in route:
        raise argparse.ArgumentTypeError("route must use expected->got or expected:got")
    expected, got = route.split(delimiter, 1)
    if not expected or not got:
        raise argparse.ArgumentTypeError("route must use expected->got or expected:got")
    return expected, got


def parse_field_filter(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("field filters must use FIELD=VALUE")
    field, expected = value.split("=", 1)
    if not field:
        raise argparse.ArgumentTypeError("field filters need a field name")
    return field, expected


def parse_bound(value: str) -> tuple[str, float]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("numeric filters must use FIELD=NUMBER")
    field, raw_number = value.split("=", 1)
    if not field:
        raise argparse.ArgumentTypeError("numeric filters need a field name")
    try:
        number = float(raw_number)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid numeric value: {raw_number}") from exc
    return field, number


def filter_rows(rows: list[dict[str, str]], args: argparse.Namespace) -> list[dict[str, str]]:
    selected = rows
    if args.expected:
        selected = [row for row in selected if row.get("expected") == args.expected]
    if args.got:
        selected = [row for row in selected if row.get("got") == args.got]
    if args.route:
        expected, got = args.route
        selected = [row for row in selected if row.get("expected") == expected and row.get("got") == got]
    if args.status:
        selected = [row for row in selected if row.get("status") == args.status]
    if args.sample:
        selected = [row for row in selected if args.sample in row.get("sample", "")]
    for field, expected in args.field:
        selected = [row for row in selected if row.get(field, "") == expected]
    for field, minimum in args.min:
        selected = [row for row in selected if as_float(row.get(field, "")) >= minimum]
    for field, maximum in args.max:
        selected = [row for row in selected if as_float(row.get(field, "")) <= maximum]
    return selected


def print_counts(rows: list[dict[str, str]], fields: list[str]) -> None:
    counter: collections.Counter[tuple[str, ...]] = collections.Counter()
    for row in rows:
        counter[tuple(row.get(field, "") for field in fields)] += 1
    print("\t".join(fields + ["count"]))
    for key, count in counter.most_common():
        print("\t".join([*key, str(count)]))


def print_table(rows: list[dict[str, str]], columns: list[str], limit: int) -> None:
    print("\t".join(columns))
    selected = rows if limit == 0 else rows[: max(0, limit)]
    for row in selected:
        print("\t".join(row.get(column, "") for column in columns))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", type=pathlib.Path)
    parser.add_argument("--expected")
    parser.add_argument("--got")
    parser.add_argument("--route", type=split_route)
    parser.add_argument("--status", choices=("hit", "miss"))
    parser.add_argument("--sample")
    parser.add_argument("--field", action="append", default=[], type=parse_field_filter)
    parser.add_argument("--min", action="append", default=[], type=parse_bound)
    parser.add_argument("--max", action="append", default=[], type=parse_bound)
    parser.add_argument("--columns", default=",".join(DEFAULT_COLUMNS))
    parser.add_argument("--count-by", action="append", default=[])
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    rows = filter_rows(load_rows(args.tsv), args)
    if args.count_by:
        print_counts(rows, args.count_by)
    else:
        columns = [column.strip() for column in args.columns.split(",") if column.strip()]
        print_table(rows, columns, args.limit)
    print(f"count\t{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
