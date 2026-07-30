#!/usr/bin/env python3
"""Find candidate attribute patterns in real-note detector TSV exports."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import contextlib
import csv
import dataclasses
import io
import pathlib
import re
import statistics
from collections.abc import Callable

from inspect_real_note_attribute_buckets import derive_row as derive_real_note_row


DEBUG_NUMERIC_FIELDS = [
    "debug_midi",
    "debug_conf",
    "onset_strength",
    "decay_rate",
    "pitch_stability",
    "simultaneous_onset",
    "bass_score",
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
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "debug_delta",
    "debug_abs_delta",
]

ROW_CONTEXT_NUMERIC_FIELDS = [
    "expected_midi",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_visual_level",
    "guitar_visual_level",
    "piano_visual_level",
    "vocal_visual_level",
    "other_visual_level",
    "amb_visual_level",
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
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
    "raw_best_debug_delta",
    "raw_best_debug_abs_delta",
    "expected_row_exact_level",
    "expected_row_pitch_level",
    "expected_row_pitch_delta",
    "strongest_row_exact_level",
    "strongest_row_pitch_level",
    "strongest_row_pitch_delta",
    "expected_exact_row_count",
    "expected_pitch_row_count",
    "expected_row_visual_exact_level",
    "expected_row_visual_pitch_level",
    "expected_row_visual_pitch_delta",
    "visual_strongest_row_exact_level",
    "visual_strongest_row_pitch_level",
    "visual_strongest_row_pitch_delta",
    "expected_visual_exact_row_count",
    "expected_visual_pitch_row_count",
    "debug_delta",
    "debug_abs_delta",
]

DEBUG_CATEGORY_FIELDS = [
    "debug_owner",
    "debug_score_state",
]

ROW_CONTEXT_CATEGORY_FIELDS = [
    "buffer_strongest_row",
    "buffer_visual_strongest_row",
    "raw_local_best_note",
]

DEFAULT_BUCKETS = [
    "ownership_miss:other/acoustic->guitar",
    "ownership_miss:piano/electronic->guitar",
    "ownership_miss:piano/electronic->bass",
    "ownership_miss:other/acoustic->piano",
    "ownership_miss:guitar/acoustic->piano",
    "ownership_miss:guitar/acoustic->bass",
]

ROW_FOR_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}


@dataclasses.dataclass(frozen=True)
class Constraint:
    field: str
    kind: str
    value: float | str


@dataclasses.dataclass(frozen=True)
class Pattern:
    label: str
    category: bool
    predicate: Callable[[dict[str, str]], bool]
    constraint: Constraint | None = None


@dataclasses.dataclass(frozen=True)
class PatternMatch:
    label: str
    positive_row_mask: int
    negative_row_mask: int
    foreign_row_mask: int
    category: bool
    constraint: Constraint | None = None


@dataclasses.dataclass(frozen=True)
class RuleResult:
    rule: str
    positive_row_mask: int
    positive_samples: int
    positive_rows: int
    negative_row_mask: int
    negative_samples: int
    negative_rows: int
    foreign_row_mask: int
    foreign_samples: int
    foreign_rows: int


@dataclasses.dataclass(frozen=True)
class SearchState:
    labels: tuple[str, ...]
    constraints: tuple[Constraint, ...]
    positive_row_mask: int
    negative_row_mask: int
    foreign_row_mask: int
    next_match_index: int


@dataclasses.dataclass(frozen=True)
class PatternSearchSettings:
    limit: int
    min_positive_samples: int
    max_negative_samples: int
    include_intervals: bool
    include_row_context: bool
    condition_specs: tuple[str, ...]
    show_examples: int
    show_near_misses: int
    max_conditions: int
    beam_width: int
    exclude_fields: tuple[str, ...]
    protected_scope: str


class SampleCountCache:
    def __init__(self, row_sample_bits: list[int], max_samples: int | None = None) -> None:
        self.row_sample_bits = row_sample_bits
        self.max_samples = max_samples
        self.cache: dict[int, tuple[int, bool]] = {}

    def count(self, row_mask: int) -> tuple[int, bool]:
        cached = self.cache.get(row_mask)
        if cached is None:
            cached = sample_count_for_rows(row_mask, self.row_sample_bits, self.max_samples)
            self.cache[row_mask] = cached
        return cached

    def bounded_count(self, row_mask: int) -> int:
        count, exceeded = self.count(row_mask)
        if exceeded and self.max_samples is not None:
            return self.max_samples + 1
        return count


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
            f"invalid bucket `{spec}`; expected format status:family/source->target"
        )
    return match.group(1), match.group(2), match.group(3), match.group(4)


def bucket_label(bucket: tuple[str, str, str, str]) -> str:
    status, family, source, first_row = bucket
    return f"{status}:{family}/{source}->{first_row}"


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return [derive_real_note_row(row) for row in csv.DictReader(handle, delimiter="\t")]


def source_key(row: dict[str, str]) -> str:
    return f"{row.get('family', 'unknown')}/{row.get('source', 'unknown')}"


def octave_displacement_label(row: dict[str, str]) -> str:
    delta = as_float(row, "debug_delta")
    if delta is None:
        return ""
    rounded = int(round(delta))
    if abs(rounded) < 12 or rounded % 12 != 0:
        return ""
    return f"{rounded:+d}"


def rows_for_bucket(rows: list[dict[str, str]], bucket: tuple[str, str, str, str]) -> list[dict[str, str]]:
    status, family, source, target = bucket
    if status == "octave_displacement":
        return [
            row
            for row in rows
            if row.get("status") == "hit"
            and row.get("family") == family
            and row.get("source") == source
            and octave_displacement_label(row) == target
            and row.get("debug_note")
        ]
    if status == "row_confusion":
        expected_row = ROW_FOR_FAMILY.get(family, family)
        return [
            row
            for row in rows
            if row.get("status") == "hit"
            and row.get("family") == family
            and row.get("source") == source
            and row.get("buffer_strongest_row") == target
            and row.get("buffer_strongest_row") != expected_row
            and row.get("debug_note")
        ]
    if status == "visual_row_confusion":
        expected_row = ROW_FOR_FAMILY.get(family, family)
        return [
            row
            for row in rows
            if row.get("status") == "hit"
            and row.get("family") == family
            and row.get("source") == source
            and row.get("buffer_visual_strongest_row") == target
            and row.get("buffer_visual_strongest_row") != expected_row
            and row.get("debug_note")
        ]
    return [
        row
        for row in rows
        if row.get("status") == status
        and row.get("family") == family
        and row.get("source") == source
        and row.get("first_row") == target
        and row.get("debug_note")
    ]


def hit_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("status") == "hit" and row.get("debug_note")]


def protected_row_matches_scope(
    row: dict[str, str], bucket: tuple[str, str, str, str], protected_scope: str
) -> bool:
    if protected_scope == "all":
        return True

    status, family, source, _target = bucket
    if row.get("family") != family or row.get("source") != source:
        return False
    if protected_scope == "same-source":
        return True

    expected_row = ROW_FOR_FAMILY.get(family, family)
    if status == "visual_row_confusion":
        return row.get("buffer_visual_strongest_row", "") == expected_row
    if status == "row_confusion":
        return row.get("buffer_strongest_row", "") == expected_row
    if status == "ownership_miss":
        return row.get("detected_expected_row", "") == "1" or row.get("first_row", "") == expected_row
    if status == "octave_displacement":
        return row.get("debug_abs_delta", "") in {"", "0"}
    return True


def protected_hit_rows(
    rows: list[dict[str, str]],
    positive_rows: list[dict[str, str]],
    bucket: tuple[str, str, str, str],
    protected_scope: str,
) -> list[dict[str, str]]:
    positive_ids = {id(row) for row in positive_rows}
    return [
        row
        for row in hit_rows(rows)
        if id(row) not in positive_ids and protected_row_matches_scope(row, bucket, protected_scope)
    ]


def foreign_miss_rows(
    rows: list[dict[str, str]], positive_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    positive_ids = {id(row) for row in positive_rows}
    return [
        row
        for row in rows
        if id(row) not in positive_ids and row.get("status") != "hit" and row.get("debug_note")
    ]


def top_buckets(
    rows: list[dict[str, str]], limit: int, bucket_status: str
) -> list[tuple[str, str, str, str]]:
    if limit <= 0:
        return []
    counts: collections.Counter[tuple[str, str, str, str]] = collections.Counter()
    for row in rows:
        if not row.get("debug_note"):
            continue
        if bucket_status == "octave_displacement":
            delta_label = octave_displacement_label(row)
            if row.get("status") != "hit" or not delta_label:
                continue
            counts[
                (
                    "octave_displacement",
                    row.get("family", ""),
                    row.get("source", ""),
                    delta_label,
                )
            ] += 1
        elif bucket_status == "row_confusion":
            family = row.get("family", "")
            expected_row = ROW_FOR_FAMILY.get(family, family)
            strongest_row = row.get("buffer_strongest_row", "")
            if row.get("status") != "hit" or strongest_row == expected_row or not strongest_row:
                continue
            counts[("row_confusion", family, row.get("source", ""), strongest_row)] += 1
        elif bucket_status == "visual_row_confusion":
            family = row.get("family", "")
            expected_row = ROW_FOR_FAMILY.get(family, family)
            strongest_row = row.get("buffer_visual_strongest_row", "")
            if row.get("status") != "hit" or strongest_row == expected_row or not strongest_row:
                continue
            counts[("visual_row_confusion", family, row.get("source", ""), strongest_row)] += 1
        else:
            if row.get("status") != bucket_status:
                continue
            counts[
                (
                    row.get("status", ""),
                    row.get("family", ""),
                    row.get("source", ""),
                    row.get("first_row", ""),
                )
            ] += 1
    return [bucket for bucket, _count in counts.most_common(limit)]


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
            Constraint(field, "upper", threshold),
        )
    return Pattern(
        f"{field}>={format_value(threshold)}",
        False,
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value >= threshold
        ),
        Constraint(field, "lower", threshold),
    )


def interval_pattern(field: str, low: float, high: float) -> Pattern:
    return Pattern(
        f"{format_value(low)}<={field}<={format_value(high)}",
        False,
        lambda row, field=field, low=low, high=high: (
            (value := as_float(row, field)) is not None and low <= value <= high
        ),
        Constraint(field, "interval", f"{low}:{high}"),
    )


def category_pattern(field: str, expected: str) -> Pattern:
    return Pattern(
        f"{field}={expected}",
        True,
        lambda row, field=field, expected=expected: row.get(field, "") == expected,
        Constraint(field, "category", expected),
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
            False,
            lambda row, field=field, threshold=threshold: (
                (row_value := as_float(row, field)) is not None and row_value < threshold
            ),
            Constraint(field, "upper", threshold),
        )
    return Pattern(
        f"{field}>{format_value(threshold)}",
        False,
        lambda row, field=field, threshold=threshold: (
            (row_value := as_float(row, field)) is not None and row_value > threshold
        ),
        Constraint(field, "lower", threshold),
    )


def build_patterns(
    positive_rows: list[dict[str, str]],
    include_intervals: bool,
    include_row_context: bool,
    exclude_fields: set[str],
) -> tuple[list[Pattern], list[Pattern]]:
    category_patterns: list[Pattern] = []
    category_fields = [
        field
        for field in DEBUG_CATEGORY_FIELDS + (
        ROW_CONTEXT_CATEGORY_FIELDS if include_row_context else []
        )
        if field not in exclude_fields
    ]
    numeric_fields = [
        field
        for field in DEBUG_NUMERIC_FIELDS + (
        ROW_CONTEXT_NUMERIC_FIELDS if include_row_context else []
        )
        if field not in exclude_fields
    ]
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
    foreign_rows: list[dict[str, str]],
) -> PatternMatch:
    return PatternMatch(
        label=pattern.label,
        positive_row_mask=mask_for_pattern(positive_rows, pattern),
        negative_row_mask=mask_for_pattern(negative_rows, pattern),
        foreign_row_mask=mask_for_pattern(foreign_rows, pattern),
        category=pattern.category,
        constraint=pattern.constraint,
    )


def result_from_masks(
    label: str,
    positive_row_mask: int,
    negative_row_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    foreign_rows: list[dict[str, str]],
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    foreign_sample_bits: list[int],
    max_negative_samples: int | None,
    foreign_row_mask: int = 0,
) -> RuleResult | None:
    positive_samples, _positive_exceeded = sample_count_for_rows(
        positive_row_mask, positive_sample_bits
    )
    negative_samples, negative_exceeded = sample_count_for_rows(
        negative_row_mask, negative_sample_bits, max_negative_samples
    )
    if negative_exceeded:
        return None
    foreign_samples, _foreign_exceeded = sample_count_for_rows(
        foreign_row_mask, foreign_sample_bits
    )
    return RuleResult(
        rule=label,
        positive_row_mask=positive_row_mask,
        positive_samples=positive_samples,
        positive_rows=positive_row_mask.bit_count(),
        negative_row_mask=negative_row_mask,
        negative_samples=negative_samples,
        negative_rows=negative_row_mask.bit_count(),
        foreign_row_mask=foreign_row_mask,
        foreign_samples=foreign_samples,
        foreign_rows=foreign_row_mask.bit_count(),
    )


def count_samples_bounded(
    row_mask: int, row_sample_bits: list[int], max_samples: int | None
) -> int:
    count, exceeded = sample_count_for_rows(row_mask, row_sample_bits, max_samples)
    if exceeded and max_samples is not None:
        return max_samples + 1
    return count


def ranked_state_key(
    state: SearchState,
    positive_counter: SampleCountCache,
    negative_counter: SampleCountCache,
    foreign_counter: SampleCountCache,
) -> tuple[int, int, int, int, int, str]:
    negative_samples = negative_counter.bounded_count(state.negative_row_mask)
    foreign_samples = foreign_counter.bounded_count(state.foreign_row_mask)
    positive_samples = positive_counter.bounded_count(state.positive_row_mask)
    return (
        negative_samples,
        foreign_samples,
        -positive_samples,
        state.negative_row_mask.bit_count(),
        len(state.labels),
        " AND ".join(state.labels),
    )


def constraints_compatible(
    existing_constraints: tuple[Constraint, ...], new_constraint: Constraint | None
) -> bool:
    if new_constraint is None:
        return True
    for existing in existing_constraints:
        if existing.field != new_constraint.field:
            continue
        if existing.kind == "category" or new_constraint.kind == "category":
            return False
        if existing.kind == "interval" or new_constraint.kind == "interval":
            return False
        if existing.kind == new_constraint.kind:
            return False
        if {existing.kind, new_constraint.kind} == {"lower", "upper"}:
            lower = float(existing.value if existing.kind == "lower" else new_constraint.value)
            upper = float(existing.value if existing.kind == "upper" else new_constraint.value)
            return lower < upper
    return True


def extend_condition_search(
    matches: list[PatternMatch],
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    foreign_rows: list[dict[str, str]],
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    foreign_sample_bits: list[int],
    min_positive_samples: int,
    max_negative_samples: int,
    max_conditions: int,
    beam_width: int,
) -> list[RuleResult]:
    if max_conditions <= 2 or not matches:
        return []

    positive_counter = SampleCountCache(positive_sample_bits)
    negative_counter = SampleCountCache(negative_sample_bits, max_negative_samples)
    foreign_counter = SampleCountCache(foreign_sample_bits)
    ordered_matches = sorted(matches, key=lambda match: match.label)
    states: list[SearchState] = []
    for index, match in enumerate(ordered_matches):
        positive_samples = positive_counter.bounded_count(match.positive_row_mask)
        if positive_samples < min_positive_samples:
            continue
        states.append(
            SearchState(
                labels=(match.label,),
                constraints=(match.constraint,) if match.constraint is not None else (),
                positive_row_mask=match.positive_row_mask,
                negative_row_mask=match.negative_row_mask,
                foreign_row_mask=match.foreign_row_mask,
                next_match_index=index + 1,
            )
        )

    results: list[RuleResult] = []
    seen_results: set[tuple[int, int]] = set()
    max_conditions = max(3, max_conditions)
    beam_width = max(1, beam_width)

    for condition_count in range(2, max_conditions + 1):
        next_states: list[SearchState] = []
        seen_states: dict[tuple[int, int], SearchState] = {}
        for state in states:
            for match_index in range(state.next_match_index, len(ordered_matches)):
                match = ordered_matches[match_index]
                if not constraints_compatible(state.constraints, match.constraint):
                    continue
                positive_row_mask = state.positive_row_mask & match.positive_row_mask
                if positive_row_mask == 0:
                    continue
                positive_samples = positive_counter.bounded_count(positive_row_mask)
                if positive_samples < min_positive_samples:
                    continue
                negative_row_mask = state.negative_row_mask & match.negative_row_mask
                foreign_row_mask = state.foreign_row_mask & match.foreign_row_mask
                candidate = SearchState(
                    labels=state.labels + (match.label,),
                    constraints=(
                        state.constraints + (match.constraint,)
                        if match.constraint is not None else state.constraints
                    ),
                    positive_row_mask=positive_row_mask,
                    negative_row_mask=negative_row_mask,
                    foreign_row_mask=foreign_row_mask,
                    next_match_index=match_index + 1,
                )
                key = (positive_row_mask, negative_row_mask, foreign_row_mask)
                existing = seen_states.get(key)
                if existing is None or ranked_state_key(
                    candidate,
                    positive_counter,
                    negative_counter,
                    foreign_counter,
                ) < ranked_state_key(
                    existing,
                    positive_counter,
                    negative_counter,
                    foreign_counter,
                ):
                    seen_states[key] = candidate

        next_states = sorted(
            seen_states.values(),
            key=lambda state: ranked_state_key(
                state, positive_counter, negative_counter, foreign_counter
            ),
        )[:beam_width]

        if condition_count >= 3:
            for state in next_states:
                result_key = (
                    state.positive_row_mask,
                    state.negative_row_mask,
                    state.foreign_row_mask,
                )
                if result_key in seen_results:
                    continue
                seen_results.add(result_key)
                result = result_from_masks(
                    " AND ".join(state.labels),
                    state.positive_row_mask,
                    state.negative_row_mask,
                    positive_rows,
                    negative_rows,
                    foreign_rows,
                    positive_sample_bits,
                    negative_sample_bits,
                    foreign_sample_bits,
                    max_negative_samples,
                    state.foreign_row_mask,
                )
                if result is not None:
                    results.append(result)

        states = next_states
        if not states:
            break

    return results


def unique_rows_from_mask(
    rows: list[dict[str, str]], row_mask: int, limit: int
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen_samples: set[str] = set()
    while row_mask and len(selected) < limit:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        sample_id = row.get("sample_id", "")
        if sample_id not in seen_samples:
            seen_samples.add(sample_id)
            selected.append(row)
        row_mask ^= bit
    return selected


def short_float(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "-"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def format_example(row: dict[str, str]) -> str:
    scores = (
        short_float(row, "bass_score"),
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
        f"{row.get('sample_id', '')} expected={row.get('expected_note', '')}"
        f"/{row.get('expected_midi', '')} debug={row.get('debug_note', '')}"
        f"/{row.get('debug_midi', '')} owner={row.get('debug_owner', '')}"
        f" delta={row.get('debug_delta', '') or '-'} reason={row.get('miss_reason', '') or '-'}"
        f" first_row={row.get('first_row', '')} strongest={row.get('buffer_strongest_row', '')}"
        f" scores(b/k/g/v/o)={scores[0]}/{scores[1]}/{scores[2]}/{scores[3]}/{scores[4]}"
        f" spec={short_float(row, 'spectral_level')}"
        f" pitch={short_float(row, 'pitch_confidence')}"
        f" per={short_float(row, 'periodicity')}"
        f" fit={short_float(row, 'fit_error')}"
        f" cent={short_float(row, 'centroid')}"
        f" slope={short_float(row, 'slope')}"
        f" noise={short_float(row, 'noise')}"
        f" third_oct={short_float(row, 'third_octave_ratio')}"
        f" raw={short_float(row, 'raw_expected_ratio')}/{short_float(row, 'raw_tuned_ratio')}"
        f" raw_best={row.get('raw_local_best_note', '')}/{short_float(row, 'raw_local_best_peak')}"
        f" raw_rank={short_float(row, 'raw_expected_rank')}"
        f" p2..p5={partials[0]},{partials[1]},{partials[2]},{partials[3]}"
    )


def print_bucket_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    include_intervals: bool,
    include_row_context: bool,
    explicit_patterns: list[Pattern],
    show_examples: int,
    show_near_misses: int,
    max_conditions: int,
    beam_width: int,
    exclude_fields: set[str],
    protected_scope: str,
) -> None:
    positive_rows = rows_for_bucket(rows, bucket)
    negatives = protected_hit_rows(rows, positive_rows, bucket, protected_scope)
    foreign_rows = foreign_miss_rows(rows, positive_rows)
    positive_samples = sample_count(positive_rows)
    negative_samples = sample_count(negatives)
    foreign_samples = sample_count(foreign_rows)
    print()
    print(
        f"{bucket_label(bucket)} positives={positive_samples} samples/{len(positive_rows)} rows "
        f"protected_hits={negative_samples} samples/{len(negatives)} rows "
        f"foreign_misses={foreign_samples} samples/{len(foreign_rows)} rows"
    )
    if not positive_rows:
        return

    positive_sample_bits, _positive_sample_count = sample_bit_map(positive_rows)
    negative_sample_bits, _negative_sample_count = sample_bit_map(negatives)
    foreign_sample_bits, _foreign_sample_count = sample_bit_map(foreign_rows)
    if explicit_patterns:
        positive_row_mask = (1 << len(positive_rows)) - 1
        negative_row_mask = (1 << len(negatives)) - 1
        foreign_row_mask = (1 << len(foreign_rows)) - 1
        for pattern in explicit_patterns:
            positive_row_mask &= mask_for_pattern(positive_rows, pattern)
            negative_row_mask &= mask_for_pattern(negatives, pattern)
            foreign_row_mask &= mask_for_pattern(foreign_rows, pattern)
        result = result_from_masks(
            " AND ".join(pattern.label for pattern in explicit_patterns),
            positive_row_mask,
            negative_row_mask,
            positive_rows,
            negatives,
            foreign_rows,
            positive_sample_bits,
            negative_sample_bits,
            foreign_sample_bits,
            None,
            foreign_row_mask,
        )
        print("  explicit rule:")
        print_results(
            [result] if result is not None else [],
            positive_samples,
            negative_samples,
            foreign_samples,
            positive_rows,
            negatives,
            foreign_rows,
            show_examples,
        )

    category_patterns, numeric_patterns = build_patterns(
        positive_rows, include_intervals, include_row_context, exclude_fields
    )
    category_matches = [
        indexed_match(pattern, positive_rows, negatives, foreign_rows) for pattern in category_patterns
    ]
    numeric_matches = [
        indexed_match(pattern, positive_rows, negatives, foreign_rows) for pattern in numeric_patterns
    ]

    def add_result(
        label: str, positive_row_mask: int, negative_row_mask: int, foreign_row_mask: int
    ) -> None:
        result = result_from_masks(
            label,
            positive_row_mask,
            negative_row_mask,
            positive_rows,
            negatives,
            foreign_rows,
            positive_sample_bits,
            negative_sample_bits,
            foreign_sample_bits,
            max_negative_samples,
            foreign_row_mask,
        )
        if result is None:
            return
        if result.positive_samples < min_positive_samples:
            return
        results.append(result)

    results: list[RuleResult] = []
    for match in [*category_matches, *numeric_matches]:
        add_result(
            match.label,
            match.positive_row_mask,
            match.negative_row_mask,
            match.foreign_row_mask,
        )
    for category in category_matches:
        for numeric in numeric_matches:
            add_result(
                f"{category.label} AND {numeric.label}",
                category.positive_row_mask & numeric.positive_row_mask,
                category.negative_row_mask & numeric.negative_row_mask,
                category.foreign_row_mask & numeric.foreign_row_mask,
            )
    results.extend(
        extend_condition_search(
            [*category_matches, *numeric_matches],
            positive_rows,
            negatives,
            foreign_rows,
            positive_sample_bits,
            negative_sample_bits,
            foreign_sample_bits,
            min_positive_samples,
            max_negative_samples,
            max_conditions,
            beam_width,
        )
    )

    low_false = sorted(
        results,
        key=lambda result: (
            result.negative_samples,
            result.foreign_samples,
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
            result.foreign_samples,
            -result.positive_rows,
            result.rule,
        ),
    )[:limit]

    print("  low-false candidate rules:")
    print_results(
        low_false,
        positive_samples,
        negative_samples,
        foreign_samples,
        positive_rows,
        negatives,
        foreign_rows,
        show_examples,
    )
    print("  highest-coverage candidate rules:")
    print_results(
        coverage,
        positive_samples,
        negative_samples,
        foreign_samples,
        positive_rows,
        negatives,
        foreign_rows,
        show_examples,
    )
    if show_near_misses > 0:
        near_misses: list[RuleResult] = []
        for match in [*category_matches, *numeric_matches]:
            result = result_from_masks(
                match.label,
                match.positive_row_mask,
                match.negative_row_mask,
                positive_rows,
                negatives,
                foreign_rows,
                positive_sample_bits,
                negative_sample_bits,
                foreign_sample_bits,
                None,
                match.foreign_row_mask,
            )
            if result is None or result.positive_samples < min_positive_samples:
                continue
            if result.negative_samples <= max_negative_samples:
                continue
            near_misses.append(result)
        near_misses = sorted(
            near_misses,
            key=lambda result: (
                result.negative_samples,
                result.foreign_samples,
                -result.positive_samples,
                result.negative_rows,
                result.rule,
            ),
        )[:show_near_misses]
        if near_misses:
            print("  nearest over-budget single-condition candidate rules:")
            print_results(
                near_misses,
                positive_samples,
                negative_samples,
                foreign_samples,
                positive_rows,
                negatives,
                foreign_rows,
                show_examples,
            )


def print_results(
    results: list[RuleResult],
    positive_total: int,
    negative_total: int,
    foreign_total: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    foreign_rows: list[dict[str, str]],
    show_examples: int,
) -> None:
    if not results:
        print("    --")
        return
    for result in results:
        negative_sources = summarize_negative_sources_from_mask(
            negative_rows, result.negative_row_mask
        )
        foreign_sources = summarize_negative_sources_from_mask(
            foreign_rows, result.foreign_row_mask
        )
        print(
            f"    {result.rule}: pos={result.positive_samples}/{positive_total} "
            f"rows={result.positive_rows} neg={result.negative_samples}/{negative_total} "
            f"rows={result.negative_rows}"
            + (
                f" foreign_miss={result.foreign_samples}/{foreign_total} "
                f"rows={result.foreign_rows}"
                if foreign_total > 0 else ""
            )
            + (f" neg_sources={negative_sources}" if negative_sources else "")
            + (f" foreign_sources={foreign_sources}" if foreign_sources else "")
        )
        if show_examples <= 0:
            continue
        positive_examples = unique_rows_from_mask(
            positive_rows, result.positive_row_mask, show_examples
        )
        if positive_examples:
            print("      positive examples:")
            for row in positive_examples:
                print(f"        {format_example(row)}")
        negative_examples = unique_rows_from_mask(
            negative_rows, result.negative_row_mask, show_examples
        )
        if negative_examples:
            print("      protected-hit examples:")
            for row in negative_examples:
                print(f"        {format_example(row)}")
        foreign_examples = unique_rows_from_mask(
            foreign_rows, result.foreign_row_mask, show_examples
        )
        if foreign_examples:
            print("      foreign-miss examples:")
            for row in foreign_examples:
                print(f"        {format_example(row)}")


def bucket_patterns_text(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str, str],
    settings: PatternSearchSettings,
) -> str:
    output = io.StringIO()
    explicit_patterns = [
        condition_pattern(spec) for spec in settings.condition_specs
    ]
    with contextlib.redirect_stdout(output):
        print_bucket_patterns(
            rows,
            bucket,
            settings.limit,
            settings.min_positive_samples,
            settings.max_negative_samples,
            settings.include_intervals,
            settings.include_row_context,
            explicit_patterns,
            settings.show_examples,
            settings.show_near_misses,
            settings.max_conditions,
            settings.beam_width,
            set(settings.exclude_fields),
            settings.protected_scope,
        )
    return output.getvalue()


def bucket_patterns_text_job(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str, str],
    settings: PatternSearchSettings,
) -> str:
    return bucket_patterns_text(rows, bucket, settings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="bucket formatted as status:family/source->first_row; repeatable",
    )
    parser.add_argument(
        "--top-buckets",
        type=int,
        default=6,
        help="when --bucket is omitted, mine this many current top buckets; 0 uses fixed defaults",
    )
    parser.add_argument(
        "--bucket-status",
        choices=("ownership_miss", "row_confusion", "visual_row_confusion", "octave_displacement"),
        default="ownership_miss",
        help=(
            "status used by --top-buckets; row_confusion means hit rows whose strongest "
            "raw row is wrong, visual_row_confusion means hit rows whose strongest UI row "
            "is wrong, octave_displacement means hit rows shifted by octave"
        ),
    )
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--min-positive-samples", type=int, default=2)
    parser.add_argument("--max-negative-samples", type=int, default=25)
    parser.add_argument(
        "--protected-scope",
        choices=("all", "same-source", "same-source-correct-row"),
        default="all",
        help=(
            "which hit rows are treated as protected negatives; default all preserves "
            "historical behavior, same-source compares against the same family/source, "
            "and same-source-correct-row keeps only same family/source rows whose "
            "display owner matches the expected family"
        ),
    )
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
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help="explicit ANDed condition to measure, such as debug_owner=guitar or pitch_confidence>=0.8",
    )
    parser.add_argument(
        "--exclude-field",
        action="append",
        default=[],
        help="field to exclude from automatic pattern search; repeatable",
    )
    parser.add_argument(
        "--show-examples",
        "--row-examples",
        dest="show_examples",
        type=int,
        default=0,
        help="print up to this many positive and protected-hit sample examples for each rule",
    )
    parser.add_argument(
        "--show-near-misses",
        type=int,
        default=0,
        help="show this many closest over-budget single-condition candidates",
    )
    parser.add_argument(
        "--max-conditions",
        type=int,
        default=2,
        help="maximum number of ANDed auto-search conditions; values above 2 use bounded beam search",
    )
    parser.add_argument(
        "--beam-width",
        type=int,
        default=160,
        help="number of partial multi-condition rules retained per search depth",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="number of independent buckets to mine in parallel",
    )
    args = parser.parse_args()

    rows = load_rows(pathlib.Path(args.path))
    buckets = [parse_bucket_spec(spec) for spec in args.bucket]
    if not buckets:
        buckets = top_buckets(rows, args.top_buckets, args.bucket_status) or [
            parse_bucket_spec(spec) for spec in DEFAULT_BUCKETS
        ]
    settings = PatternSearchSettings(
        limit=max(1, args.limit),
        min_positive_samples=max(1, args.min_positive_samples),
        max_negative_samples=max(0, args.max_negative_samples),
        include_intervals=args.include_intervals,
        include_row_context=args.include_row_context,
        condition_specs=tuple(args.condition),
        show_examples=max(0, args.show_examples),
        show_near_misses=max(0, args.show_near_misses),
        max_conditions=max(1, args.max_conditions),
        beam_width=max(1, args.beam_width),
        exclude_fields=tuple(sorted(set(args.exclude_field))),
        protected_scope=args.protected_scope,
    )
    jobs = min(max(1, args.jobs), len(buckets))
    if jobs <= 1:
        for bucket in buckets:
            print(bucket_patterns_text(rows, bucket, settings), end="")
        return 0

    outputs = [""] * len(buckets)
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(bucket_patterns_text_job, rows, bucket, settings): index
            for index, bucket in enumerate(buckets)
        }
        for future in concurrent.futures.as_completed(futures):
            outputs[futures[future]] = future.result()
    for output in outputs:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
