#!/usr/bin/env python3
"""Find candidate attribute patterns in drum primary debug rows."""

from __future__ import annotations

import argparse
import bisect
import concurrent.futures
import contextlib
import csv
import dataclasses
import io
import pathlib
import re
import statistics
from collections import Counter
from collections.abc import Callable


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
METRIC_FIELDS = ("band", "seg", "shape_score", "trigger", "threshold", "shape", "level")
ROW_RE = re.compile(r"debug 100ms (?P<sample>\S+) expected (?P<expected>\w+)")
DETAIL_RE = re.compile(
    r"(?P<cat>kick|snare|hihat|crash|tom|ride|rim) "
    r"band=(?P<band>[0-9.]+) "
    r"seg=(?P<seg>[0-9.]+) "
    r"shape_score=(?P<shape_score>[0-9.]+) "
    r"trigger=(?P<trigger>[0-9.]+)/(?P<threshold>[0-9.]+) "
    r"shape=(?P<shape>[01]) "
    r"level=(?P<level>[0-9.]+)"
)
TRANSIENT_RE = re.compile(
    r"transient=(?P<transient>[0-9.]+) onset=(?P<onset>[0-9.]+) "
    r"energy=(?P<low>[0-9.]+)/(?P<mid>[0-9.]+)/(?P<high>[0-9.]+)"
    r"(?: body=(?P<kick_body>[0-9.]+)/(?P<snare_body>[0-9.]+)/(?P<tom_body>[0-9.]+)"
    r" crack=(?P<snare_crack>[0-9.]+) upper_tom=(?P<upper_tom_body>[0-9.]+)"
    r" body_shape=(?P<body_shape>-?[0-9]+))?"
)
MERGED_EXPECTED_RE = re.compile(r"\bmerged_expected=(?P<merged>[01])\b")


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
    all_mask: int
    constraint: Constraint | None = None


@dataclasses.dataclass(frozen=True)
class SearchState:
    labels: tuple[str, ...]
    constraints: tuple[Constraint, ...]
    positive_mask: int
    negative_mask: int
    all_mask: int
    next_match_index: int


@dataclasses.dataclass(frozen=True)
class RuleResult:
    rule: str
    positive_rows: int
    positive_samples: int
    negative_rows: int
    negative_samples: int
    foreign_rows: int
    foreign_samples: int
    new_active_rows: int
    new_active_samples: int
    primary_break_rows: int
    primary_break_samples: int
    positive_examples: list[dict[str, str]]
    negative_examples: list[dict[str, str]]
    new_active_examples: list[dict[str, str]]
    primary_break_examples: list[dict[str, str]]


@dataclasses.dataclass
class SampleCounter:
    row_bits: list[int]
    exact_counts: dict[int, int] = dataclasses.field(default_factory=dict)
    limited_counts: dict[tuple[int, int], tuple[int, bool]] = dataclasses.field(default_factory=dict)

    def count(self, row_mask: int, limit: int | None = None) -> tuple[int, bool]:
        if limit is None:
            cached = self.exact_counts.get(row_mask)
            if cached is not None:
                return cached, False
            count = self.sample_mask(row_mask).bit_count()
            self.exact_counts[row_mask] = count
            return count, False

        cached_exact = self.exact_counts.get(row_mask)
        if cached_exact is not None:
            return cached_exact, cached_exact > limit
        key = (row_mask, limit)
        cached_limited = self.limited_counts.get(key)
        if cached_limited is not None:
            return cached_limited

        sample_mask = 0
        work_mask = row_mask
        while work_mask:
            bit = work_mask & -work_mask
            index = bit.bit_length() - 1
            sample_mask |= self.row_bits[index]
            count = sample_mask.bit_count()
            if count > limit:
                result = (count, True)
                self.limited_counts[key] = result
                return result
            work_mask ^= bit
        count = sample_mask.bit_count()
        self.exact_counts[row_mask] = count
        result = (count, False)
        self.limited_counts[key] = result
        return result

    def sample_mask(self, row_mask: int) -> int:
        sample_mask = 0
        work_mask = row_mask
        while work_mask:
            bit = work_mask & -work_mask
            index = bit.bit_length() - 1
            sample_mask |= self.row_bits[index]
            work_mask ^= bit
        return sample_mask


@dataclasses.dataclass(frozen=True)
class SideEffectMaskSet:
    foreign: int
    new_active: int
    primary_break: int


