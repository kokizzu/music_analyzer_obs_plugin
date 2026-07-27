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
    top_bucket_keys,
)


OUTCOME_NUMERIC_FIELDS = {
    "chord_hit",
    "simple_chord_hit",
    "guitar_chord_hit",
    "expected_label_in_display",
    "expected_label_in_raw",
    "expected_label_in_smooth",
}
PATTERN_NUMERIC_FIELDS = [field for field in NUMERIC_FIELDS if field not in OUTCOME_NUMERIC_FIELDS]
RUNTIME_NUMERIC_FIELDS = [
    "rms",
    "low",
    "mid",
    "high",
    "guitar_pc_count",
    "analysis_pc_count",
    "smooth_pc_count",
]
RUNTIME_CATEGORY_FIELDS: list[str] = []


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


@dataclasses.dataclass(frozen=True)
class PatternMatch:
    label: str
    positive_mask: int
    negative_mask: int


@dataclasses.dataclass(frozen=True)
class SearchState:
    labels: tuple[str, ...]
    positive_mask: int
    negative_mask: int
    next_match_index: int


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


def build_patterns(positive_rows: list[dict[str, str]], *, runtime_only: bool = False) -> list[Pattern]:
    patterns: list[Pattern] = []
    category_fields = RUNTIME_CATEGORY_FIELDS if runtime_only else CATEGORY_FIELDS + ["quality"]
    numeric_fields = RUNTIME_NUMERIC_FIELDS if runtime_only else PATTERN_NUMERIC_FIELDS
    for field in category_fields:
        values = sorted({row.get(field, "") for row in positive_rows if row.get(field, "")})
        for value in values:
            patterns.append(category_pattern(field, value))
    for field in numeric_fields:
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


def recording_bit_map(rows: list[dict[str, str]]) -> list[int]:
    bits: dict[str, int] = {}
    row_bits: list[int] = []
    for row in rows:
        recording_id = row.get("recording_id", "")
        if recording_id not in bits:
            bits[recording_id] = 1 << len(bits)
        row_bits.append(bits[recording_id])
    return row_bits


def mask_for_pattern(rows: list[dict[str, str]], pattern: Pattern) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern.predicate(row):
            mask |= 1 << index
    return mask


def recording_count_for_mask(row_mask: int, row_bits: list[int], limit: int | None = None) -> tuple[int, bool]:
    recording_mask = 0
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        recording_mask |= row_bits[index]
        if limit is not None:
            count = recording_mask.bit_count()
            if count > limit:
                return count, True
        row_mask ^= bit
    return recording_mask.bit_count(), False


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


