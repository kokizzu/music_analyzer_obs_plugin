#!/usr/bin/env python3
"""Find candidate attribute patterns in generated instrument owner debug rows."""

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

from inspect_instrument_sample_owner_buckets import derive_row as derive_instrument_row


NUMERIC_FIELDS = [
    "midi",
    "window_ms",
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
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
    "debug_midi",
    "debug_conf",
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
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "debug_count",
    "nearest_debug_delta",
    "nearest_debug_abs_delta",
    "nearest_debug_conf",
]

FULL_MIX_DEBUG_NUMERIC_FIELDS = [
    "debug_midi",
    "debug_conf",
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
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]

DISPLAY_NUMERIC_FIELDS = [
    "detected_expected_row",
    "detected_anywhere",
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
]

CATEGORY_FIELDS = [
    "program_name",
    "note",
    "debug_note",
    "debug_owner",
    "nearest_debug_note",
    "nearest_debug_owner",
    "raw_local_best_note",
]

FULL_MIX_DEBUG_CATEGORY_FIELDS = [
    "debug_note",
    "debug_owner",
    "nearest_debug_note",
    "nearest_debug_owner",
]

DISPLAY_CATEGORY_FIELDS = [
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

DEFAULT_STATUS_BUCKETS = [
    "miss:strings",
    "miss:synth",
]


@dataclasses.dataclass(frozen=True)
class Constraint:
    field: str
    kind: str
    value: float | str


@dataclasses.dataclass(frozen=True)
class Pattern:
    label: str
    predicate: Callable[[dict[str, str]], bool]
    constraint: Constraint | None = None


@dataclasses.dataclass(frozen=True)
class PatternMatch:
    label: str
    positive_mask: int
    negative_mask: int
    constraint: Constraint | None = None


@dataclasses.dataclass(frozen=True)
class SearchState:
    labels: tuple[str, ...]
    constraints: tuple[Constraint, ...]
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


@dataclasses.dataclass(frozen=True)
class PatternSearchSettings:
    limit: int
    min_positive_samples: int
    max_negative_samples: int
    condition_specs: tuple[str, ...]
    positive_condition_specs: tuple[str, ...]
    negative_mode: str
    status_negative_mode: str
    show_examples: int
    max_conditions: int
    beam_width: int
    include_display_fields: bool
    field_preset: str
    excluded_fields: tuple[str, ...]
    profile_fields: int


def load_rows(path: pathlib.Path, *, include_all_note_rows: bool = False) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    derived: list[dict[str, str]] = []
    for row in rows:
        if row.get("kind") != "note":
            continue
        row = derive_instrument_row(row)
        row["_owner_target"] = owner_target(row)
        row["_owner"], row["_owner_source"] = owner_and_source(row)
        row["_owner_status"] = owner_status(row)
        row["_status_bucket"] = status_bucket_label((row.get("status", ""), note_row_family(row)))
        if include_all_note_rows:
            derived.append(row)
        elif row["_owner_status"] in {"owner_hit", "owner_miss"}:
            derived.append(row)
    return derived


def note_row_family(row: dict[str, str]) -> str:
    return row.get("family", "") or row.get("expected_family", "") or "unknown"


def owner_target(row: dict[str, str]) -> str:
    family = note_row_family(row)
    if family == "piano":
        return "piano"
    if family == "guitar":
        return "guitar"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth"}:
        return "other"
    if family == "bass":
        return "bass"
    return family or "unknown"


DISPLAY_LEVEL_FIELDS = {
    "bass": "bass_level",
    "piano": "piano_level",
    "guitar": "guitar_level",
    "vocals": "vocal_level",
    "other": "other_level",
}


def target_display_hit(row: dict[str, str], target: str) -> bool:
    if row.get("status") != "hit" or row.get("detected_expected_row") != "1":
        return False
    field = DISPLAY_LEVEL_FIELDS.get(target)
    value = as_float(row, field) if field else None
    return value is not None and value > 0.0


def owner_and_source(row: dict[str, str]) -> tuple[str, str]:
    target = owner_target(row)
    if target_display_hit(row, target):
        return target, "display"
    return row.get("debug_owner", "") or "none", "debug"


def owner_status(row: dict[str, str]) -> str:
    target = owner_target(row)
    owner, _source = owner_and_source(row)
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
        raise SystemExit(
            f"invalid bucket `{spec}`; expected format owner_miss:guitar->piano "
            "or debug_owner_miss:guitar->piano"
        )
    status = match.group(1)
    if status == "debug_owner_miss":
        status = "owner_miss"
    if status == "debug_owner_hit":
        status = "owner_hit"
    return status, match.group(2), match.group(3)


def parse_status_bucket_spec(spec: str) -> tuple[str, str]:
    match = re.fullmatch(r"([^:]+):(.+)", spec)
    if not match:
        raise SystemExit(f"invalid status bucket `{spec}`; expected format miss:strings")
    return match.group(1), match.group(2)


def bucket_label(bucket: tuple[str, str, str]) -> str:
    status, family, owner = bucket
    display_status = {
        "owner_miss": "owner_miss",
        "owner_hit": "owner_hit",
    }.get(status, status)
    return f"{display_status}:{family}->{owner}"


def status_bucket_label(bucket: tuple[str, str]) -> str:
    status, family = bucket
    return f"status:{status}:{family}"


def rows_for_bucket(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> list[dict[str, str]]:
    status, family, owner = bucket
    return [
        row
        for row in rows
        if row.get("_owner_status") == status
        and row.get("family") == family
        and row.get("_owner", "") == owner
    ]


def rows_for_status_bucket(rows: list[dict[str, str]], bucket: tuple[str, str]) -> list[dict[str, str]]:
    status, family = bucket
    return [
        row
        for row in rows
        if row.get("status") == status and note_row_family(row) == family
    ]


def top_owner_buckets(rows: list[dict[str, str]], limit: int, status: str) -> list[tuple[str, str, str]]:
    if limit <= 0:
        return []
    counts: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for row in rows:
        if row.get("_owner_status") != status:
            continue
        family = note_row_family(row)
        owner = row.get("_owner", "")
        if not family or not owner:
            continue
        counts[(status, family, owner)] += 1
    return [bucket for bucket, _count in counts.most_common(limit)]


def top_status_buckets(rows: list[dict[str, str]], limit: int, status: str) -> list[tuple[str, str]]:
    if limit <= 0:
        return []
    counts: collections.Counter[tuple[str, str]] = collections.Counter()
    for row in rows:
        if row.get("status") != status:
            continue
        family = note_row_family(row)
        if not family:
            continue
        counts[(status, family)] += 1
    return [bucket for bucket, _count in counts.most_common(limit)]


def hit_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("_owner_status") == "owner_hit"]


def status_hit_rows(rows: list[dict[str, str]], family: str | None = None) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("status") == "hit" and (family is None or note_row_family(row) == family)
    ]


