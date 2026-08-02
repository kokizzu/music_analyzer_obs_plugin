#!/usr/bin/env python3
"""Summarize drum rule-flag usage on false-active routes."""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import Counter
from statistics import median


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
FLAG_FIELDS = (
    "flag_generated_gm_source",
    "flag_one_shot_source",
    "flag_real_track_source",
    "flag_tom_kick_primary_recovery",
    "flag_protected_tom_kick_primary_recovery",
    "flag_narrow_tom_kick_primary_recovery",
    "flag_gm_orchestra_tom_recovery",
    "flag_snare_crack_tom_bleed",
    "flag_strong_low_kick_tom_bleed",
    "flag_saturated_kick_tom_bleed",
    "flag_high_band_kick_body_tom_bleed",
    "flag_massive_tom_body_snare_primary_recovery",
    "flag_upper_tom_snare_active_bleed",
    "flag_bright_kick_active_bleed",
    "flag_upper_tom_from_snare_active_bleed",
)


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: value for key, value in row.items() if key and value is not None}
            for row in csv.DictReader(handle, delimiter="\t")
            if row.get("sample") and row.get("expected")
        ]


def true_active_rows(rows: list[dict[str, str]], category: str, threshold: float) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("expected", "") == category and as_float(row.get(f"{category}_level", "")) > threshold
    ]


def false_route_rows(
    rows: list[dict[str, str]],
    expected: str,
    active: str,
    threshold: float,
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("expected", "") == expected and as_float(row.get(f"{active}_level", "")) > threshold
    ]


def false_routes(
    rows: list[dict[str, str]],
    threshold: float,
) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        expected = row.get("expected", "")
        for active in CATEGORIES:
            if active == expected:
                continue
            if as_float(row.get(f"{active}_level", "")) > threshold:
                grouped.setdefault((expected, active), []).append(row)
    return grouped


def has_flag(row: dict[str, str], field: str) -> bool:
    return row.get(field, "") not in ("", "0", "0.0", "false", "False")


def median_field(rows: list[dict[str, str]], field: str) -> str:
    values = [as_float(row.get(field, "")) for row in rows if row.get(field, "") != ""]
    return "--" if not values else f"{median(values):.3f}"


def flag_counter(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        for field in FLAG_FIELDS:
            if has_flag(row, field):
                counts[field] += 1
    return counts


def format_flags(counter: Counter[str], total: int, limit: int) -> str:
    if not counter or total <= 0:
        return "--"
    parts = []
    for field, count in counter.most_common(limit):
        percent = 100.0 * count / total
        parts.append(f"{field}={count}/{total} {percent:.1f}%")
    return " ".join(parts)


def format_delta_flags(
    false_counts: Counter[str],
    false_total: int,
    protected_counts: Counter[str],
    protected_total: int,
    limit: int,
) -> str:
    if false_total <= 0:
        return "--"
    scored: list[tuple[float, str, int, float, int, float]] = []
    for field in FLAG_FIELDS:
        false_count = false_counts[field]
        if false_count == 0:
            continue
        protected_count = protected_counts[field]
        false_percent = false_count / false_total
        protected_percent = protected_count / protected_total if protected_total else 0.0
        scored.append(
            (
                false_percent - protected_percent,
                field,
                false_count,
                false_percent,
                protected_count,
                protected_percent,
            )
        )
    if not scored:
        return "--"
    scored.sort(key=lambda item: (-item[0], item[1]))
    parts = []
    for _delta, field, false_count, false_percent, protected_count, protected_percent in scored[:limit]:
        parts.append(
            f"{field}=false {false_count}/{false_total} {100.0 * false_percent:.1f}% "
            f"protected {protected_count}/{protected_total} {100.0 * protected_percent:.1f}%"
        )
    return " ".join(parts)


def parse_route(route: str) -> tuple[str, str]:
    separator = "->" if "->" in route else ":"
    if separator not in route:
        raise argparse.ArgumentTypeError("route must use expected->active or expected:active syntax")
    expected, active = route.split(separator, 1)
    if expected not in CATEGORIES or active not in CATEGORIES or expected == active:
        raise argparse.ArgumentTypeError(f"unsupported route: {route}")
    return expected, active


def summarize_route(
    rows: list[dict[str, str]],
    expected: str,
    active: str,
    threshold: float,
    flag_limit: int,
    example_count: int,
) -> None:
    route_rows = false_route_rows(rows, expected, active, threshold)
    protected = true_active_rows(rows, active, threshold)
    false_counts = flag_counter(route_rows)
    protected_counts = flag_counter(protected)
    print(
        f"route {expected}->{active} false={len(route_rows)} protected_true_{active}={len(protected)} "
        f"false_level_med={median_field(route_rows, active + '_level')} "
        f"protected_level_med={median_field(protected, active + '_level')}"
    )
    print(f"  false flags: {format_flags(false_counts, len(route_rows), flag_limit)}")
    print(f"  protected flags: {format_flags(protected_counts, len(protected), flag_limit)}")
    print(
        f"  false-skew flags: "
        f"{format_delta_flags(false_counts, len(route_rows), protected_counts, len(protected), flag_limit)}"
    )
    for row in route_rows[:example_count]:
        active_level = as_float(row.get(f"{active}_level", ""))
        expected_level = as_float(row.get(f"{expected}_level", ""))
        flags = [field for field in FLAG_FIELDS if has_flag(row, field)]
        print(
            f"    sample={row.get('sample', '--')} got={row.get('got', '--')} "
            f"{active}_level={active_level:.3f} {expected}_level={expected_level:.3f} "
            f"flags={','.join(flags) if flags else '--'}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", type=pathlib.Path)
    parser.add_argument("--threshold", type=float, default=0.30)
    parser.add_argument("--route", action="append", type=parse_route, default=[])
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--flag-limit", type=int, default=5)
    parser.add_argument("--examples", type=int, default=2)
    args = parser.parse_args()

    rows = read_rows(args.rows)
    print(f"drum rule flag summary: rows={len(rows)} threshold={args.threshold:.2f} source={args.rows}")
    selected_routes = args.route
    if not selected_routes:
        grouped = false_routes(rows, args.threshold)
        selected_routes = [
            route
            for route, _route_rows in sorted(
                grouped.items(),
                key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
            )[: max(0, args.limit)]
        ]
    for expected, active in selected_routes:
        summarize_route(
            rows,
            expected,
            active,
            args.threshold,
            max(0, args.flag_limit),
            max(0, args.examples),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
