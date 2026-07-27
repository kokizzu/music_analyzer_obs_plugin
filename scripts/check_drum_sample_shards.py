#!/usr/bin/env python3
"""Aggregate analyzer_drum_samples category shards and validate full-gate thresholds."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
MATRIX_RE = re.compile(r"^analyzer_drum_samples: (?P<kind>active|primary) matrix$")
ROW_RE = re.compile(r"^\s*expected\s+(?P<expected>\w+)\s+(?P<counts>.+)$")
OK_RE = re.compile(r"^analyzer_drum_samples: ok \((?P<body>.+)\)$")


def empty_matrix() -> dict[str, dict[str, int]]:
    return {expected: {detected: 0 for detected in CATEGORIES} for expected in CATEGORIES}


def parse_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for token in text.split():
        if "=" not in token:
            continue
        label, value = token.split("=", 1)
        try:
            counts[label] = int(value)
        except ValueError:
            continue
    return counts


def parse_shard(path: pathlib.Path) -> tuple[int, dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    active = empty_matrix()
    primary = empty_matrix()
    skipped = 0
    current: str | None = None
    for line in path.read_text(errors="replace").splitlines():
        ok_match = OK_RE.match(line)
        if ok_match:
            header = re.search(r"\bskipped (?P<skipped>\d+)", ok_match.group("body"))
            if header:
                skipped += int(header.group("skipped"))
            continue
        matrix_match = MATRIX_RE.match(line)
        if matrix_match:
            current = matrix_match.group("kind")
            continue
        row_match = ROW_RE.match(line)
        if current is None or not row_match:
            continue
        expected = row_match.group("expected")
        if expected not in CATEGORIES:
            continue
        target = active if current == "active" else primary
        for label, value in parse_counts(row_match.group("counts")).items():
            if label in CATEGORIES or label in {"ambiguous", "none"}:
                target.setdefault(expected, {})[label] = target.setdefault(expected, {}).get(label, 0) + value
    return skipped, active, primary


def add_matrix(total: dict[str, dict[str, int]], part: dict[str, dict[str, int]]) -> None:
    for expected, counts in part.items():
        for label, value in counts.items():
            total.setdefault(expected, {})[label] = total.setdefault(expected, {}).get(label, 0) + value


def percent(hit: int, total: int) -> int:
    return hit * 100 // total if total > 0 else 0


def fail(message: str) -> None:
    print(f"check_drum_sample_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def threshold(args: argparse.Namespace, name: str, category: str) -> int:
    value = getattr(args, f"{category}_{name}")
    if value is not None:
        return value
    return getattr(args, name)


def validate(args: argparse.Namespace, skipped: int, active: dict[str, dict[str, int]],
             primary: dict[str, dict[str, int]]) -> None:
    totals = {category: sum(primary.get(category, {}).values()) for category in CATEGORIES}
    usable = sum(totals.values())
    for category in CATEGORIES:
        total = totals[category]
        if total < 2:
            fail(f"expected at least two usable {category} samples, got {total}")
        active_hit = active.get(category, {}).get(category, 0)
        primary_hit = primary.get(category, {}).get(category, 0)
        active_total = sum(active.get(expected, {}).get(category, 0) for expected in CATEGORIES)
        false_total = active_total - active_hit
        recall = percent(active_hit, total)
        primary_recall = percent(primary_hit, total)
        precision = percent(active_hit, active_total)
        non_category_total = max(0, usable - total)
        false_percent = percent(false_total, non_category_total)

        min_recall = threshold(args, "min_recall_percent", category)
        min_primary = threshold(args, "min_primary_recall_percent", category)
        min_precision = args.min_precision_percent
        max_false = threshold(args, "max_false_percent", category)
        if recall < min_recall:
            fail(
                f"expected 100ms {category} recall >= {min_recall}%, got "
                f"{recall}% ({active_hit}/{total})"
            )
        if primary_recall < min_primary:
            fail(
                f"expected 100ms {category} primary recall >= {min_primary}%, got "
                f"{primary_recall}% ({primary_hit}/{total})"
            )
        if min_precision > 0 and precision < min_precision:
            fail(
                f"expected 100ms {category} precision >= {min_precision}%, got "
                f"{precision}% ({active_hit}/{active_total}, false {false_total})"
            )
        if false_percent > max_false:
            fail(
                f"expected 100ms {category} false activations <= {max_false}%, got "
                f"{false_percent}% ({false_total}/{non_category_total})"
            )

    print("check_drum_sample_shards: active matrix")
    for expected in CATEGORIES:
        print(
            f"  expected {expected:<5}"
            + "".join(f" {detected}={active.get(expected, {}).get(detected, 0)}" for detected in CATEGORIES)
        )
    print("check_drum_sample_shards: primary matrix")
    for expected in CATEGORIES:
        row = primary.get(expected, {})
        print(
            f"  expected {expected:<5}"
            + "".join(f" {detected}={row.get(detected, 0)}" for detected in CATEGORIES)
            + f" ambiguous={row.get('ambiguous', 0)} none={row.get('none', 0)}"
        )
    primary_confusion: Counter[str] = Counter()
    for expected in CATEGORIES:
        for detected, value in primary.get(expected, {}).items():
            if value <= 0 or detected == expected:
                continue
            primary_confusion[f"{expected}->{detected}"] += value
    if primary_confusion:
        print(
            "check_drum_sample_shards: primary confusion "
            + " ".join(f"{route}={value}" for route, value in primary_confusion.most_common(12))
        )
    print(f"check_drum_sample_shards: ok (usable {usable}, skipped {skipped}", end="")
    for category in CATEGORIES:
        total = totals[category]
        active_hit = active.get(category, {}).get(category, 0)
        primary_hit = primary.get(category, {}).get(category, 0)
        active_total = sum(active.get(expected, {}).get(category, 0) for expected in CATEGORIES)
        false_total = active_total - active_hit
        precision = percent(active_hit, active_total)
        print(
            f", {category} recall {active_hit}/{total} primary {primary_hit}/{total} "
            f"precision {active_hit}/{active_total} false {false_total} {precision}%",
            end="",
        )
    print(")")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-recall-percent", type=int, default=35)
    parser.add_argument("--min-precision-percent", type=int, default=3)
    parser.add_argument("--min-primary-recall-percent", type=int, default=0)
    parser.add_argument("--max-false-percent", type=int, default=100)
    for category in CATEGORIES:
        parser.add_argument(f"--{category}-min-recall-percent", type=int)
        parser.add_argument(f"--{category}-min-primary-recall-percent", type=int)
        parser.add_argument(f"--{category}-max-false-percent", type=int)
    args = parser.parse_args()

    active = empty_matrix()
    primary = {expected: {detected: 0 for detected in (*CATEGORIES, "ambiguous", "none")}
               for expected in CATEGORIES}
    skipped = 0
    for path in args.logs:
        shard_skipped, shard_active, shard_primary = parse_shard(path)
        skipped += shard_skipped
        add_matrix(active, shard_active)
        add_matrix(primary, shard_primary)
    validate(args, skipped, active, primary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
