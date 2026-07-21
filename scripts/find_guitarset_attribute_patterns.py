#!/usr/bin/env python3
"""Find candidate GuitarSet chord attribute patterns for a selected bucket."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import pathlib
import statistics
from collections.abc import Callable

from inspect_guitarset_attribute_buckets import (
    CATEGORY_FIELDS,
    NUMERIC_FIELDS,
    as_float_opt,
    bucket_label,
    bucket_matches,
    derive_rows,
    load_rows,
    parse_bucket_spec,
)


@dataclasses.dataclass(frozen=True)
class Pattern:
    label: str
    predicate: Callable[[dict[str, str]], bool]


@dataclasses.dataclass(frozen=True)
class RuleResult:
    rule: str
    positive_rows: int
    positive_recordings: int
    negative_rows: int
    negative_recordings: int
    positives: list[dict[str, str]]


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def thresholds(values: list[float]) -> list[float]:
    if not values:
        return []
    sorted_values = sorted(values)
    candidates = {
        sorted_values[0],
        quantile(sorted_values, 0.25),
        statistics.median(sorted_values),
        quantile(sorted_values, 0.75),
        sorted_values[-1],
    }
    return sorted(candidates)


def format_value(value: float) -> str:
    if abs(value - round(value)) < 1.0e-6 and abs(value) >= 10.0:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def numeric_pattern(field: str, operator: str, threshold: float) -> Pattern:
    if operator == "<=":
        return Pattern(
            f"{field}<={format_value(threshold)}",
            lambda row, field=field, threshold=threshold: (
                (value := as_float_opt(row, field)) is not None and value <= threshold
            ),
        )
    return Pattern(
        f"{field}>={format_value(threshold)}",
        lambda row, field=field, threshold=threshold: (
            (value := as_float_opt(row, field)) is not None and value >= threshold
        ),
    )


def category_pattern(field: str, expected: str) -> Pattern:
    return Pattern(
        f"{field}={expected}",
        lambda row, field=field, expected=expected: row.get(field, "") == expected,
    )


def build_patterns(positive_rows: list[dict[str, str]]) -> list[Pattern]:
    patterns: list[Pattern] = []
    for field in CATEGORY_FIELDS + ["quality"]:
        values = sorted({row.get(field, "") for row in positive_rows if row.get(field, "")})
        for value in values:
            patterns.append(category_pattern(field, value))
    for field in NUMERIC_FIELDS:
        values = [value for row in positive_rows if (value := as_float_opt(row, field)) is not None]
        for threshold in thresholds(values):
            patterns.append(numeric_pattern(field, "<=", threshold))
            patterns.append(numeric_pattern(field, ">=", threshold))

    deduped: list[Pattern] = []
    seen: set[str] = set()
    for pattern in patterns:
        if pattern.label in seen:
            continue
        seen.add(pattern.label)
        deduped.append(pattern)
    return deduped


def recording_count(rows: list[dict[str, str]]) -> int:
    return len({row.get("recording_id", "") for row in rows if row.get("recording_id", "")})


def selected_recordings(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        recording_id = row.get("recording_id", "")
        if recording_id in seen:
            continue
        seen.add(recording_id)
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def combine_patterns(left: Pattern, right: Pattern) -> Pattern:
    return Pattern(
        f"{left.label} AND {right.label}",
        lambda row, left=left, right=right: left.predicate(row) and right.predicate(row),
    )


def evaluate(
    pattern: Pattern,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    max_negative_recordings: int,
    show_examples: int,
) -> RuleResult | None:
    positives = [row for row in positive_rows if pattern.predicate(row)]
    positive_recordings = recording_count(positives)
    if positive_recordings <= 0:
        return None
    negatives = [row for row in negative_rows if pattern.predicate(row)]
    negative_recordings = recording_count(negatives)
    if negative_recordings > max_negative_recordings:
        return None
    return RuleResult(
        rule=pattern.label,
        positive_rows=len(positives),
        positive_recordings=positive_recordings,
        negative_rows=len(negatives),
        negative_recordings=negative_recordings,
        positives=selected_recordings(positives, show_examples),
    )


def rank_result(result: RuleResult) -> tuple[int, int, int, int, str]:
    return (
        result.negative_recordings,
        -result.positive_recordings,
        result.negative_rows,
        result.rule.count(" AND "),
        result.rule,
    )


def format_example(row: dict[str, str]) -> str:
    return (
        f"{row.get('recording_id', '')}@{float(row.get('center_seconds', '0') or 0):.3f}s "
        f"expected={row.get('expected_chords', '--')} guitar={row.get('guitar_chord', '--')} "
        f"support={row.get('support', '')} "
        f"raw(root/third/fifth)={float(row.get('raw_root', '0') or 0):.2f}/"
        f"{float(row.get('raw_third', '0') or 0):.2f}/"
        f"{float(row.get('raw_fifth', '0') or 0):.2f} "
        f"analysis={row.get('guitar_analysis_pitch_classes', '--')} "
        f"visible={row.get('guitar_pitch_classes', '--')}"
    )


def print_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    limit: int,
    min_positive_recordings: int,
    max_negative_recordings: int,
    show_examples: int,
) -> None:
    positive_rows = [row for row in rows if bucket_matches(row, bucket)]
    negative_rows = [row for row in rows if row.get("status") == "chord_hit"]
    print(
        f"bucket {bucket_label(bucket)} positives={recording_count(positive_rows)} "
        f"positive_rows={len(positive_rows)} protected_hits={recording_count(negative_rows)}"
    )
    if not positive_rows:
        return

    base_patterns = build_patterns(positive_rows)
    results: list[RuleResult] = []
    for pattern in base_patterns:
        result = evaluate(pattern, positive_rows, negative_rows, max_negative_recordings, show_examples)
        if result is not None and result.positive_recordings >= min_positive_recordings:
            results.append(result)

    # One pair of conditions is enough for these small diagnostic buckets and keeps
    # the report fast enough to run interactively while tuning the detector.
    for index, left in enumerate(base_patterns):
        for right in base_patterns[index + 1 :]:
            result = evaluate(
                combine_patterns(left, right),
                positive_rows,
                negative_rows,
                max_negative_recordings,
                show_examples,
            )
            if result is not None and result.positive_recordings >= min_positive_recordings:
                results.append(result)

    deduped: dict[str, RuleResult] = {}
    for result in results:
        existing = deduped.get(result.rule)
        if existing is None or rank_result(result) < rank_result(existing):
            deduped[result.rule] = result
    for result in sorted(deduped.values(), key=rank_result)[:limit]:
        print(
            f"  +{result.positive_recordings} rows={result.positive_rows} "
            f"-{result.negative_recordings} rows={result.negative_rows} :: {result.rule}"
        )
        for example in result.positives:
            print("    " + format_example(example))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument(
        "--bucket",
        action="append",
        required=True,
        help="bucket formatted as status:quality:support; repeatable",
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--min-positive-recordings", type=int, default=3)
    parser.add_argument("--max-negative-recordings", type=int, default=0)
    parser.add_argument("--show-examples", type=int, default=3)
    args = parser.parse_args()

    rows = derive_rows(load_rows(pathlib.Path(args.path)))
    for spec in args.bucket:
        print_patterns(
            rows,
            parse_bucket_spec(spec),
            max(1, args.limit),
            max(1, args.min_positive_recordings),
            max(0, args.max_negative_recordings),
            max(0, args.show_examples),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
