#!/usr/bin/env python3
"""Find candidate attribute patterns in generated instrument owner debug rows."""

from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import pathlib
import re
import statistics
from collections.abc import Callable


NUMERIC_FIELDS = [
    "midi",
    "window_ms",
    "detected_expected_row",
    "detected_anywhere",
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "rms",
    "low",
    "mid",
    "high",
    "raw_expected_peak",
    "raw_expected_ratio",
    "raw_tuned_peak",
    "raw_tuned_ratio",
    "raw_tuned_cent_offset",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_midi",
    "raw_local_best_peak",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
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

CATEGORY_FIELDS = [
    "program_name",
    "note",
    "debug_note",
    "debug_owner",
    "raw_local_best_note",
    "bass_label",
    "piano_label",
    "guitar_label",
    "vocal_label",
    "other_label",
]

DEFAULT_BUCKETS = [
    "owner_miss:guitar->piano",
    "owner_miss:guitar->other",
    "owner_miss:piano->guitar",
    "owner_miss:piano->other",
    "owner_miss:vocals->other",
    "owner_miss:strings->guitar",
    "owner_miss:strings->piano",
    "owner_miss:synth->guitar",
    "owner_miss:synth->piano",
]


@dataclasses.dataclass(frozen=True)
class Pattern:
    label: str
    predicate: Callable[[dict[str, str]], bool]


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


@dataclasses.dataclass(frozen=True)
class RuleResult:
    rule: str
    positive_mask: int
    positive_rows: int
    positive_samples: int
    negative_mask: int
    negative_rows: int
    negative_samples: int


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    derived: list[dict[str, str]] = []
    for row in rows:
        if row.get("kind") != "note" or not row.get("debug_note"):
            continue
        row = dict(row)
        row["_owner_target"] = owner_target(row)
        row["_owner_status"] = owner_status(row)
        if row["_owner_status"] in {"owner_hit", "owner_miss", "bass_debug"}:
            derived.append(row)
    return derived


def owner_target(row: dict[str, str]) -> str:
    family = row.get("family", "") or row.get("expected_family", "")
    if family == "piano":
        return "piano"
    if family == "guitar":
        return "guitar"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth"}:
        return "other"
    if family == "bass":
        return "bass-display"
    return family or "unknown"


def owner_status(row: dict[str, str]) -> str:
    target = owner_target(row)
    owner = row.get("debug_owner", "") or "none"
    if target == "bass-display":
        return "bass_debug"
    return "owner_hit" if owner == target else "owner_miss"


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_bucket_spec(spec: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"([^:]+):([^>]+)->(.+)", spec)
    if not match:
        raise SystemExit(f"invalid bucket `{spec}`; expected format owner_miss:guitar->piano")
    return match.group(1), match.group(2), match.group(3)


def bucket_label(bucket: tuple[str, str, str]) -> str:
    status, family, owner = bucket
    return f"{status}:{family}->{owner}"


def rows_for_bucket(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> list[dict[str, str]]:
    status, family, owner = bucket
    return [
        row
        for row in rows
        if row.get("_owner_status") == status
        and row.get("family") == family
        and (row.get("debug_owner", "") or "none") == owner
    ]


def hit_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("_owner_status") == "owner_hit"]


def sample_id(row: dict[str, str]) -> str:
    return (
        row.get("path", "")
        or f"{row.get('family', '')}:{row.get('program_name', '')}:{row.get('note', '')}"
    )


def sample_count(rows: list[dict[str, str]]) -> int:
    return len({sample_id(row) for row in rows if sample_id(row)})


def sample_bit_map(rows: list[dict[str, str]]) -> list[int]:
    bits: dict[str, int] = {}
    row_bits: list[int] = []
    for row in rows:
        key = sample_id(row)
        if key not in bits:
            bits[key] = 1 << len(bits)
        row_bits.append(bits[key])
    return row_bits


def sample_count_for_mask(row_mask: int, row_bits: list[int], limit: int | None = None) -> tuple[int, bool]:
    sample_mask = 0
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        sample_mask |= row_bits[index]
        if limit is not None:
            count = sample_mask.bit_count()
            if count > limit:
                return count, True
        row_mask ^= bit
    return sample_mask.bit_count(), False


def bounded_sample_count(row_mask: int, row_bits: list[int], limit: int | None) -> int:
    count, exceeded = sample_count_for_mask(row_mask, row_bits, limit)
    if exceeded and limit is not None:
        return limit + 1
    return count


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def thresholds(values: list[float]) -> list[float]:
    if not values:
        return []
    sorted_values = sorted(values)
    return sorted(
        {
            sorted_values[0],
            quantile(sorted_values, 0.10),
            quantile(sorted_values, 0.25),
            statistics.median(sorted_values),
            quantile(sorted_values, 0.75),
            quantile(sorted_values, 0.90),
            sorted_values[-1],
        }
    )


def format_value(value: float) -> str:
    if abs(value - round(value)) < 1.0e-6 and abs(value) >= 10.0:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def numeric_pattern(field: str, operator: str, threshold: float) -> Pattern:
    if operator == "<=":
        return Pattern(
            f"{field}<={format_value(threshold)}",
            lambda row, field=field, threshold=threshold: (
                (value := as_float(row, field)) is not None and value <= threshold
            ),
        )
    return Pattern(
        f"{field}>={format_value(threshold)}",
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value >= threshold
        ),
    )