@dataclasses.dataclass(frozen=True)
class RoutePatternSettings:
    limit: int
    min_positive_samples: int
    max_negative_samples: int
    max_conditions: int
    beam_width: int
    show_examples: int
    show_near_misses: int
    include_merged_rows: bool
    min_route_positive_samples: int
    min_route_positive_rows: int
    profile_fields: int


def primary_from_levels(row: dict[str, str]) -> str:
    best = "none"
    best_level = 0.0
    for category in CATEGORIES:
        level = as_float(row, f"{category}_level") or 0.0
        if level <= 0.30 or level <= best_level:
            continue
        best = category
        best_level = level
    if best == "none":
        return best
    tied = sum(
        1
        for category in CATEGORIES
        if (as_float(row, f"{category}_level") or 0.0) > 0.30
        and abs((as_float(row, f"{category}_level") or 0.0) - best_level) <= 0.005
    )
    return "ambiguous" if tied > 1 else best


def parse_debug_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        row_match = ROW_RE.search(line)
        transient_match = TRANSIENT_RE.search(line)
        if not row_match or not transient_match:
            continue
        row: dict[str, str] = {
            "sample": row_match.group("sample"),
            "expected": row_match.group("expected"),
            "merged_expected": "0",
        }
        merged_match = MERGED_EXPECTED_RE.search(line)
        if merged_match:
            row["merged_expected"] = merged_match.group("merged")
        for field in (
            "transient",
            "onset",
            "low",
            "mid",
            "high",
            "kick_body",
            "snare_body",
            "tom_body",
            "snare_crack",
            "upper_tom_body",
            "body_shape",
        ):
            row[field] = transient_match.group(field) or "0"
        for match in DETAIL_RE.finditer(line):
            category = match.group("cat")
            for field in METRIC_FIELDS:
                row[f"{category}_{field}"] = match.group(field)
        if not any(f"{category}_level" in row for category in CATEGORIES):
            continue
        row["primary"] = primary_from_levels(row)
        add_ratios(row)
        rows.append(row)
    return rows


def parse_tsv_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for raw in reader:
        if not raw.get("sample") or not raw.get("expected"):
            continue
        row: dict[str, str] = {}
        for field, value in raw.items():
            if field is None or value is None:
                continue
            if field in {"energy_low", "energy_mid", "energy_high", "got"}:
                continue
            row[field] = value
        for source, target in (
            ("energy_low", "low"),
            ("energy_mid", "mid"),
            ("energy_high", "high"),
        ):
            if raw.get(source):
                row[target] = raw[source]
        row["sample"] = raw["sample"]
        row["expected"] = raw["expected"]
        row["primary"] = raw.get("got") or primary_from_levels(row)
        row["merged_expected"] = raw.get("merged_expected") or "0"
        if not any(f"{category}_level" in row for category in CATEGORIES):
            continue
        add_ratios(row)
        rows.append(row)
    return rows


def parse_rows(path: pathlib.Path, source: str | None = None) -> list[dict[str, str]]:
    text = path.read_text(errors="replace")
    first_line = next((line for line in text.splitlines() if line.strip()), "")
    if "\t" in first_line:
        header = first_line.split("\t")
        if {"sample", "expected"}.issubset(set(header)):
            rows = parse_tsv_rows(text)
        else:
            rows = parse_debug_rows(text)
    else:
        rows = parse_debug_rows(text)
    source = source or path.stem
    for row in rows:
        row["source"] = source
    return rows


def add_ratios(row: dict[str, str]) -> None:
    for lhs, rhs in (
        ("tom", "snare"),
        ("tom", "kick"),
        ("snare", "kick"),
        ("hihat", "rim"),
        ("crash", "hihat"),
        ("ride", "hihat"),
    ):
        for field in ("band", "seg", "shape_score", "trigger", "level"):
            lhs_value = as_float(row, f"{lhs}_{field}")
            rhs_value = as_float(row, f"{rhs}_{field}")
            if lhs_value is None or rhs_value is None:
                continue
            if abs(rhs_value) < 1.0e-6:
                continue
            row[f"{lhs}_{rhs}_{field}_ratio"] = f"{lhs_value / rhs_value:.9f}"
    for label, lhs_field, rhs_field in (
        ("tom_snare_body_ratio", "tom_body", "snare_body"),
        ("tom_kick_body_ratio", "tom_body", "kick_body"),
        ("snare_kick_body_ratio", "snare_body", "kick_body"),
        ("upper_tom_snare_body_ratio", "upper_tom_body", "snare_body"),
        ("upper_tom_snare_crack_ratio", "upper_tom_body", "snare_crack"),
    ):
        lhs_value = as_float(row, lhs_field)
        rhs_value = as_float(row, rhs_field)
        if lhs_value is None or rhs_value is None:
            continue
        if abs(rhs_value) < 1.0e-6:
            continue
        row[label] = f"{lhs_value / rhs_value:.9f}"


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


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


def numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    fields = set()
    for row in rows:
        for field, value in row.items():
            if field in {"sample", "expected", "primary", "merged_expected"}:
                continue
            try:
                float(value)
            except ValueError:
                continue
            fields.add(field)
    return sorted(fields)


def build_patterns(positive_rows: list[dict[str, str]]) -> list[Pattern]:
    patterns: list[Pattern] = []
    for field in ("body_shape",):
        for value in sorted({row.get(field, "") for row in positive_rows if row.get(field, "")}):
            patterns.append(category_pattern(field, value))
    for field in numeric_fields(positive_rows):
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


def sample_key(row: dict[str, str]) -> str:
    return f"{row.get('source', '')}\0{row.get('sample', '')}"


def sample_bit_map(rows: list[dict[str, str]]) -> list[int]:
    bits: dict[str, int] = {}
    row_bits: list[int] = []
    for row in rows:
        sample = sample_key(row)
        if sample not in bits:
            bits[sample] = 1 << len(bits)
        row_bits.append(bits[sample])
    return row_bits


def mask_for_pattern(rows: list[dict[str, str]], pattern: Pattern) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern.predicate(row):
            mask |= 1 << index
    return mask


def sample_count_for_mask(row_mask: int, row_bits: list[int], limit: int | None = None) -> tuple[int, bool]:
    return SampleCounter(row_bits).count(row_mask, limit)


def bounded_sample_count(row_mask: int, counter: SampleCounter, limit: int | None) -> int:
    count, exceeded = counter.count(row_mask, limit)
    if exceeded and limit is not None:
        return limit + 1
    return count