def negative_rows(rows: list[dict[str, str]], bucket: tuple[str, str, str], mode: str) -> list[dict[str, str]]:
    if mode == "owner-hit":
        return hit_rows(rows)
    if mode == "not-family":
        _status, family, _owner = bucket
        return [row for row in rows if row.get("family") != family]
    raise SystemExit(f"unsupported negative mode `{mode}`")


def status_negative_rows(rows: list[dict[str, str]], bucket: tuple[str, str], mode: str) -> list[dict[str, str]]:
    status, family = bucket
    if mode == "same-family-hit":
        return status_hit_rows(rows, family)
    if mode == "all-hit":
        return status_hit_rows(rows)
    if mode == "not-bucket":
        return [
            row
            for row in rows
            if not (row.get("status") == status and note_row_family(row) == family)
        ]
    raise SystemExit(f"unsupported status negative mode `{mode}`")


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


def selected_field_sources(
    include_display_fields: bool,
    field_preset: str,
    excluded_fields: set[str],
) -> tuple[list[str], list[str]]:
    if field_preset == "full-mix-debug":
        category_source = FULL_MIX_DEBUG_CATEGORY_FIELDS
        numeric_source = FULL_MIX_DEBUG_NUMERIC_FIELDS
    else:
        category_source = CATEGORY_FIELDS
        numeric_source = NUMERIC_FIELDS
    category_fields = [
        field
        for field in category_source + (DISPLAY_CATEGORY_FIELDS if include_display_fields else [])
        if field not in excluded_fields
    ]
    numeric_fields = [
        field
        for field in numeric_source + (DISPLAY_NUMERIC_FIELDS if include_display_fields else [])
        if field not in excluded_fields
    ]
    return category_fields, numeric_fields


