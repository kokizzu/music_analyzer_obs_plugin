#!/usr/bin/env python3
"""Inspect drum TSV rows matching simple numeric candidate conditions."""

from __future__ import annotations

import argparse
import csv
import operator
import pathlib
import re
from collections import Counter
from statistics import median


CONDITION_RE = re.compile(r"^([A-Za-z0-9_]+)(<=|>=|==|<|>)(-?[0-9]+(?:\.[0-9]+)?)$")
OPS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
}


def as_float(value: str | None) -> float:
    try:
        return float(value or 0.0)
    except ValueError:
        return 0.0


def parse_condition(text: str):
    match = CONDITION_RE.match(text)
    if not match:
        raise argparse.ArgumentTypeError(
            f"condition must look like field>=1.23, got {text!r}"
        )
    field, op_name, value = match.groups()
    return field, op_name, float(value)


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: value for key, value in row.items() if key and value is not None}
            for row in csv.DictReader(handle, delimiter="\t")
            if row.get("sample") and row.get("expected")
        ]


def matches(row: dict[str, str], conditions) -> bool:
    for field, op_name, value in conditions:
        if not OPS[op_name](as_float(row.get(field)), value):
            return False
    return True


def summarize_field(rows: list[dict[str, str]], field: str) -> str:
    values = [as_float(row.get(field)) for row in rows if row.get(field, "") != ""]
    if not values:
        return "--"
    return f"min={min(values):.3f} med={median(values):.3f} max={max(values):.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", type=pathlib.Path)
    parser.add_argument("--condition", action="append", type=parse_condition, default=[])
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="numeric field to summarize; may be repeated",
    )
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    fields = args.field or [
        "crash_level",
        "hihat_level",
        "rim_band",
        "snare_band",
        "crash_seg",
        "hihat_seg",
        "ride_level",
        "rim_level",
        "energy_low",
        "energy_mid",
        "energy_high",
        "kick_body",
        "snare_body",
        "tom_body",
        "snare_crack",
    ]

    for path in args.rows:
        rows = read_rows(path)
        selected = [row for row in rows if matches(row, args.condition)]
        print(f"{path}: rows={len(rows)} selected={len(selected)}")
        print(f"  expected={dict(Counter(row.get('expected', '') for row in selected))}")
        print(f"  got={dict(Counter(row.get('got', '') for row in selected))}")
        for field in fields:
            print(f"  {field}: {summarize_field(selected, field)}")
        for row in selected[: max(0, args.examples)]:
            parts = [
                row.get("sample", "--"),
                f"expected={row.get('expected', '--')}",
                f"got={row.get('got', '--')}",
            ]
            parts.extend(f"{field}={row.get(field, '')}" for field in fields[:8])
            print("  example " + " ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
