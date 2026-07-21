#!/usr/bin/env python3
"""Find candidate attribute patterns in real-note detector TSV exports."""

from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import pathlib
import re
import statistics
from collections.abc import Callable


DEBUG_NUMERIC_FIELDS = [
    "debug_midi",
    "debug_conf",
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
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]

ROW_CONTEXT_NUMERIC_FIELDS = [
    "expected_midi",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
]

DEBUG_CATEGORY_FIELDS = [
    "debug_owner",
]

ROW_CONTEXT_CATEGORY_FIELDS = [
    "buffer_strongest_row",
]

DEFAULT_BUCKETS = [
    "ownership_miss:other/acoustic->guitar",
    "ownership_miss:piano/electronic->guitar",
    "ownership_miss:piano/electronic->bass",
    "ownership_miss:other/acoustic->piano",
    "ownership_miss:guitar/acoustic->piano",
    "ownership_miss:guitar/acoustic->bass",
]


@dataclasses.dataclass(frozen=True)
class Pattern:
    label: str
    category: bool
    predicate: Callable[[dict[str, str]], bool]


@dataclasses.dataclass(frozen=True)
class PatternMatch:
    label: str
    positive_row_mask: int
    negative_row_mask: int
    category: bool


@dataclasses.dataclass(frozen=True)
class RuleResult:
    rule: str
    positive_samples: int
    positive_rows: int
    negative_samples: int
    negative_rows: int
    negative_row_mask: int


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_bucket_spec(spec: str) -> tuple[str, str, str, str]:
    match = re.fullmatch(r"([^:]+):([^/]+)/(.+)->(.+)", spec)
    if not match:
        raise SystemExit(
            f"invalid bucket `{spec}`; expected format status:family/source->first_row"
        )
    return match.group(1), match.group(2), match.group(3), match.group(4)


def bucket_label(bucket: tuple[str, str, str, str]) -> str:
    status, family, source, first_row = bucket
    return f"{status}:{family}/{source}->{first_row}"


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def source_key(row: dict[str, str]) -> str:
    return f"{row.get('family', 'unknown')}/{row.get('source', 'unknown')}"


def rows_for_bucket(rows: list[dict[str, str]], bucket: tuple[str, str, str, str]) -> list[dict[str, str]]:
    status, family, source, first_row = bucket
    return [
        row
        for row in rows
        if row.get("status") == status
        and row.get("family") == family
        and row.get("source") == source
        and row.get("first_row") == first_row
        and row.get("debug_note")
    ]


def hit_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("status") == "hit" and row.get("debug_note")]


def sample_count(rows: list[dict[str, str]]) -> int:
    return len({row.get("sample_id", "") for row in rows if row.get("sample_id", "")})


def sample_bit_map(rows: list[dict[str, str]]) -> tuple[list[int], int]:
    sample_bits: dict[str, int] = {}
    row_bits: list[int] = []
    for row in rows:
        sample_id = row.get("sample_id", "")
        if sample_id not in sample_bits:
            sample_bits[sample_id] = 1 << len(sample_bits)
        row_bits.append(sample_bits[sample_id])
    return row_bits, len(sample_bits)


def mask_for_pattern(rows: list[dict[str, str]], pattern: Pattern) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern.predicate(row):
            mask |= 1 << index
    return mask


def sample_mask_for_rows(row_mask: int, row_sample_bits: list[int]) -> int:
    sample_mask = 0
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        sample_mask |= row_sample_bits[index]
        row_mask ^= bit
    return sample_mask


def sample_count_for_rows(row_mask: int, row_sample_bits: list[int], limit: int | None = None) -> tuple[int, bool]:
    sample_mask = 0
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        sample_mask |= row_sample_bits[index]
        if limit is not None:
            count = sample_mask.bit_count()
            if count > limit:
                return count, True
        row_mask ^= bit
    return sample_mask.bit_count(), False