def numeric_summary(values: list[float]) -> str:
    if not values:
        return "-"
    sorted_values = sorted(values)
    median = statistics.median(sorted_values)
    low = quantile(sorted_values, 0.10)
    high = quantile(sorted_values, 0.90)
    return f"{format_value(median)} [{format_value(low)}..{format_value(high)}]"


def numeric_separation(positive_values: list[float], negative_values: list[float]) -> tuple[float, str]:
    if not positive_values or not negative_values:
        return 0.0, ">="

    sorted_negatives = sorted(negative_values)
    less = 0
    equal = 0
    for value in positive_values:
        lower_count = 0
        upper_count = len(sorted_negatives)
        while lower_count < upper_count:
            midpoint = (lower_count + upper_count) // 2
            if sorted_negatives[midpoint] < value:
                lower_count = midpoint + 1
            else:
                upper_count = midpoint
        left = lower_count
        lower_count = 0
        upper_count = len(sorted_negatives)
        while lower_count < upper_count:
            midpoint = (lower_count + upper_count) // 2
            if sorted_negatives[midpoint] <= value:
                lower_count = midpoint + 1
            else:
                upper_count = midpoint
        right = lower_count
        less += left
        equal += right - left

    pairs = len(positive_values) * len(negative_values)
    positive_higher = (less + equal * 0.5) / pairs
    positive_lower = 1.0 - positive_higher
    if positive_higher >= positive_lower:
        return positive_higher, ">="
    return positive_lower, "<="


def numeric_pattern(field: str, operator: str, threshold: float) -> Pattern:
    if operator == "<=":
        return Pattern(
            f"{field}<={format_value(threshold)}",
            lambda row, field=field, threshold=threshold: (
                (value := as_float(row, field)) is not None and value <= threshold
            ),
            Constraint(field, "upper", threshold),
        )
    return Pattern(
        f"{field}>={format_value(threshold)}",
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value >= threshold
        ),
        Constraint(field, "lower", threshold),
    )


def category_pattern(field: str, expected: str) -> Pattern:
    return Pattern(
        f"{field}={expected}",
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
            lambda row, field=field, threshold=threshold: (
                (value := as_float(row, field)) is not None and value < threshold
            ),
            Constraint(field, "upper", threshold),
        )
    return Pattern(
        f"{field}>{format_value(threshold)}",
        lambda row, field=field, threshold=threshold: (
            (value := as_float(row, field)) is not None and value > threshold
        ),
        Constraint(field, "lower", threshold),
    )