def category_pattern(field: str, expected: str) -> Pattern:
    return Pattern(
        f"{field}={expected}",
        lambda row, field=field, expected=expected: row.get(field, "") == expected,
    )


def condition_pattern(spec: str) -> Pattern:
    match = re.fullmatch(r"([A-Za-z0-9_]+)(<=|>=|<|>|=)(.+)", spec)
    if not match:
        raise SystemExit(
            f"invalid condition `{spec}`; expected field<=value, field>=value, field<value, field>value, or field=value"
        )
    field, operator, raw_value = match.groups()
    value = raw_value.strip()
    if operator == "=":
        return category_pattern(field, value)
    try:
        threshold = float(value)
    except ValueError as exc:
        raise SystemExit(f"invalid numeric threshold in condition `{spec}`") from exc
    if operator == "<=":
        return numeric_pattern(field, "<=", threshold)
    if operator == ">=":
        return numeric_pattern(field, ">=", threshold)
    if operator == "<":
        return Pattern(
            f"{field}<{format_value(threshold)}",
            lambda row, field=field, threshold=threshold: (
                (value := as_float(row, field)) is not None and value < threshold
            ),
        )
    return Pattern(
        f"{field}>{format_value(threshold)}",
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value > threshold
        ),
    )


def build_patterns(positive_rows: list[dict[str, str]]) -> list[Pattern]:
    patterns: list[Pattern] = []
    for field in CATEGORY_FIELDS:
        for value in sorted({row.get(field, "") for row in positive_rows if row.get(field, "")}):
            patterns.append(category_pattern(field, value))
    for field in NUMERIC_FIELDS:
        values = [value for row in positive_rows if (value := as_float(row, field)) is not None]
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


def mask_for_pattern(rows: list[dict[str, str]], pattern: Pattern) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern.predicate(row):
            mask |= 1 << index
    return mask