def summarize_negative_sources_from_mask(
    rows: list[dict[str, str]], row_mask: int, limit: int = 4
) -> str:
    counts: collections.Counter[str] = collections.Counter()
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        counts[source_key(rows[index])] += 1
        row_mask ^= bit
    return ",".join(f"{key}={value}" for key, value in counts.most_common(limit))


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
        quantile(sorted_values, 0.10),
        quantile(sorted_values, 0.25),
        statistics.median(sorted_values),
        quantile(sorted_values, 0.75),
        quantile(sorted_values, 0.90),
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
            False,
            lambda row, field=field, threshold=threshold: (
                (value := as_float(row, field)) is not None and value <= threshold
            ),
        )
    return Pattern(
        f"{field}>={format_value(threshold)}",
        False,
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value >= threshold
        ),
    )


def interval_pattern(field: str, low: float, high: float) -> Pattern:
    return Pattern(
        f"{format_value(low)}<={field}<={format_value(high)}",
        False,
        lambda row, field=field, low=low, high=high: (
            (value := as_float(row, field)) is not None and low <= value <= high
        ),
    )


def category_pattern(field: str, expected: str) -> Pattern:
    return Pattern(
        f"{field}={expected}",
        True,
        lambda row, field=field, expected=expected: row.get(field, "") == expected,
    )


def build_patterns(
    positive_rows: list[dict[str, str]], include_intervals: bool, include_row_context: bool
) -> tuple[list[Pattern], list[Pattern]]:
    category_patterns: list[Pattern] = []
    category_fields = DEBUG_CATEGORY_FIELDS + (
        ROW_CONTEXT_CATEGORY_FIELDS if include_row_context else []
    )
    numeric_fields = DEBUG_NUMERIC_FIELDS + (
        ROW_CONTEXT_NUMERIC_FIELDS if include_row_context else []
    )
    for field in category_fields:
        values = sorted({row.get(field, "") for row in positive_rows if row.get(field, "")})
        for value in values:
            category_patterns.append(category_pattern(field, value))

    numeric_patterns: list[Pattern] = []
    for field in numeric_fields:
        values = [value for row in positive_rows if (value := as_float(row, field)) is not None]
        if not values:
            continue
        for threshold in thresholds(values):
            numeric_patterns.append(numeric_pattern(field, "<=", threshold))
            numeric_patterns.append(numeric_pattern(field, ">=", threshold))

        if include_intervals:
            bounds = thresholds(values)
            for low in bounds[:3]:
                for high in bounds[-3:]:
                    if low < high:
                        numeric_patterns.append(interval_pattern(field, low, high))

    deduped_categories: list[Pattern] = []
    deduped_numerics: list[Pattern] = []
    seen = set()
    for pattern in category_patterns:
        if pattern.label in seen:
            continue
        seen.add(pattern.label)
        deduped_categories.append(pattern)
    seen.clear()
    for pattern in numeric_patterns:
        if pattern.label in seen:
            continue
        seen.add(pattern.label)
        deduped_numerics.append(pattern)
    return deduped_categories, deduped_numerics


def indexed_match(
    pattern: Pattern,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
) -> PatternMatch:
    return PatternMatch(
        label=pattern.label,
        positive_row_mask=mask_for_pattern(positive_rows, pattern),
        negative_row_mask=mask_for_pattern(negative_rows, pattern),
        category=pattern.category,
    )


def result_from_masks(
    label: str,
    positive_row_mask: int,
    negative_row_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    max_negative_samples: int,
) -> RuleResult | None:
    positive_samples, _positive_exceeded = sample_count_for_rows(
        positive_row_mask, positive_sample_bits
    )
    negative_samples, negative_exceeded = sample_count_for_rows(
        negative_row_mask, negative_sample_bits, max_negative_samples
    )
    if negative_exceeded:
        return None
    return RuleResult(
        rule=label,
        positive_samples=positive_samples,
        positive_rows=positive_row_mask.bit_count(),
        negative_samples=negative_samples,
        negative_rows=negative_row_mask.bit_count(),
        negative_row_mask=negative_row_mask,
    )