def selected_recordings_from_mask(
    rows: list[dict[str, str]], row_mask: int, limit: int
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    while row_mask and len(selected) < limit:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        recording_id = row.get("recording_id", "")
        if recording_id not in seen:
            seen.add(recording_id)
            selected.append(row)
        row_mask ^= bit
    return selected


def result_from_masks(
    rule: str,
    positive_mask: int,
    negative_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_recording_bits: list[int],
    negative_recording_bits: list[int],
    max_negative_recordings: int,
    show_examples: int,
) -> RuleResult | None:
    positive_recordings, _positive_exceeded = recording_count_for_mask(
        positive_mask, positive_recording_bits
    )
    if positive_recordings <= 0:
        return None
    negative_recordings, negative_exceeded = recording_count_for_mask(
        negative_mask, negative_recording_bits, max_negative_recordings
    )
    if negative_exceeded:
        return None
    return RuleResult(
        rule=rule,
        positive_rows=positive_mask.bit_count(),
        positive_recordings=positive_recordings,
        negative_rows=negative_mask.bit_count(),
        negative_recordings=negative_recordings,
        positives=selected_recordings_from_mask(positive_rows, positive_mask, show_examples),
    )


def rank_result(result: RuleResult) -> tuple[int, int, int, int, str]:
    return (
        result.negative_recordings,
        -result.positive_recordings,
        result.negative_rows,
        result.rule.count(" AND "),
        result.rule,
    )


def bounded_recording_count(row_mask: int, row_bits: list[int], max_recordings: int | None) -> int:
    count, exceeded = recording_count_for_mask(row_mask, row_bits, max_recordings)
    if exceeded and max_recordings is not None:
        return max_recordings + 1
    return count


def ranked_state_key(
    state: SearchState,
    positive_recording_bits: list[int],
    negative_recording_bits: list[int],
    max_negative_recordings: int,
) -> tuple[int, int, int, int, str]:
    negative_recordings = bounded_recording_count(
        state.negative_mask, negative_recording_bits, max_negative_recordings
    )
    positive_recordings = bounded_recording_count(state.positive_mask, positive_recording_bits, None)
    return (
        negative_recordings,
        -positive_recordings,
        state.negative_mask.bit_count(),
        len(state.labels),
        " AND ".join(state.labels),
    )


def extend_condition_search(
    matches: list[PatternMatch],
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_recording_bits: list[int],
    negative_recording_bits: list[int],
    min_positive_recordings: int,
    max_negative_recordings: int,
    max_conditions: int,
    beam_width: int,
    show_examples: int,
) -> list[RuleResult]:
    if max_conditions < 2 or not matches:
        return []

    ordered = sorted(matches, key=lambda match: match.label)
    states: list[SearchState] = []
    for index, match in enumerate(ordered):
        positive_recordings = bounded_recording_count(
            match.positive_mask, positive_recording_bits, None
        )
        if positive_recordings < min_positive_recordings:
            continue
        states.append(
            SearchState(
                labels=(match.label,),
                positive_mask=match.positive_mask,
                negative_mask=match.negative_mask,
                next_match_index=index + 1,
            )
        )

    results: list[RuleResult] = []
    seen_results: set[tuple[int, int]] = set()
    for condition_count in range(2, max(2, max_conditions) + 1):
        next_states_by_mask: dict[tuple[int, int], SearchState] = {}
        for state in states:
            for match_index in range(state.next_match_index, len(ordered)):
                match = ordered[match_index]
                positive_mask = state.positive_mask & match.positive_mask
                if positive_mask == 0:
                    continue
                positive_recordings = bounded_recording_count(
                    positive_mask, positive_recording_bits, None
                )
                if positive_recordings < min_positive_recordings:
                    continue
                negative_mask = state.negative_mask & match.negative_mask
                candidate = SearchState(
                    labels=state.labels + (match.label,),
                    positive_mask=positive_mask,
                    negative_mask=negative_mask,
                    next_match_index=match_index + 1,
                )
                mask_key = (positive_mask, negative_mask)
                existing = next_states_by_mask.get(mask_key)
                if existing is None or ranked_state_key(
                    candidate,
                    positive_recording_bits,
                    negative_recording_bits,
                    max_negative_recordings,
                ) < ranked_state_key(
                    existing,
                    positive_recording_bits,
                    negative_recording_bits,
                    max_negative_recordings,
                ):
                    next_states_by_mask[mask_key] = candidate

        states = sorted(
            next_states_by_mask.values(),
            key=lambda state: ranked_state_key(
                state,
                positive_recording_bits,
                negative_recording_bits,
                max_negative_recordings,
            ),
        )[: max(1, beam_width)]
        for state in states:
            result_key = (state.positive_mask, state.negative_mask)
            if result_key in seen_results:
                continue
            seen_results.add(result_key)
            result = result_from_masks(
                " AND ".join(state.labels),
                state.positive_mask,
                state.negative_mask,
                positive_rows,
                negative_rows,
                positive_recording_bits,
                negative_recording_bits,
                max_negative_recordings,
                show_examples,
            )
            if result is not None:
                results.append(result)
        if not states:
            break
    return results


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
    protected_source_rows: list[dict[str, str]],
    protected_buckets: list[tuple[str, str, str]],
    bucket: tuple[str, str, str],
    limit: int,
    min_positive_recordings: int,
    max_negative_recordings: int,
    show_examples: int,
    max_conditions: int,
    beam_width: int,
    runtime_only: bool,
) -> None:
    positive_rows = [row for row in rows if bucket_matches(row, bucket)]
    if protected_buckets:
        negative_rows = [
            row
            for row in protected_source_rows
            if any(bucket_matches(row, protected_bucket) for protected_bucket in protected_buckets)
        ]
    else:
        negative_rows = [row for row in protected_source_rows if row.get("status") == "chord_hit"]
    print(
        f"bucket {bucket_label(bucket)} positives={recording_count(positive_rows)} "
        f"positive_rows={len(positive_rows)} protected_hits={recording_count(negative_rows)}"
    )
    if not positive_rows:
        return

    base_patterns = build_patterns(positive_rows, runtime_only=runtime_only)
    positive_recording_bits = recording_bit_map(positive_rows)
    negative_recording_bits = recording_bit_map(negative_rows)
    results: list[RuleResult] = []
    for pattern in base_patterns:
        result = evaluate(pattern, positive_rows, negative_rows, max_negative_recordings, show_examples)
        if result is not None and result.positive_recordings >= min_positive_recordings:
            results.append(result)

    matches = [
        PatternMatch(
            label=pattern.label,
            positive_mask=mask_for_pattern(positive_rows, pattern),
            negative_mask=mask_for_pattern(negative_rows, pattern),
        )
        for pattern in base_patterns
    ]
    results.extend(
        extend_condition_search(
            matches,
            positive_rows,
            negative_rows,
            positive_recording_bits,
            negative_recording_bits,
            min_positive_recordings,
            max_negative_recordings,
            max(2, max_conditions),
            max(1, beam_width),
            show_examples,
        )
    )

    deduped: dict[str, RuleResult] = {}
    for result in results:
        existing = deduped.get(result.rule)
        if existing is None or rank_result(result) < rank_result(existing):
            deduped[result.rule] = result
    ranked_results = sorted(deduped.values(), key=rank_result)[:limit]
    if not ranked_results:
        print("  --")
        return
    for result in ranked_results:
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
        default=[],
        help="bucket formatted as status:quality:support; repeatable",
    )
    parser.add_argument(
        "--protected-path",
        action="append",
        default=[],
        help="additional attribute TSV to use for protected negative rows; repeatable",
    )
    parser.add_argument(
        "--protected-bucket",
        action="append",
        default=[],
        help=(
            "protected bucket formatted as status:quality:support; repeatable. "
            "Defaults to chord_hit rows from the selected protected path(s), or the main path."
        ),
    )
    parser.add_argument(
        "--top-buckets",
        type=int,
        default=4,
        help="when --bucket is omitted, mine this many largest chord-miss buckets; 0 disables auto buckets",
    )
    parser.add_argument(
        "--limit",
        "--max-patterns",
        dest="limit",
        type=int,
        default=12,
        help="maximum patterns to print per bucket",
    )
    parser.add_argument(
        "--min-positive-recordings",
        "--min-support",
        dest="min_positive_recordings",
        type=int,
        default=3,
        help="minimum positive recordings a printed pattern must cover",
    )
    parser.add_argument("--max-negative-recordings", type=int, default=0)
    parser.add_argument("--show-examples", "--row-examples", dest="show_examples", type=int, default=3)
    parser.add_argument(
        "--max-conditions",
        type=int,
        default=2,
        help="maximum number of ANDed auto-search conditions; values above 2 use bounded beam search",
    )
    parser.add_argument(
        "--beam-width",
        type=int,
        default=180,
        help="number of partial multi-condition rules retained per search depth",
    )
    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help="mine only runtime-observable count and energy fields, excluding ground-truth labels and outcomes",
    )
    args = parser.parse_args()

    rows = derive_rows(load_rows(pathlib.Path(args.path)))
    protected_source_rows = rows
    if args.protected_path:
        protected_source_rows = []
        for protected_path in args.protected_path:
            protected_source_rows.extend(derive_rows(load_rows(pathlib.Path(protected_path))))
    protected_buckets = [parse_bucket_spec(spec) for spec in args.protected_bucket]
    buckets = [parse_bucket_spec(spec) for spec in args.bucket]
    if not buckets and args.top_buckets > 0:
        buckets = top_bucket_keys(rows, args.top_buckets, include_comparisons=False)
    if not buckets:
        print("find_guitarset_attribute_patterns: no chord buckets selected")
        return 0
    for bucket in buckets:
        print_patterns(
            rows,
            protected_source_rows,
            protected_buckets,
            bucket,
            max(1, args.limit),
            max(1, args.min_positive_recordings),
            max(0, args.max_negative_recordings),
            max(0, args.show_examples),
            max(1, args.max_conditions),
            max(1, args.beam_width),
            args.runtime_only,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