def selected_examples(rows: list[dict[str, str]], row_mask: int, limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    while row_mask and len(selected) < limit:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        key = sample_id(row)
        if key not in seen:
            seen.add(key)
            selected.append(row)
        row_mask ^= bit
    return selected


def result_from_masks(
    rule: str,
    positive_mask: int,
    negative_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_bits: list[int],
    negative_bits: list[int],
    max_negative_samples: int | None,
) -> RuleResult | None:
    positive_samples, _positive_exceeded = sample_count_for_mask(positive_mask, positive_bits)
    if positive_samples <= 0:
        return None
    negative_samples, negative_exceeded = sample_count_for_mask(
        negative_mask, negative_bits, max_negative_samples
    )
    if negative_exceeded:
        return None
    return RuleResult(
        rule=rule,
        positive_mask=positive_mask,
        positive_rows=positive_mask.bit_count(),
        positive_samples=positive_samples,
        negative_mask=negative_mask,
        negative_rows=negative_mask.bit_count(),
        negative_samples=negative_samples,
    )


def ranked_state_key(
    state: SearchState,
    positive_bits: list[int],
    negative_bits: list[int],
    max_negative_samples: int,
) -> tuple[int, int, int, int, str]:
    return (
        bounded_sample_count(state.negative_mask, negative_bits, max_negative_samples),
        -bounded_sample_count(state.positive_mask, positive_bits, None),
        state.negative_mask.bit_count(),
        len(state.labels),
        " AND ".join(state.labels),
    )


def extend_condition_search(
    matches: list[PatternMatch],
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_bits: list[int],
    negative_bits: list[int],
    min_positive_samples: int,
    max_negative_samples: int,
    max_conditions: int,
    beam_width: int,
) -> list[RuleResult]:
    if max_conditions < 2 or not matches:
        return []

    ordered = sorted(matches, key=lambda match: match.label)
    states: list[SearchState] = []
    for index, match in enumerate(ordered):
        if bounded_sample_count(match.positive_mask, positive_bits, None) < min_positive_samples:
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
    for _condition_count in range(2, max(2, max_conditions) + 1):
        next_states: dict[tuple[int, int], SearchState] = {}
        for state in states:
            for match_index in range(state.next_match_index, len(ordered)):
                match = ordered[match_index]
                positive_mask = state.positive_mask & match.positive_mask
                if positive_mask == 0:
                    continue
                if bounded_sample_count(positive_mask, positive_bits, None) < min_positive_samples:
                    continue
                negative_mask = state.negative_mask & match.negative_mask
                candidate = SearchState(
                    labels=state.labels + (match.label,),
                    positive_mask=positive_mask,
                    negative_mask=negative_mask,
                    next_match_index=match_index + 1,
                )
                key = (positive_mask, negative_mask)
                existing = next_states.get(key)
                if existing is None or ranked_state_key(
                    candidate, positive_bits, negative_bits, max_negative_samples
                ) < ranked_state_key(existing, positive_bits, negative_bits, max_negative_samples):
                    next_states[key] = candidate
        states = sorted(
            next_states.values(),
            key=lambda state: ranked_state_key(state, positive_bits, negative_bits, max_negative_samples),
        )[: max(1, beam_width)]
        for state in states:
            key = (state.positive_mask, state.negative_mask)
            if key in seen_results:
                continue
            seen_results.add(key)
            result = result_from_masks(
                " AND ".join(state.labels),
                state.positive_mask,
                state.negative_mask,
                positive_rows,
                negative_rows,
                positive_bits,
                negative_bits,
                max_negative_samples,
            )
            if result is not None:
                results.append(result)
        if not states:
            break
    return results


def rank_result(result: RuleResult) -> tuple[int, int, int, int, str]:
    return (
        result.negative_samples,
        -result.positive_samples,
        result.negative_rows,
        result.rule.count(" AND "),
        result.rule,
    )


def compact_sources(rows: list[dict[str, str]], row_mask: int, limit: int = 4) -> str:
    counts: collections.Counter[str] = collections.Counter()
    while row_mask:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        counts[f"{row.get('family', '')}->{row.get('debug_owner', '') or 'none'}"] += 1
        row_mask ^= bit
    return ",".join(f"{key}={value}" for key, value in counts.most_common(limit))


def short_float(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "-"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def format_example(row: dict[str, str]) -> str:
    scores = (
        short_float(row, "keyboard_score"),
        short_float(row, "guitar_score"),
        short_float(row, "vocal_score"),
        short_float(row, "other_score"),
    )
    partials = (
        short_float(row, "partial2"),
        short_float(row, "partial3"),
        short_float(row, "partial4"),
        short_float(row, "partial5"),
    )
    return (
        f"{row.get('family', '')} {row.get('program_name', '')} {row.get('note', '')} "
        f"path={row.get('path', '')} target={row.get('_owner_target', '')} "
        f"owner={row.get('debug_owner', '') or 'none'} debug={row.get('debug_note', '')}"
        f" scores(k/g/v/o)={scores[0]}/{scores[1]}/{scores[2]}/{scores[3]}"
        f" spec={short_float(row, 'spectral_level')} pitch={short_float(row, 'pitch_confidence')}"
        f" per={short_float(row, 'periodicity')} fit={short_float(row, 'fit_error')}"
        f" raw={short_float(row, 'raw_expected_ratio')}/{short_float(row, 'raw_tuned_ratio')}"
        f" raw_best={row.get('raw_local_best_note', '')}/{short_float(row, 'raw_local_best_peak')}"
        f" raw_rank={short_float(row, 'raw_expected_rank')} p2..p5={partials[0]},{partials[1]},{partials[2]},{partials[3]}"
    )


def print_results(
    results: list[RuleResult],
    positive_total: int,
    negative_total: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    show_examples: int,
) -> None:
    if not results:
        print("    --")
        return
    for result in results:
        negative_sources = compact_sources(negative_rows, result.negative_mask)
        print(
            f"    {result.rule}: pos={result.positive_samples}/{positive_total} "
            f"rows={result.positive_rows} neg={result.negative_samples}/{negative_total} "
            f"rows={result.negative_rows}"
            + (f" neg_sources={negative_sources}" if negative_sources else "")
        )
        if show_examples <= 0:
            continue
        positives = selected_examples(positive_rows, result.positive_mask, show_examples)
        if positives:
            print("      positive examples:")
            for row in positives:
                print(f"        {format_example(row)}")
        negatives = selected_examples(negative_rows, result.negative_mask, show_examples)
        if negatives:
            print("      protected-hit examples:")
            for row in negatives:
                print(f"        {format_example(row)}")


def print_bucket_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    explicit_patterns: list[Pattern],
    show_examples: int,
    max_conditions: int,
    beam_width: int,
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

    positive_bits = sample_bit_map(positive_rows)
    negative_bits = sample_bit_map(negatives)
    if explicit_patterns:
        positive_mask = (1 << len(positive_rows)) - 1
        negative_mask = (1 << len(negatives)) - 1
        for pattern in explicit_patterns:
            positive_mask &= mask_for_pattern(positive_rows, pattern)
            negative_mask &= mask_for_pattern(negatives, pattern)
        result = result_from_masks(
            " AND ".join(pattern.label for pattern in explicit_patterns),
            positive_mask,
            negative_mask,
            positive_rows,
            negatives,
            positive_bits,
            negative_bits,
            None,
        )
        print("  explicit rule:")
        print_results([result] if result is not None else [], positive_samples, negative_samples, positive_rows, negatives, show_examples)

    patterns = build_patterns(positive_rows)
    matches = [
        PatternMatch(
            pattern.label,
            mask_for_pattern(positive_rows, pattern),
            mask_for_pattern(negatives, pattern),
        )
        for pattern in patterns
    ]

    results: list[RuleResult] = []
    for match in matches:
        result = result_from_masks(
            match.label,
            match.positive_mask,
            match.negative_mask,
            positive_rows,
            negatives,
            positive_bits,
            negative_bits,
            max_negative_samples,
        )
        if result is not None and result.positive_samples >= min_positive_samples:
            results.append(result)
    results.extend(
        extend_condition_search(
            matches,
            positive_rows,
            negatives,
            positive_bits,
            negative_bits,
            min_positive_samples,
            max_negative_samples,
            max(2, max_conditions),
            max(1, beam_width),
        )
    )

    deduped: dict[str, RuleResult] = {}
    for result in results:
        existing = deduped.get(result.rule)
        if existing is None or rank_result(result) < rank_result(existing):
            deduped[result.rule] = result
    ranked = sorted(deduped.values(), key=rank_result)
    low_false = ranked[:limit]
    high_coverage = sorted(
        deduped.values(),
        key=lambda result: (-result.positive_samples, result.negative_samples, -result.positive_rows, result.rule),
    )[:limit]

    print("  low-false candidate rules:")
    print_results(low_false, positive_samples, negative_samples, positive_rows, negatives, show_examples)
    print("  highest-coverage candidate rules:")
    print_results(high_coverage, positive_samples, negative_samples, positive_rows, negatives, show_examples)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/instrument_sample_attributes.tsv")
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="owner bucket formatted as owner_miss:guitar->piano; repeatable",
    )
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--min-positive-samples", type=int, default=2)
    parser.add_argument("--max-negative-samples", type=int, default=25)
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help="explicit ANDed condition to measure, such as debug_owner=piano or partial2<=0.2",
    )
    parser.add_argument("--show-examples", type=int, default=0)
    parser.add_argument("--max-conditions", type=int, default=2)
    parser.add_argument("--beam-width", type=int, default=160)
    args = parser.parse_args()

    rows = load_rows(pathlib.Path(args.path))
    buckets = [parse_bucket_spec(spec) for spec in (args.bucket or DEFAULT_BUCKETS)]
    explicit_patterns = [condition_pattern(spec) for spec in args.condition]
    for bucket in buckets:
        print_bucket_patterns(
            rows,
            bucket,
            max(1, args.limit),
            max(1, args.min_positive_samples),
            max(0, args.max_negative_samples),
            explicit_patterns,
            max(0, args.show_examples),
            max(1, args.max_conditions),
            max(1, args.beam_width),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
