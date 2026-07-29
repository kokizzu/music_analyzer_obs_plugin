#!/usr/bin/env python3
"""Summarize false active drum rows from analyzer_drum_samples attributes."""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import Counter
from statistics import median


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def pct(hit: int, total: int) -> float:
    return 100.0 * hit / total if total else 0.0


def median_field(rows: list[dict[str, str]], field: str) -> str:
    values = [as_float(row.get(field, "")) for row in rows if row.get(field, "") != ""]
    return "--" if not values else f"{median(values):.3f}"


def median_values(values: list[float]) -> str:
    return "--" if not values else f"{median(values):.3f}"


def compact_counter(counter: Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def active_trigger_ratio(row: dict[str, str], category: str) -> float:
    return as_float(row.get(f"{category}_trigger", "")) / (
        as_float(row.get(f"{category}_threshold", "")) + 1.0e-6
    )


def expected_level(row: dict[str, str]) -> float:
    expected = row.get("expected", "")
    return as_float(row.get(f"{expected}_level", ""))


def expected_trigger_ratio(row: dict[str, str]) -> float:
    expected = row.get("expected", "")
    return as_float(row.get(f"{expected}_trigger", "")) / (
        as_float(row.get(f"{expected}_threshold", "")) + 1.0e-6
    )


def route_text(rows: list[dict[str, str]], expected: str, active: str) -> str:
    return (
        f"{expected}->{active} rows={len(rows)} "
        f"level_med={median_field(rows, active + '_level')} "
        f"trigger_ratio_med={median_values([active_trigger_ratio(row, active) for row in rows]):s} "
        f"seg_med={median_field(rows, active + '_seg')} "
        f"expected_level_med={median_values([expected_level(row) for row in rows]):s} "
        f"expected_trigger_ratio_med={median_values([expected_trigger_ratio(row) for row in rows]):s} "
        f"primary={compact_counter(Counter(row.get('got', '') for row in rows), 4)}"
    )


def false_route_rows(rows: list[dict[str, str]], threshold: float) -> list[tuple[str, str, dict[str, str]]]:
    routes: list[tuple[str, str, dict[str, str]]] = []
    for row in rows:
        expected = row.get("expected", "")
        for active in CATEGORIES:
            if active == expected:
                continue
            if as_float(row.get(f"{active}_level", "")) > threshold:
                routes.append((expected, active, row))
    return routes


def summarize_false_routes(
    rows: list[dict[str, str]],
    threshold: float,
    limit: int,
    examples: int,
) -> None:
    routes = false_route_rows(rows, threshold)
    if not routes:
        return
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for expected, active, row in routes:
        grouped.setdefault((expected, active), []).append(row)
    print("top false-active routes:")
    ranked = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
    )
    for (expected, active), route_rows_for_pair in ranked[:limit]:
        print(f"  {route_text(route_rows_for_pair, expected, active)}")
        for row in route_rows_for_pair[:examples]:
            print(
                f"    route sample={row.get('sample', '--')} "
                f"got={row.get('got', '--')} "
                f"{active}_level={as_float(row.get(active + '_level', '')):.3f} "
                f"{expected}_level={expected_level(row):.3f}"
            )


def summarize_category(
    rows: list[dict[str, str]],
    category: str,
    threshold: float,
    examples: int,
    route_limit: int,
) -> None:
    total = [row for row in rows if row.get("expected") == category]
    true_active = [
        row
        for row in total
        if as_float(row.get(f"{category}_level", "")) > threshold
    ]
    active = [
        row
        for row in rows
        if as_float(row.get(f"{category}_level", "")) > threshold
    ]
    false_active = [row for row in active if row.get("expected") != category]
    print(
        f"{category}: recall={len(true_active)}/{len(total)} {pct(len(true_active), len(total)):.2f}% "
        f"precision={len(true_active)}/{len(active)} {pct(len(true_active), len(active)):.2f}% "
        f"false={len(false_active)}"
    )
    print(
        f"  true level_med={median_field(true_active, category + '_level')} "
        f"trigger_med={median_field(true_active, category + '_trigger')} "
        f"seg_med={median_field(true_active, category + '_seg')} "
        f"shape_med={median_field(true_active, category + '_shape')}"
    )
    print(
        f"  false level_med={median_field(false_active, category + '_level')} "
        f"trigger_med={median_field(false_active, category + '_trigger')} "
        f"seg_med={median_field(false_active, category + '_seg')} "
        f"shape_med={median_field(false_active, category + '_shape')} "
        f"expected={compact_counter(Counter(row.get('expected', '') for row in false_active), 5)}"
    )
    for row in false_active[:examples]:
        print(
            f"    false {row.get('expected', '--')}->{category} "
            f"sample={row.get('sample', '--')} level={as_float(row.get(category + '_level', '')):.3f} "
            f"trigger={as_float(row.get(category + '_trigger', '')):.3f}/"
            f"{as_float(row.get(category + '_threshold', '')):.3f} "
            f"seg={as_float(row.get(category + '_seg', '')):.3f} "
            f"shape={row.get(category + '_shape', '--')} got={row.get('got', '--')}"
        )
    if false_active and route_limit > 0:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in false_active:
            grouped.setdefault(row.get("expected", ""), []).append(row)
        routes = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
        print("  false routes:")
        for expected, route_rows_for_expected in routes[:route_limit]:
            print(f"    {route_text(route_rows_for_expected, expected, category)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", type=pathlib.Path)
    parser.add_argument("--threshold", type=float, default=0.30)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--route-limit", type=int, default=5)
    parser.add_argument("--route-examples", type=int, default=1)
    args = parser.parse_args()

    rows = read_rows(args.rows)
    print(f"drum active false rows: rows={len(rows)} threshold={args.threshold:.2f} source={args.rows}")
    for category in CATEGORIES:
        summarize_category(
            rows,
            category,
            args.threshold,
            max(0, args.examples),
            max(0, args.route_limit),
        )
    summarize_false_routes(rows, args.threshold, max(0, args.route_limit), max(0, args.route_examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