def print_bucket_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    include_intervals: bool,
    include_row_context: bool,
) -> None:
    positive_rows = rows_for_bucket(rows, bucket)
    negatives = hit_rows(rows)
    positive_samples = sample_count(positive_rows)
    negative_samples = sample_count(negatives)
    print()
    print(
        f"{bucket_label(bucket)} positives={positive_samples} samples/{len(positive_rows)} rows "
        f"protected_hits={negative_samples} samples/{len(negatives)} rows"
    )
    if not positive_rows:
        return

    positive_sample_bits, _positive_sample_count = sample_bit_map(positive_rows)
    negative_sample_bits, _negative_sample_count = sample_bit_map(negatives)
    category_patterns, numeric_patterns = build_patterns(
        positive_rows, include_intervals, include_row_context
    )
    category_matches = [
        indexed_match(pattern, positive_rows, negatives) for pattern in category_patterns
    ]
    numeric_matches = [
        indexed_match(pattern, positive_rows, negatives) for pattern in numeric_patterns
    ]

    def add_result(label: str, positive_row_mask: int, negative_row_mask: int) -> None:
        result = result_from_masks(
            label,
            positive_row_mask,
            negative_row_mask,
            positive_rows,
            negatives,
            positive_sample_bits,
            negative_sample_bits,
            max_negative_samples,
        )
        if result is None:
            return
        if result.positive_samples < min_positive_samples:
            return
        results.append(result)

    results: list[RuleResult] = []
    for match in [*category_matches, *numeric_matches]:
        add_result(match.label, match.positive_row_mask, match.negative_row_mask)
    for category in category_matches:
        for numeric in numeric_matches:
            add_result(
                f"{category.label} AND {numeric.label}",
                category.positive_row_mask & numeric.positive_row_mask,
                category.negative_row_mask & numeric.negative_row_mask,
            )

    low_false = sorted(
        results,
        key=lambda result: (
            result.negative_samples,
            -result.positive_samples,
            result.negative_rows,
            result.rule,
        ),
    )[:limit]
    coverage = sorted(
        results,
        key=lambda result: (
            -result.positive_samples,
            result.negative_samples,
            -result.positive_rows,
            result.rule,
        ),
    )[:limit]

    print("  low-false candidate rules:")
    print_results(low_false, positive_samples, negative_samples, negatives)
    print("  highest-coverage candidate rules:")
    print_results(coverage, positive_samples, negative_samples, negatives)


def print_results(
    results: list[RuleResult],
    positive_total: int,
    negative_total: int,
    negative_rows: list[dict[str, str]],
) -> None:
    if not results:
        print("    --")
        return
    for result in results:
        negative_sources = summarize_negative_sources_from_mask(
            negative_rows, result.negative_row_mask
        )
        print(
            f"    {result.rule}: pos={result.positive_samples}/{positive_total} "
            f"rows={result.positive_rows} neg={result.negative_samples}/{negative_total} "
            f"rows={result.negative_rows}"
            + (f" neg_sources={negative_sources}" if negative_sources else "")
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="ownership-miss bucket formatted as status:family/source->first_row; repeatable",
    )
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--min-positive-samples", type=int, default=2)
    parser.add_argument("--max-negative-samples", type=int, default=25)
    parser.add_argument(
        "--include-intervals",
        action="store_true",
        help="also test bounded numeric intervals; slower and noisier but useful for manual deep dives",
    )
    parser.add_argument(
        "--include-row-context",
        action="store_true",
        help="also test display-row context fields such as first visible row and per-row levels",
    )
    args = parser.parse_args()

    rows = load_rows(pathlib.Path(args.path))
    buckets = [parse_bucket_spec(spec) for spec in (args.bucket or DEFAULT_BUCKETS)]
    for bucket in buckets:
        print_bucket_patterns(
            rows,
            bucket,
            max(1, args.limit),
            max(1, args.min_positive_samples),
            max(0, args.max_negative_samples),
            args.include_intervals,
            args.include_row_context,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