def build_patterns(
    positive_rows: list[dict[str, str]],
    include_display_fields: bool,
    field_preset: str,
    excluded_fields: set[str],
) -> list[Pattern]:
    patterns: list[Pattern] = []
    category_fields, numeric_fields = selected_field_sources(
        include_display_fields,
        field_preset,
        excluded_fields,
    )
    for field in category_fields:
        for value in sorted({row.get(field, "") for row in positive_rows if row.get(field, "")}):
            patterns.append(category_pattern(field, value))
    for field in numeric_fields:
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
                constraints=(match.constraint,) if match.constraint is not None else (),
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
                if not constraints_compatible(state.constraints, match.constraint):
                    continue
                positive_mask = state.positive_mask & match.positive_mask
                if positive_mask == 0:
                    continue
                if bounded_sample_count(positive_mask, positive_bits, None) < min_positive_samples:
                    continue
                negative_mask = state.negative_mask & match.negative_mask
                candidate = SearchState(
                    labels=state.labels + (match.label,),
                    constraints=(
                        state.constraints + (match.constraint,)
                        if match.constraint is not None else state.constraints
                    ),
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
        counts[f"{row.get('family', '')}->{row.get('_owner', '') or 'none'}"] += 1
        row_mask ^= bit
    return ",".join(f"{key}={value}" for key, value in counts.most_common(limit))


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
        f"{row.get('family', '')} {row.get('program_name', '')} {row.get('note', '')} "
        f"path={row.get('path', '')} status={row.get('status', '')} "
        f"target={row.get('_owner_target', '')} expected_level={short_float(row, 'expected_level')} "
        f"levels(b/p/g/v/o/a)={short_float(row, 'bass_level')}/{short_float(row, 'piano_level')}/"
        f"{short_float(row, 'guitar_level')}/{short_float(row, 'vocal_level')}/"
        f"{short_float(row, 'other_level')}/{short_float(row, 'amb_level')} "
        f"owner={row.get('_owner', '') or 'none'} source={row.get('_owner_source', '') or '-'} "
        f"debug_owner={row.get('debug_owner', '') or 'none'} debug={row.get('debug_note', '')}"
        f" nearest={row.get('nearest_debug_note', '') or '-'}"
        f"/{row.get('nearest_debug_delta', '') or '-'}"
        f"/{row.get('nearest_debug_owner', '') or '-'} reason={row.get('miss_reason', '') or '-'}"
        f" scores(b/k/g/v/o)={scores[0]}/{scores[1]}/{scores[2]}/{scores[3]}/{scores[4]}"
        f" spec={short_float(row, 'spectral_level')} pitch={short_float(row, 'pitch_confidence')}"
        f" per={short_float(row, 'periodicity')} fit={short_float(row, 'fit_error')}"
        f" debug_count={short_float(row, 'debug_count')} candidates={row.get('debug_candidates', '') or '-'}"
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


def print_attribute_profile(
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    include_display_fields: bool,
    field_preset: str,
    excluded_fields: set[str],
    limit: int,
) -> None:
    if limit <= 0:
        return

    category_fields, numeric_fields = selected_field_sources(
        include_display_fields,
        field_preset,
        excluded_fields,
    )
    numeric_profiles: list[tuple[float, str, str, str, str]] = []
    for field in numeric_fields:
        positive_values = [
            value for row in positive_rows if (value := as_float(row, field)) is not None
        ]
        negative_values = [
            value for row in negative_rows if (value := as_float(row, field)) is not None
        ]
        if not positive_values or not negative_values:
            continue
        separation, direction = numeric_separation(positive_values, negative_values)
        numeric_profiles.append(
            (
                abs(separation - 0.5),
                field,
                direction,
                numeric_summary(positive_values),
                numeric_summary(negative_values),
            )
        )
    numeric_profiles.sort(key=lambda item: (-item[0], item[1]))

    category_profiles: list[tuple[float, str, str, int, int, int, int]] = []
    for field in category_fields:
        positive_counts = collections.Counter(
            row.get(field, "") for row in positive_rows if row.get(field, "")
        )
        negative_counts = collections.Counter(
            row.get(field, "") for row in negative_rows if row.get(field, "")
        )
        if not positive_counts:
            continue
        positive_total = sum(positive_counts.values())
        negative_total = sum(negative_counts.values())
        for value, positive_count in positive_counts.items():
            negative_count = negative_counts.get(value, 0)
            positive_rate = positive_count / positive_total if positive_total else 0.0
            negative_rate = negative_count / negative_total if negative_total else 0.0
            category_profiles.append(
                (
                    positive_rate - negative_rate,
                    field,
                    value,
                    positive_count,
                    positive_total,
                    negative_count,
                    negative_total,
                )
            )
    category_profiles.sort(key=lambda item: (-item[0], item[1], item[2]))

    if numeric_profiles:
        print("  numeric attribute profile:")
        for separation, field, direction, positive_summary, negative_summary in numeric_profiles[:limit]:
            print(
                f"    {field} {direction} sep={separation + 0.5:.3f} "
                f"pos={positive_summary} protected={negative_summary}"
            )
    if category_profiles:
        print("  category attribute profile:")
        for (
            enrichment,
            field,
            value,
            positive_count,
            positive_total,
            negative_count,
            negative_total,
        ) in category_profiles[:limit]:
            print(
                f"    {field}={value} enrich={enrichment:.3f} "
                f"pos={positive_count}/{positive_total} protected={negative_count}/{negative_total}"
            )


def print_bucket_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    explicit_patterns: list[Pattern],
    positive_filters: list[Pattern],
    negative_mode: str,
    show_examples: int,
    max_conditions: int,
    beam_width: int,
    include_display_fields: bool,
    field_preset: str,
    excluded_fields: set[str],
    profile_fields: int,
) -> None:
    positive_rows = rows_for_bucket(rows, bucket)
    if positive_filters:
        positive_rows = [
            row
            for row in positive_rows
            if all(pattern.predicate(row) for pattern in positive_filters)
        ]
    negatives = negative_rows(rows, bucket, negative_mode)
    positive_samples = sample_count(positive_rows)
    negative_samples = sample_count(negatives)
    print()
    print(
        f"{bucket_label(bucket)} positives={positive_samples} samples/{len(positive_rows)} rows "
        f"negatives({negative_mode})={negative_samples} samples/{len(negatives)} rows"
    )
    if not positive_rows:
        return
    print_attribute_profile(
        positive_rows,
        negatives,
        include_display_fields,
        field_preset,
        excluded_fields,
        profile_fields,
    )

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

    patterns = build_patterns(positive_rows, include_display_fields, field_preset, excluded_fields)
    matches = [
        PatternMatch(
            pattern.label,
            mask_for_pattern(positive_rows, pattern),
            mask_for_pattern(negatives, pattern),
            pattern.constraint,
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


def print_status_patterns(
    rows: list[dict[str, str]],
    bucket: tuple[str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    explicit_patterns: list[Pattern],
    positive_filters: list[Pattern],
    negative_mode: str,
    show_examples: int,
    max_conditions: int,
    beam_width: int,
    include_display_fields: bool,
    field_preset: str,
    excluded_fields: set[str],
    profile_fields: int,
) -> None:
    positive_rows = rows_for_status_bucket(rows, bucket)
    if positive_filters:
        positive_rows = [
            row
            for row in positive_rows
            if all(pattern.predicate(row) for pattern in positive_filters)
        ]
    negatives = status_negative_rows(rows, bucket, negative_mode)
    positive_samples = sample_count(positive_rows)
    negative_samples = sample_count(negatives)
    print()
    print(
        f"{status_bucket_label(bucket)} positives={positive_samples} samples/{len(positive_rows)} rows "
        f"negatives({negative_mode})={negative_samples} samples/{len(negatives)} rows"
    )
    if not positive_rows:
        return
    print_attribute_profile(
        positive_rows,
        negatives,
        include_display_fields,
        field_preset,
        excluded_fields,
        profile_fields,
    )

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
        print_results(
            [result] if result is not None else [],
            positive_samples,
            negative_samples,
            positive_rows,
            negatives,
            show_examples,
        )

    patterns = build_patterns(positive_rows, include_display_fields, field_preset, excluded_fields)
    matches = [
        PatternMatch(
            pattern.label,
            mask_for_pattern(positive_rows, pattern),
            mask_for_pattern(negatives, pattern),
            pattern.constraint,
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


def bucket_patterns_text(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    settings: PatternSearchSettings,
) -> str:
    buffer = io.StringIO()
    explicit_patterns = [condition_pattern(spec) for spec in settings.condition_specs]
    positive_filters = [condition_pattern(spec) for spec in settings.positive_condition_specs]
    with contextlib.redirect_stdout(buffer):
        print_bucket_patterns(
            rows,
            bucket,
            settings.limit,
            settings.min_positive_samples,
            settings.max_negative_samples,
            explicit_patterns,
            positive_filters,
            settings.negative_mode,
            settings.show_examples,
            settings.max_conditions,
            settings.beam_width,
            settings.include_display_fields,
            settings.field_preset,
            set(settings.excluded_fields),
            settings.profile_fields,
        )
    return buffer.getvalue()


def status_patterns_text(
    rows: list[dict[str, str]],
    bucket: tuple[str, str],
    settings: PatternSearchSettings,
) -> str:
    buffer = io.StringIO()
    explicit_patterns = [condition_pattern(spec) for spec in settings.condition_specs]
    positive_filters = [condition_pattern(spec) for spec in settings.positive_condition_specs]
    with contextlib.redirect_stdout(buffer):
        print_status_patterns(
            rows,
            bucket,
            settings.limit,
            settings.min_positive_samples,
            settings.max_negative_samples,
            explicit_patterns,
            positive_filters,
            settings.status_negative_mode,
            settings.show_examples,
            settings.max_conditions,
            settings.beam_width,
            settings.include_display_fields,
            settings.field_preset,
            set(settings.excluded_fields),
            settings.profile_fields,
        )
    return buffer.getvalue()


def bucket_patterns_worker(
    task: tuple[int, list[dict[str, str]], tuple[str, str, str], PatternSearchSettings],
) -> tuple[int, str]:
    index, rows, bucket, settings = task
    return index, bucket_patterns_text(rows, bucket, settings)


def status_patterns_worker(
    task: tuple[int, list[dict[str, str]], tuple[str, str], PatternSearchSettings],
) -> tuple[int, str]:
    index, rows, bucket, settings = task
    return index, status_patterns_text(rows, bucket, settings)


def print_parallel_outputs(
    tasks: list[tuple],
    worker: Callable[[tuple], tuple[int, str]],
    jobs: int,
) -> None:
    if not tasks:
        return
    jobs = min(max(1, jobs), len(tasks))
    if jobs <= 1:
        for task in tasks:
            print(worker(task)[1], end="")
        return
    outputs: list[str] = [""] * len(tasks)
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        for index, text in executor.map(worker, tasks):
            outputs[index] = text
    for text in outputs:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/instrument_sample_attributes.tsv")
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help=(
            "debug-owner bucket formatted as debug_owner_miss:guitar->piano; "
            "legacy owner_miss:guitar->piano is also accepted; repeatable"
        ),
    )
    parser.add_argument(
        "--status-bucket",
        action="append",
        default=[],
        help="final note status bucket formatted as miss:strings or ownership_miss:synth; repeatable",
    )
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument(
        "--top-buckets",
        type=int,
        default=None,
        help=(
            "when --bucket is omitted, mine this many current top owner buckets; "
            "0 uses fixed defaults"
        ),
    )
    parser.add_argument(
        "--bucket-status",
        choices=["owner_miss", "owner_hit"],
        default="owner_miss",
        help="owner status used by --top-buckets",
    )
    parser.add_argument(
        "--status-top-buckets",
        type=int,
        default=None,
        help=(
            "when --status-bucket is omitted, mine this many current final-status buckets; "
            "0 uses fixed defaults"
        ),
    )
    parser.add_argument(
        "--status-bucket-status",
        default="miss",
        help="final note status used by --status-top-buckets",
    )
    parser.add_argument("--min-positive-samples", type=int, default=2)
    parser.add_argument("--max-negative-samples", type=int, default=25)
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help="explicit ANDed condition to measure, such as debug_owner=piano or partial2<=0.2",
    )
    parser.add_argument(
        "--positive-condition",
        action="append",
        default=[],
        help="ANDed condition used to prefilter positive bucket rows before searching",
    )
    parser.add_argument("--show-examples", type=int, default=0)
    parser.add_argument("--max-conditions", type=int, default=2)
    parser.add_argument("--beam-width", type=int, default=160)
    parser.add_argument(
        "--negative-mode",
        choices=["owner-hit", "not-family"],
        default="owner-hit",
        help="negative row set to protect while mining candidate rules",
    )
    parser.add_argument(
        "--status-negative-mode",
        choices=["same-family-hit", "all-hit", "not-bucket"],
        default="same-family-hit",
        help="negative row set to protect while mining final-status rules",
    )
    parser.add_argument(
        "--include-display-fields",
        action="store_true",
        help="include display/result fields such as expected_level and row labels in automatic rules",
    )
    parser.add_argument(
        "--field-preset",
        choices=["all", "full-mix-debug"],
        default="all",
        help="automatic pattern field set; full-mix-debug uses only candidate fields available in live display logic",
    )
    parser.add_argument(
        "--exclude-field",
        action="append",
        default=[],
        help="field to exclude from automatic pattern search; repeatable",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="mine independent owner/status buckets in parallel when multiple buckets are selected",
    )
    parser.add_argument(
        "--profile-fields",
        type=int,
        default=0,
        help="print this many ranked numeric and category attribute profiles for each bucket",
    )
    args = parser.parse_args()

    settings = PatternSearchSettings(
        limit=max(1, args.limit),
        min_positive_samples=max(1, args.min_positive_samples),
        max_negative_samples=max(0, args.max_negative_samples),
        condition_specs=tuple(args.condition),
        positive_condition_specs=tuple(args.positive_condition),
        negative_mode=args.negative_mode,
        status_negative_mode=args.status_negative_mode,
        show_examples=max(0, args.show_examples),
        max_conditions=max(1, args.max_conditions),
        beam_width=max(1, args.beam_width),
        include_display_fields=args.include_display_fields,
        field_preset=args.field_preset,
        excluded_fields=tuple(args.exclude_field),
        profile_fields=max(0, args.profile_fields),
    )
    jobs = max(1, args.jobs)
    if args.bucket or not (args.status_bucket or args.status_top_buckets is not None):
        owner_rows = load_rows(pathlib.Path(args.path))
        buckets = [parse_bucket_spec(spec) for spec in args.bucket]
        if not buckets:
            if args.top_buckets is not None:
                buckets = top_owner_buckets(owner_rows, args.top_buckets, args.bucket_status)
            if not buckets:
                buckets = [parse_bucket_spec(spec) for spec in DEFAULT_BUCKETS]
        print_parallel_outputs(
            [(index, owner_rows, bucket, settings) for index, bucket in enumerate(buckets)],
            bucket_patterns_worker,
            jobs,
        )
    if args.status_bucket or args.status_top_buckets is not None:
        status_rows = load_rows(pathlib.Path(args.path), include_all_note_rows=True)
        status_buckets = [parse_status_bucket_spec(spec) for spec in args.status_bucket]
        if not status_buckets:
            if args.status_top_buckets is not None:
                status_buckets = top_status_buckets(
                    status_rows,
                    args.status_top_buckets,
                    args.status_bucket_status,
            )
            if not status_buckets:
                status_buckets = [parse_status_bucket_spec(spec) for spec in DEFAULT_STATUS_BUCKETS]
        print_parallel_outputs(
            [(index, status_rows, bucket, settings) for index, bucket in enumerate(status_buckets)],
            status_patterns_worker,
            jobs,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