def selected_samples_from_mask(rows: list[dict[str, str]], row_mask: int, limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    while row_mask and len(selected) < limit:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        sample = sample_key(row)
        if sample not in seen:
            seen.add(sample)
            selected.append(row)
        row_mask ^= bit
    return selected


def side_effect_base_masks(rows: list[dict[str, str]], target_category: str) -> SideEffectMaskSet:
    foreign_mask = 0
    new_active_mask = 0
    primary_break_mask = 0
    target_level_field = f"{target_category}_level"
    for index, row in enumerate(rows):
        bit = 1 << index
        expected = row.get("expected", "")
        if expected == target_category:
            continue
        foreign_mask |= bit
        target_level = as_float(row, target_level_field) or 0.0
        if target_level <= 0.30:
            new_active_mask |= bit
        if expected in CATEGORIES:
            primary = row.get("primary", "")
            expected_level = as_float(row, f"{expected}_level") or 0.0
            primary_level = as_float(row, f"{primary}_level") if primary in CATEGORIES else None
            current_winner_level = expected_level if primary_level is None else max(expected_level, primary_level)
            repaired_target_level = max(target_level, 0.90, current_winner_level + 0.02)
            if repaired_target_level > expected_level + 0.005:
                primary_break_mask |= bit
    return SideEffectMaskSet(
        foreign=foreign_mask,
        new_active=new_active_mask,
        primary_break=primary_break_mask,
    )


def side_effect_masks(row_mask: int, base_masks: SideEffectMaskSet) -> tuple[int, int, int]:
    return (
        row_mask & base_masks.foreign,
        row_mask & base_masks.new_active,
        row_mask & base_masks.primary_break,
    )


def result_from_masks(
    rule: str,
    positive_mask: int,
    negative_mask: int,
    all_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    all_rows: list[dict[str, str]],
    positive_counter: SampleCounter,
    negative_counter: SampleCounter,
    all_counter: SampleCounter,
    side_effect_base: SideEffectMaskSet,
    target_category: str,
    max_negative_samples: int | None,
    show_examples: int,
) -> RuleResult | None:
    positive_samples, _positive_exceeded = positive_counter.count(positive_mask)
    if positive_samples <= 0:
        return None
    negative_samples, negative_exceeded = negative_counter.count(negative_mask, max_negative_samples)
    if negative_exceeded:
        return None
    foreign_mask, new_active_mask, primary_break_mask = side_effect_masks(all_mask, side_effect_base)
    foreign_samples, _foreign_exceeded = all_counter.count(foreign_mask)
    new_active_samples, _new_active_exceeded = all_counter.count(new_active_mask)
    primary_break_samples, _primary_break_exceeded = all_counter.count(primary_break_mask)
    return RuleResult(
        rule=rule,
        positive_rows=positive_mask.bit_count(),
        positive_samples=positive_samples,
        negative_rows=negative_mask.bit_count(),
        negative_samples=negative_samples,
        foreign_rows=foreign_mask.bit_count(),
        foreign_samples=foreign_samples,
        new_active_rows=new_active_mask.bit_count(),
        new_active_samples=new_active_samples,
        primary_break_rows=primary_break_mask.bit_count(),
        primary_break_samples=primary_break_samples,
        positive_examples=selected_samples_from_mask(positive_rows, positive_mask, show_examples),
        negative_examples=selected_samples_from_mask(negative_rows, negative_mask, show_examples),
        new_active_examples=selected_samples_from_mask(all_rows, new_active_mask, show_examples),
        primary_break_examples=selected_samples_from_mask(all_rows, primary_break_mask, show_examples),
    )


def ranked_state_key(
    state: SearchState,
    positive_counter: SampleCounter,
    negative_counter: SampleCounter,
    max_negative_samples: int | None,
) -> tuple[int, int, int, int, str]:
    negative_samples = bounded_sample_count(state.negative_mask, negative_counter, max_negative_samples)
    positive_samples = bounded_sample_count(state.positive_mask, positive_counter, None)
    return (
        negative_samples,
        -positive_samples,
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
    all_rows: list[dict[str, str]],
    positive_counter: SampleCounter,
    negative_counter: SampleCounter,
    all_counter: SampleCounter,
    side_effect_base: SideEffectMaskSet,
    target_category: str,
    min_positive_samples: int,
    max_negative_samples: int | None,
    max_conditions: int,
    beam_width: int,
    show_examples: int,
) -> list[RuleResult]:
    if max_conditions < 2 or not matches:
        return []
    ordered = sorted(matches, key=lambda match: match.label)
    states: list[SearchState] = []
    for index, match in enumerate(ordered):
        if bounded_sample_count(match.positive_mask, positive_counter, None) < min_positive_samples:
            continue
        states.append(
            SearchState(
                labels=(match.label,),
                constraints=(match.constraint,) if match.constraint is not None else (),
                positive_mask=match.positive_mask,
                negative_mask=match.negative_mask,
                all_mask=match.all_mask,
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
                if bounded_sample_count(positive_mask, positive_counter, None) < min_positive_samples:
                    continue
                negative_mask = state.negative_mask & match.negative_mask
                all_mask = state.all_mask & match.all_mask
                candidate = SearchState(
                    labels=state.labels + (match.label,),
                    constraints=(
                        state.constraints + (match.constraint,)
                        if match.constraint is not None else state.constraints
                    ),
                    positive_mask=positive_mask,
                    negative_mask=negative_mask,
                    all_mask=all_mask,
                    next_match_index=match_index + 1,
                )
                key = (positive_mask, negative_mask, all_mask)
                existing = next_states.get(key)
                if existing is None or ranked_state_key(
                    candidate, positive_counter, negative_counter, max_negative_samples
                ) < ranked_state_key(existing, positive_counter, negative_counter, max_negative_samples):
                    next_states[key] = candidate
        states = sorted(
            next_states.values(),
            key=lambda state: ranked_state_key(
                state, positive_counter, negative_counter, max_negative_samples
            ),
        )[: max(1, beam_width)]
        for state in states:
            result_key = (state.positive_mask, state.negative_mask, state.all_mask)
            if result_key in seen_results:
                continue
            seen_results.add(result_key)
            result = result_from_masks(
                " AND ".join(state.labels),
                state.positive_mask,
                state.negative_mask,
                state.all_mask,
                positive_rows,
                negative_rows,
                all_rows,
                positive_counter,
                negative_counter,
                all_counter,
                side_effect_base,
                target_category,
                max_negative_samples,
                show_examples,
            )
            if result is not None:
                results.append(result)
        if not states:
            break
    return results


def rank_result(result: RuleResult) -> tuple[int, int, int, int, int, int, int, str]:
    return (
        result.negative_samples,
        result.primary_break_samples,
        result.new_active_samples,
        result.foreign_samples,
        -result.positive_samples,
        result.negative_rows,
        result.rule.count(" AND "),
        result.rule,
    )


def parse_route(route: str) -> tuple[str, str]:
    match = re.fullmatch(r"([a-z]+)->([a-z]+|ambiguous|none)", route)
    if not match:
        raise SystemExit(f"invalid route `{route}`; expected e.g. tom->snare")
    return match.group(1), match.group(2)


def route_positive_rows(
    rows: list[dict[str, str]],
    route: tuple[str, str],
    include_merged_positives: bool,
) -> list[dict[str, str]]:
    expected, got = route
    return [
        row for row in rows
        if row.get("expected") == expected
        and row.get("primary") == got
        and (include_merged_positives or row.get("merged_expected") != "1")
    ]


def route_sample_count(rows: list[dict[str, str]]) -> int:
    return len({sample_key(row) for row in rows})


def top_routes(
    rows: list[dict[str, str]],
    limit: int,
    min_positive_samples: int,
    min_positive_rows: int,
    include_merged_positives: bool,
) -> list[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    route_sample_keys: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        expected = row.get("expected", "")
        got = row.get("primary", "")
        if not expected or not got or expected == got:
            continue
        if not include_merged_positives and row.get("merged_expected") == "1":
            continue
        counts[(expected, got)] += 1
        route_sample_keys.setdefault((expected, got), set()).add(sample_key(row))
    routes = []
    for route, row_count in counts.most_common():
        sample_count = len(route_sample_keys.get(route, set()))
        if sample_count < min_positive_samples or row_count < min_positive_rows:
            continue
        routes.append(route)
        if len(routes) >= max(1, limit):
            break
    return routes


def format_example(row: dict[str, str]) -> str:
    expected = row.get("expected", "")
    got = row.get("primary", "")
    source = row.get("source", "")
    sample = row.get("sample", "")
    sample_text = f"{source}:{sample}" if source else sample
    parts = [
        f"{sample_text} {expected}->{got}",
        f"energy={value_text(row, 'low')}/{value_text(row, 'mid')}/{value_text(row, 'high')}",
        f"body={value_text(row, 'kick_body')}/{value_text(row, 'snare_body')}/{value_text(row, 'tom_body')}",
        f"crack={value_text(row, 'snare_crack')}",
        f"upper_tom={value_text(row, 'upper_tom_body')}",
        f"body_shape={row.get('body_shape', '')}",
    ]
    for category in (expected, got, "tom", "snare", "kick"):
        if category not in CATEGORIES:
            continue
        level_field = f"{category}_level"
        trigger_field = f"{category}_trigger"
        if level_field not in row:
            continue
        text = f"{category}:level={value_text(row, level_field)} trigger={value_text(row, trigger_field)}"
        if text not in parts:
            parts.append(text)
    return " ".join(parts)


def value_text(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "-"
    return f"{value:.3f}".rstrip("0").rstrip(".")


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
        left = bisect.bisect_left(sorted_negatives, value)
        right = bisect.bisect_right(sorted_negatives, value)
        less += left
        equal += right - left

    pairs = len(positive_values) * len(negative_values)
    positive_higher = (less + equal * 0.5) / pairs
    positive_lower = 1.0 - positive_higher
    if positive_higher >= positive_lower:
        return positive_higher, ">="
    return positive_lower, "<="


def print_attribute_profile(
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    limit: int,
) -> None:
    if limit <= 0:
        return

    numeric_profiles: list[tuple[float, str, str, str, str]] = []
    for field in numeric_fields(positive_rows):
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
    for field in ("body_shape", "source"):
        positive_counts = Counter(
            row.get(field, "") for row in positive_rows if row.get(field, "")
        )
        negative_counts = Counter(
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


def print_route_patterns(
    rows: list[dict[str, str]],
    route: tuple[str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    max_conditions: int,
    beam_width: int,
    show_examples: int,
    show_near_misses: int,
    include_merged_positives: bool,
    profile_fields: int,
) -> None:
    expected, got = route
    positive_rows = route_positive_rows(rows, route, include_merged_positives)
    negative_rows = [
        row for row in rows
        if (
            row.get("expected") == row.get("primary") or
            (not include_merged_positives and row.get("merged_expected") == "1")
        )
    ]
    protected_by_expected = Counter(row.get("expected", "") for row in negative_rows)
    print(
        f"route {expected}->{got} positives={len({sample_key(row) for row in positive_rows})} "
        f"rows={len(positive_rows)} protected_correct={len({sample_key(row) for row in negative_rows})} "
        f"rows={len(negative_rows)}"
    )
    if not positive_rows:
        print("  --")
        return
    print(
        "  protected_by_expected="
        + " ".join(f"{key}={value}" for key, value in sorted(protected_by_expected.items()))
    )
    print_attribute_profile(positive_rows, negative_rows, profile_fields)

    positive_sample_bits = sample_bit_map(positive_rows)
    negative_sample_bits = sample_bit_map(negative_rows)
    all_sample_bits = sample_bit_map(rows)
    positive_counter = SampleCounter(positive_sample_bits)
    negative_counter = SampleCounter(negative_sample_bits)
    all_counter = SampleCounter(all_sample_bits)
    side_effect_base = side_effect_base_masks(rows, expected)
    patterns = build_patterns(positive_rows)
    matches = [
        PatternMatch(
            label=pattern.label,
            positive_mask=mask_for_pattern(positive_rows, pattern),
            negative_mask=mask_for_pattern(negative_rows, pattern),
            all_mask=mask_for_pattern(rows, pattern),
            constraint=pattern.constraint,
        )
        for pattern in patterns
    ]

    def collect_results(max_negative_samples_limit: int | None, include_multi_condition: bool) -> list[RuleResult]:
        results: list[RuleResult] = []
        for match in matches:
            result = result_from_masks(
                match.label,
                match.positive_mask,
                match.negative_mask,
                match.all_mask,
                positive_rows,
                negative_rows,
                rows,
                positive_counter,
                negative_counter,
                all_counter,
                side_effect_base,
                expected,
                max_negative_samples_limit,
                show_examples,
            )
            if result is not None and result.positive_samples >= min_positive_samples:
                results.append(result)
        if include_multi_condition:
            results.extend(
                extend_condition_search(
                    matches,
                    positive_rows,
                    negative_rows,
                    rows,
                    positive_counter,
                    negative_counter,
                    all_counter,
                    side_effect_base,
                    expected,
                    min_positive_samples,
                    max_negative_samples_limit,
                    max_conditions,
                    max(1, beam_width),
                    show_examples,
                )
            )
        deduped: dict[str, RuleResult] = {}
        for result in results:
            existing = deduped.get(result.rule)
            if existing is None or rank_result(result) < rank_result(existing):
                deduped[result.rule] = result
        return sorted(deduped.values(), key=rank_result)

    def print_rules(rules: list[RuleResult]) -> None:
        for result in rules:
            print(
                f"  +{result.positive_samples} rows={result.positive_rows} "
                f"-{result.negative_samples} rows={result.negative_rows} "
                f"foreign={result.foreign_samples} rows={result.foreign_rows} "
                f"new-active={result.new_active_samples} rows={result.new_active_rows} "
                f"primary-break={result.primary_break_samples} rows={result.primary_break_rows} :: {result.rule}"
            )
            if show_examples <= 0:
                continue
            if result.positive_examples:
                print("    positive examples:")
                for row in result.positive_examples:
                    print(f"      {format_example(row)}")
            if result.negative_examples:
                print("    protected-correct examples:")
                for row in result.negative_examples:
                    print(f"      {format_example(row)}")
            if result.new_active_examples:
                print("    new-active side-effect examples:")
                for row in result.new_active_examples:
                    print(f"      {format_example(row)}")
            if result.primary_break_examples:
                print("    primary-break side-effect examples:")
                for row in result.primary_break_examples:
                    print(f"      {format_example(row)}")

    ranked = collect_results(max_negative_samples, True)[:limit]
    if not ranked:
        print("  --")
        if show_near_misses > 0:
            near_misses = [
                result
                for result in collect_results(None, False)
                if result.negative_samples > max_negative_samples
            ][:show_near_misses]
            if near_misses:
                print("  nearest over-budget single-condition candidate rules:")
                print_rules(near_misses)
        return
    print_rules(ranked)


def route_patterns_text(
    rows: list[dict[str, str]],
    route: tuple[str, str],
    settings: RoutePatternSettings,
) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        route_rows = route_positive_rows(rows, route, settings.include_merged_rows)
        route_samples = route_sample_count(route_rows)
        if (
            route_samples < settings.min_route_positive_samples
            or len(route_rows) < settings.min_route_positive_rows
        ):
            expected, got = route
            print(
                f"route {expected}->{got} skipped: positives={route_samples} rows={len(route_rows)} "
                f"below min-route-positive-samples={settings.min_route_positive_samples} "
                f"min-route-positive-rows={settings.min_route_positive_rows}"
            )
            return buffer.getvalue()
        print_route_patterns(
            rows,
            route,
            settings.limit,
            settings.min_positive_samples,
            settings.max_negative_samples,
            settings.max_conditions,
            settings.beam_width,
            settings.show_examples,
            settings.show_near_misses,
            settings.include_merged_rows,
            settings.profile_fields,
        )
    return buffer.getvalue()


def route_patterns_worker(
    task: tuple[int, list[dict[str, str]], tuple[str, str], RoutePatternSettings],
) -> tuple[int, str]:
    index, rows, route, settings = task
    return index, route_patterns_text(rows, route, settings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--route", action="append", default=[], help="route like tom->snare; repeatable")
    parser.add_argument("--top-routes", type=int, default=5)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-positive-samples", type=int, default=3)
    parser.add_argument(
        "--min-route-positive-samples",
        type=int,
        default=0,
        help="skip route searches with fewer positive samples before mining candidate rules",
    )
    parser.add_argument(
        "--min-route-positive-rows",
        type=int,
        default=0,
        help="skip route searches with fewer positive rows before mining candidate rules",
    )
    parser.add_argument("--max-negative-samples", type=int, default=0)
    parser.add_argument("--max-conditions", type=int, default=3)
    parser.add_argument("--beam-width", type=int, default=220)
    parser.add_argument("--show-examples", "--row-examples", dest="show_examples", type=int, default=0)
    parser.add_argument(
        "--show-near-misses",
        type=int,
        default=0,
        help="when no rule fits the negative budget, show this many closest over-budget candidates",
    )
    parser.add_argument(
        "--include-merged-rows",
        action="store_true",
        help="mine drum rows whose expected level was credited from a later frame as positives",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="mine independent routes in parallel when multiple routes are selected",
    )
    parser.add_argument(
        "--profile-fields",
        type=int,
        default=0,
        help=(
            "print this many ranked numeric and category attribute profiles for each route "
            "before candidate rules"
        ),
    )
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    source_stem_counts = Counter(path.stem for path in args.logs)
    for path in args.logs:
        source = path.stem if source_stem_counts[path.stem] == 1 else path.as_posix()
        rows.extend(parse_rows(path, source))
    merged_rows = sum(1 for row in rows if row.get("merged_expected") == "1")
    min_route_positive_samples = max(0, args.min_route_positive_samples)
    min_route_positive_rows = max(0, args.min_route_positive_rows)
    routes = (
        [parse_route(route) for route in args.route]
        if args.route
        else top_routes(
            rows,
            args.top_routes,
            min_route_positive_samples,
            min_route_positive_rows,
            args.include_merged_rows,
        )
    )
    print("candidate rules are attribute selectors; rerun analyzer gates to validate runtime level and primary-label effects")
    if merged_rows and not args.include_merged_rows:
        print(
            f"protecting merged expected-credit rows={merged_rows}; pass --include-merged-rows to mine them"
        )
    if not routes:
        print("no routes matched the route-level positive thresholds")
        return 0
    settings = RoutePatternSettings(
        limit=max(1, args.limit),
        min_positive_samples=max(1, args.min_positive_samples),
        max_negative_samples=max(0, args.max_negative_samples),
        max_conditions=max(1, args.max_conditions),
        beam_width=max(1, args.beam_width),
        show_examples=max(0, args.show_examples),
        show_near_misses=max(0, args.show_near_misses),
        include_merged_rows=args.include_merged_rows,
        min_route_positive_samples=min_route_positive_samples,
        min_route_positive_rows=min_route_positive_rows,
        profile_fields=max(0, args.profile_fields),
    )
    jobs = min(max(1, args.jobs), len(routes))
    if jobs <= 1:
        for route in routes:
            print(route_patterns_text(rows, route, settings), end="")
    else:
        outputs: list[str] = [""] * len(routes)
        tasks = [(index, rows, route, settings) for index, route in enumerate(routes)]
        with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
            for index, text in executor.map(route_patterns_worker, tasks):
                outputs[index] = text
        for text in outputs:
            print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
