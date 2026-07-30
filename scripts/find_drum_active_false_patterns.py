#!/usr/bin/env python3
"""Find candidate rules for suppressing false active drum bars."""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import csv
import dataclasses
import io
import itertools
import pathlib
import statistics
from collections import Counter
from collections.abc import Callable


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
SKIP_FIELDS = {"sample", "expected", "got", "primary", "source", "merged_expected"}


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
class Match:
    label: str
    positive_mask: int
    protected_mask: int
    constraint: Constraint | None


@dataclasses.dataclass(frozen=True)
class State:
    labels: tuple[str, ...]
    constraints: tuple[Constraint, ...]
    positive_mask: int
    protected_mask: int
    next_index: int


@dataclasses.dataclass(frozen=True)
class Result:
    rule: str
    constraints: tuple[Constraint, ...]
    positive_rows: int
    positive_samples: int
    protected_rows: int
    protected_samples: int
    positive_examples: list[dict[str, str]]
    protected_examples: list[dict[str, str]]


@dataclasses.dataclass(frozen=True)
class RouteAnalysis:
    route: tuple[str, str]
    positive_rows: list[dict[str, str]]
    protected_rows: list[dict[str, str]]
    positive_samples: int
    protected_samples: int
    candidates: list[Result]
    accepted: list[Result]


@dataclasses.dataclass(frozen=True)
class RouteSummary:
    kind: str
    route: tuple[str, str]
    rule: str
    positive_samples: int
    positive_rows: int
    protected_samples: int
    protected_rows: int
    protected_total_samples: int


@dataclasses.dataclass(frozen=True)
class Settings:
    threshold: float
    limit: int
    min_positive_samples: int
    max_protected_samples: int
    max_conditions: int
    beam_width: int
    show_examples: int
    show_near_misses: int
    protected_margin: float
    protected_relative_margin: float
    excluded_fields: frozenset[str]


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle, delimiter="\t"):
            if not raw.get("sample") or not raw.get("expected"):
                continue
            row = {key: value for key, value in raw.items() if key and value is not None}
            row["source"] = path.stem
            row["primary"] = row.get("got") or primary_from_levels(row)
            add_ratios(row)
            rows.append(row)
    return rows


def primary_from_levels(row: dict[str, str]) -> str:
    best = "none"
    best_level = 0.0
    for category in CATEGORIES:
        level = as_float(row, f"{category}_level") or 0.0
        if level > 0.30 and level > best_level:
            best = category
            best_level = level
    return best


def add_ratios(row: dict[str, str]) -> None:
    for lhs, rhs in (
        ("tom", "snare"),
        ("tom", "kick"),
        ("snare", "kick"),
        ("hihat", "rim"),
        ("crash", "hihat"),
        ("ride", "hihat"),
        ("kick", "bass"),
    ):
        for field in ("band", "seg", "shape_score", "trigger", "level"):
            lhs_value = as_float(row, f"{lhs}_{field}")
            rhs_value = as_float(row, f"{rhs}_{field}")
            if lhs_value is None or rhs_value is None or abs(rhs_value) < 1.0e-6:
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
        if lhs_value is None or rhs_value is None or abs(rhs_value) < 1.0e-6:
            continue
        row[label] = f"{lhs_value / rhs_value:.9f}"


def sample_key(row: dict[str, str]) -> str:
    return f"{row.get('source', '')}\0{row.get('sample', '')}"


def sample_bits(rows: list[dict[str, str]]) -> list[int]:
    by_key: dict[str, int] = {}
    bits: list[int] = []
    for row in rows:
        key = sample_key(row)
        if key not in by_key:
            by_key[key] = 1 << len(by_key)
        bits.append(by_key[key])
    return bits


def sample_count(mask: int, row_bits: list[int]) -> int:
    samples = 0
    work = mask
    while work:
        bit = work & -work
        index = bit.bit_length() - 1
        samples |= row_bits[index]
        work ^= bit
    return samples.bit_count()


def selected_examples(rows: list[dict[str, str]], mask: int, limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    work = mask
    while work and len(selected) < limit:
        bit = work & -work
        index = bit.bit_length() - 1
        row = rows[index]
        key = sample_key(row)
        if key not in seen:
            seen.add(key)
            selected.append(row)
        work ^= bit
    return selected


def quantile(values: list[float], fraction: float) -> float:
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def thresholds(values: list[float]) -> list[float]:
    if not values:
        return []
    ordered = sorted(values)
    return sorted(
        {
            ordered[0],
            quantile(ordered, 0.10),
            quantile(ordered, 0.25),
            statistics.median(ordered),
            quantile(ordered, 0.75),
            quantile(ordered, 0.90),
            ordered[-1],
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


def category_pattern(field: str, value: str) -> Pattern:
    return Pattern(
        f"{field}={value}",
        lambda row, field=field, value=value: row.get(field, "") == value,
        Constraint(field, "category", value),
    )


def field_excluded(field: str, excluded_fields: frozenset[str]) -> bool:
    return any(field == excluded or excluded in field for excluded in excluded_fields)


def numeric_fields(rows: list[dict[str, str]], excluded_fields: frozenset[str]) -> list[str]:
    fields: set[str] = set()
    for row in rows:
        for field, value in row.items():
            if field in SKIP_FIELDS or field_excluded(field, excluded_fields):
                continue
            try:
                float(value)
            except ValueError:
                continue
            fields.add(field)
    return sorted(fields)


def build_patterns(positive_rows: list[dict[str, str]], excluded_fields: frozenset[str]) -> list[Pattern]:
    patterns: list[Pattern] = []
    for field in ("body_shape",):
        if field_excluded(field, excluded_fields):
            continue
        for value in sorted({row.get(field, "") for row in positive_rows if row.get(field, "")}):
            patterns.append(category_pattern(field, value))
    for field in numeric_fields(positive_rows, excluded_fields):
        values = [value for row in positive_rows if (value := as_float(row, field)) is not None]
        for threshold in thresholds(values):
            patterns.append(numeric_pattern(field, "<=", threshold))
            patterns.append(numeric_pattern(field, ">=", threshold))
    seen: set[str] = set()
    deduped: list[Pattern] = []
    for pattern in patterns:
        if pattern.label in seen:
            continue
        seen.add(pattern.label)
        deduped.append(pattern)
    return deduped


def pattern_matches(row: dict[str, str], pattern: Pattern, protected_margin: float = 0.0,
                    protected_relative_margin: float = 0.0) -> bool:
    constraint = pattern.constraint
    if constraint is None or constraint.kind == "category" or protected_margin <= 0.0:
        return pattern.predicate(row)
    value = as_float(row, constraint.field)
    if value is None:
        return False
    threshold = float(constraint.value)
    margin = max(protected_margin, abs(threshold) * max(0.0, protected_relative_margin))
    if constraint.kind == "upper":
        return value <= threshold + margin
    if constraint.kind == "lower":
        return value >= threshold - margin
    return pattern.predicate(row)


def mask_for(rows: list[dict[str, str]], pattern: Pattern, protected_margin: float = 0.0,
             protected_relative_margin: float = 0.0) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern_matches(row, pattern, protected_margin, protected_relative_margin):
            mask |= 1 << index
    return mask


def constraints_compatible(existing: tuple[Constraint, ...], new: Constraint | None) -> bool:
    if new is None:
        return True
    for constraint in existing:
        if constraint.field != new.field:
            continue
        if constraint.kind == "category" or new.kind == "category":
            return False
        if constraint.kind == new.kind:
            return False
        lower = float(constraint.value if constraint.kind == "lower" else new.value)
        upper = float(constraint.value if constraint.kind == "upper" else new.value)
        return lower < upper
    return True


def rank_result(result: Result) -> tuple[int, int, int, int, str]:
    return (
        result.protected_samples,
        result.protected_rows,
        -result.positive_samples,
        result.rule.count(" AND "),
        result.rule,
    )


def rank_state(
    state: State,
    positive_rows: list[dict[str, str]],
    protected_rows: list[dict[str, str]],
    positive_bits: list[int],
    protected_bits: list[int],
) -> tuple[int, int, int, int, str]:
    return rank_result(
        result_from_state(state, positive_rows, protected_rows, positive_bits, protected_bits, 0)
    )


def result_from_state(
    state: State,
    positive_rows: list[dict[str, str]],
    protected_rows: list[dict[str, str]],
    positive_bits: list[int],
    protected_bits: list[int],
    show_examples: int,
) -> Result:
    return Result(
        rule=" AND ".join(state.labels),
        constraints=state.constraints,
        positive_rows=state.positive_mask.bit_count(),
        positive_samples=sample_count(state.positive_mask, positive_bits),
        protected_rows=state.protected_mask.bit_count(),
        protected_samples=sample_count(state.protected_mask, protected_bits),
        positive_examples=selected_examples(positive_rows, state.positive_mask, show_examples),
        protected_examples=selected_examples(protected_rows, state.protected_mask, show_examples),
    )


def search_results(
    positive_rows: list[dict[str, str]],
    protected_rows: list[dict[str, str]],
    settings: Settings,
) -> list[Result]:
    positive_bits = sample_bits(positive_rows)
    protected_bits = sample_bits(protected_rows)
    matches: list[Match] = []
    for pattern in build_patterns(positive_rows, settings.excluded_fields):
        positive_mask = mask_for(positive_rows, pattern)
        if sample_count(positive_mask, positive_bits) < settings.min_positive_samples:
            continue
        matches.append(
            Match(
                label=pattern.label,
                positive_mask=positive_mask,
                protected_mask=mask_for(
                    protected_rows,
                    pattern,
                    settings.protected_margin,
                    settings.protected_relative_margin,
                ),
                constraint=pattern.constraint,
            )
        )
    ordered = sorted(matches, key=lambda match: match.label)
    states: list[State] = [
        State(
            labels=(match.label,),
            constraints=(match.constraint,) if match.constraint is not None else (),
            positive_mask=match.positive_mask,
            protected_mask=match.protected_mask,
            next_index=index + 1,
        )
        for index, match in enumerate(ordered)
    ]
    states = sorted(
        states,
        key=lambda state: rank_state(state, positive_rows, protected_rows, positive_bits, protected_bits),
    )[: max(1, settings.beam_width)]
    results: dict[tuple[int, int], Result] = {}
    for condition_count in range(1, max(1, settings.max_conditions) + 1):
        next_states: dict[tuple[int, int], State] = {}
        for state in states:
            result = result_from_state(
                state, positive_rows, protected_rows, positive_bits, protected_bits,
                settings.show_examples
            )
            if result.positive_samples >= settings.min_positive_samples:
                key = (state.positive_mask, state.protected_mask)
                previous = results.get(key)
                if previous is None or rank_result(result) < rank_result(previous):
                    results[key] = result
            if condition_count >= settings.max_conditions:
                continue
            for match_index in range(state.next_index, len(ordered)):
                match = ordered[match_index]
                if not constraints_compatible(state.constraints, match.constraint):
                    continue
                positive_mask = state.positive_mask & match.positive_mask
                if sample_count(positive_mask, positive_bits) < settings.min_positive_samples:
                    continue
                protected_mask = state.protected_mask & match.protected_mask
                candidate = State(
                    labels=state.labels + (match.label,),
                    constraints=(
                        state.constraints + (match.constraint,)
                        if match.constraint is not None else state.constraints
                    ),
                    positive_mask=positive_mask,
                    protected_mask=protected_mask,
                    next_index=match_index + 1,
                )
                key = (positive_mask, protected_mask)
                previous_state = next_states.get(key)
                if previous_state is None:
                    next_states[key] = candidate
                    continue
                if rank_state(candidate, positive_rows, protected_rows, positive_bits, protected_bits) < rank_state(
                    previous_state, positive_rows, protected_rows, positive_bits, protected_bits
                ):
                    next_states[key] = candidate
        states = sorted(
            next_states.values(),
            key=lambda state: rank_state(state, positive_rows, protected_rows, positive_bits, protected_bits),
        )[: max(1, settings.beam_width)]
        if not states:
            break
    return sorted(results.values(), key=rank_result)


def false_rows_for_route(
    rows: list[dict[str, str]],
    expected: str,
    active: str,
    threshold: float,
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("expected") == expected
        and active != expected
        and (as_float(row, f"{active}_level") or 0.0) > threshold
    ]


def protected_rows_for_active(
    rows: list[dict[str, str]],
    active: str,
    threshold: float,
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("expected") == active and (as_float(row, f"{active}_level") or 0.0) > threshold
    ]


def top_routes(rows: list[dict[str, str]], threshold: float, limit: int) -> list[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    samples: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        expected = row.get("expected", "")
        if expected not in CATEGORIES:
            continue
        for active in CATEGORIES:
            if active == expected:
                continue
            if (as_float(row, f"{active}_level") or 0.0) > threshold:
                route = (expected, active)
                counts[route] += 1
                samples.setdefault(route, set()).add(sample_key(row))
    return [
        route
        for route, _count in sorted(
            counts.items(),
            key=lambda item: (-len(samples.get(item[0], set())), -item[1], item[0][0], item[0][1]),
        )[: max(1, limit)]
    ]


def parse_route(text: str) -> tuple[str, str]:
    if "->" not in text:
        raise SystemExit(f"invalid route `{text}`; expected e.g. kick->tom")
    expected, active = text.split("->", 1)
    if expected not in CATEGORIES or active not in CATEGORIES or expected == active:
        raise SystemExit(f"invalid route `{text}`; expected different known drum categories")
    return expected, active


def format_example(row: dict[str, str], active: str) -> str:
    expected = row.get("expected", "")
    parts = [
        f"{row.get('source', '')}:{row.get('sample', '')} {expected}->{active}",
        f"got={row.get('primary', '')}",
        f"{active}:level={value_text(row, active + '_level')}",
        f"{active}:seg={value_text(row, active + '_seg')}",
        f"{expected}:level={value_text(row, expected + '_level')}",
    ]
    for field in ("low", "mid", "high", "kick_body", "snare_body", "tom_body", "snare_crack"):
        if row.get(field, ""):
            parts.append(f"{field}={value_text(row, field)}")
    return " ".join(parts)


def value_text(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "-"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def analyze_route(
    rows: list[dict[str, str]],
    extra_protected_rows: list[dict[str, str]],
    route: tuple[str, str],
    settings: Settings,
) -> RouteAnalysis:
    expected, active = route
    positive_rows = false_rows_for_route(rows, expected, active, settings.threshold)
    protected_rows = protected_rows_for_active(rows, active, settings.threshold) + protected_rows_for_active(
        extra_protected_rows, active, settings.threshold
    )
    positive_samples = len({sample_key(row) for row in positive_rows})
    protected_samples = len({sample_key(row) for row in protected_rows})
    candidates: list[Result] = []
    accepted: list[Result] = []
    if positive_samples >= settings.min_positive_samples:
        candidates = search_results(positive_rows, protected_rows, settings)
        accepted = [
            result
            for result in candidates
            if result.protected_samples <= settings.max_protected_samples
        ][: settings.limit]
    return RouteAnalysis(
        route=route,
        positive_rows=positive_rows,
        protected_rows=protected_rows,
        positive_samples=positive_samples,
        protected_samples=protected_samples,
        candidates=candidates,
        accepted=accepted,
    )


def route_summaries(analysis: RouteAnalysis, settings: Settings) -> list[RouteSummary]:
    summaries: list[RouteSummary] = []
    for result in analysis.accepted[: settings.limit]:
        summaries.append(
            RouteSummary(
                kind="candidate",
                route=analysis.route,
                rule=result.rule,
                positive_samples=result.positive_samples,
                positive_rows=result.positive_rows,
                protected_samples=result.protected_samples,
                protected_rows=result.protected_rows,
                protected_total_samples=analysis.protected_samples,
            )
        )
    if not summaries:
        over_budget = [
            result for result in analysis.candidates
            if result.protected_samples > settings.max_protected_samples
        ]
        if over_budget:
            result = over_budget[0]
            summaries.append(
                RouteSummary(
                    kind="nearest",
                    route=analysis.route,
                    rule=result.rule,
                    positive_samples=result.positive_samples,
                    positive_rows=result.positive_rows,
                    protected_samples=result.protected_samples,
                    protected_rows=result.protected_rows,
                    protected_total_samples=analysis.protected_samples,
                )
            )
    return summaries


def summary_rank(summary: RouteSummary) -> tuple[int, int, int, int, str, str]:
    return (
        0 if summary.kind == "candidate" else 1,
        summary.protected_samples,
        -summary.positive_samples,
        summary.protected_rows,
        f"{summary.route[0]}->{summary.route[1]}",
        summary.rule,
    )


def print_ranked_summary(summaries: list[RouteSummary], limit: int) -> None:
    print("ranked active false suppression opportunities")
    print("  attribute-level candidates; validate runtime changes with the full drum gate")
    if not summaries:
        print("  no matching suppression opportunities")
        return
    for summary in sorted(summaries, key=summary_rank)[: max(0, limit)]:
        expected, active = summary.route
        print(
            f"  {summary.kind} {expected}->{active} "
            f"+{summary.positive_samples} rows={summary.positive_rows} "
            f"-{summary.protected_samples} rows={summary.protected_rows} "
            f"protected_true_{active}={summary.protected_total_samples} :: {summary.rule}"
        )


def route_text_from_analysis(analysis: RouteAnalysis, settings: Settings) -> str:
    expected, active = analysis.route
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print(
            f"route {expected}->{active} positives={analysis.positive_samples} "
            f"rows={len(analysis.positive_rows)} "
            f"protected_true_{active}={analysis.protected_samples} "
            f"rows={len(analysis.protected_rows)}"
        )
        if analysis.positive_samples < settings.min_positive_samples:
            print("  --")
            return buffer.getvalue()
        if not analysis.accepted:
            print("  --")
            near = [
                result
                for result in analysis.candidates
                if result.protected_samples > settings.max_protected_samples
            ][: settings.show_near_misses]
            if near:
                print("  nearest over-budget rules:")
                print_results(near, active, settings.show_examples, analysis.protected_rows, 0)
            return buffer.getvalue()
        print_results(
            analysis.accepted,
            active,
            settings.show_examples,
            analysis.protected_rows,
            settings.show_near_misses,
        )
    return buffer.getvalue()


def route_text(
    rows: list[dict[str, str]],
    extra_protected_rows: list[dict[str, str]],
    route: tuple[str, str],
    settings: Settings,
) -> str:
    return route_text_from_analysis(analyze_route(rows, extra_protected_rows, route, settings), settings)


def constraint_distance(row: dict[str, str], constraints: tuple[Constraint, ...]) -> tuple[int, float] | None:
    misses = 0
    score = 0.0
    for constraint in constraints:
        if constraint.kind == "category":
            if row.get(constraint.field, "") != str(constraint.value):
                return None
            continue
        value = as_float(row, constraint.field)
        if value is None:
            return None
        threshold = float(constraint.value)
        scale = max(1.0, abs(threshold))
        if constraint.kind == "upper":
            distance = max(0.0, value - threshold)
        elif constraint.kind == "lower":
            distance = max(0.0, threshold - value)
        else:
            continue
        if distance > 0.0:
            misses += 1
            score += distance / scale
    return misses, score


def nearest_protected_examples(
    protected_rows: list[dict[str, str]],
    result: Result,
    limit: int,
) -> list[dict[str, str]]:
    if limit <= 0 or not result.constraints:
        return []
    excluded = {sample_key(row) for row in result.protected_examples}
    candidates: list[tuple[int, float, str, dict[str, str]]] = []
    seen: set[str] = set()
    for row in protected_rows:
        key = sample_key(row)
        if key in seen or key in excluded:
            continue
        distance = constraint_distance(row, result.constraints)
        if distance is None:
            continue
        seen.add(key)
        misses, score = distance
        candidates.append((misses, score, key, row))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    return [row for _misses, _score, _key, row in candidates[:limit]]


def format_constraint_status(row: dict[str, str], constraint: Constraint) -> str:
    if constraint.kind == "category":
        value = row.get(constraint.field, "") or "-"
        expected = str(constraint.value)
        status = "ok" if value == expected else f"want {expected}"
        return f"{constraint.field}={value} {status}"
    value = as_float(row, constraint.field)
    if value is None:
        return f"{constraint.field}=-"
    threshold = float(constraint.value)
    if constraint.kind == "upper":
        delta = value - threshold
        status = "ok" if delta <= 0.0 else f"+{format_value(delta)}"
        return (
            f"{constraint.field}={value_text(row, constraint.field)} "
            f"<= {format_value(threshold)} {status}"
        )
    if constraint.kind == "lower":
        delta = threshold - value
        status = "ok" if delta <= 0.0 else f"-{format_value(delta)}"
        return (
            f"{constraint.field}={value_text(row, constraint.field)} "
            f">= {format_value(threshold)} {status}"
        )
    return constraint.field


def format_near_example(row: dict[str, str], active: str, constraints: tuple[Constraint, ...]) -> str:
    statuses = " ".join(format_constraint_status(row, constraint) for constraint in constraints)
    return f"{format_example(row, active)} near: {statuses}"


def print_results(
    results: list[Result],
    active: str,
    show_examples: int,
    protected_rows: list[dict[str, str]],
    show_near_misses: int,
) -> None:
    for result in results:
        print(
            f"  +{result.positive_samples} rows={result.positive_rows} "
            f"-{result.protected_samples} rows={result.protected_rows} :: {result.rule}"
        )
        if show_examples > 0:
            if result.positive_examples:
                print("    false-active examples:")
                for row in result.positive_examples:
                    print(f"      {format_example(row, active)}")
            if result.protected_examples:
                print("    protected true-active examples:")
                for row in result.protected_examples:
                    print(f"      {format_example(row, active)}")
        near_examples = nearest_protected_examples(protected_rows, result, show_near_misses)
        if near_examples:
            print("    nearest protected true-active near misses:")
            for row in near_examples:
                print(f"      {format_near_example(row, active, result.constraints)}")


def worker(
    task: tuple[int, list[dict[str, str]], list[dict[str, str]], tuple[str, str], Settings]
) -> tuple[int, str, list[RouteSummary]]:
    index, rows, extra_protected_rows, route, settings = task
    analysis = analyze_route(rows, extra_protected_rows, route, settings)
    return index, route_text_from_analysis(analysis, settings), route_summaries(analysis, settings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", type=pathlib.Path)
    parser.add_argument(
        "--extra-protected-rows",
        action="append",
        default=[],
        type=pathlib.Path,
        help="TSV rows used only as protected true-hit rows, not as false-active positives",
    )
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--top-routes", type=int, default=6)
    parser.add_argument("--threshold", type=float, default=0.30)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--min-positive-samples", type=int, default=8)
    parser.add_argument("--max-protected-samples", type=int, default=0)
    parser.add_argument("--max-conditions", type=int, default=2)
    parser.add_argument("--beam-width", type=int, default=160)
    parser.add_argument("--show-examples", type=int, default=0)
    parser.add_argument("--show-near-misses", type=int, default=0)
    parser.add_argument(
        "--protected-margin",
        type=float,
        default=0.002,
        help="expand numeric rule thresholds by this absolute amount for protected true-hit rows",
    )
    parser.add_argument(
        "--protected-relative-margin",
        type=float,
        default=0.001,
        help="expand numeric rule thresholds by this threshold-relative fraction for protected rows",
    )
    parser.add_argument(
        "--exclude-fields",
        default="",
        help=(
            "comma-separated candidate fields to skip; derived ratio fields containing "
            "an excluded field name are skipped too"
        ),
    )
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()

    rows = list(itertools.chain.from_iterable(read_rows(path) for path in args.rows))
    extra_protected_rows = list(
        itertools.chain.from_iterable(read_rows(path) for path in args.extra_protected_rows)
    )
    routes = [parse_route(route) for route in args.route] if args.route else top_routes(
        rows, args.threshold, args.top_routes
    )
    print(
        f"drum active false pattern candidates: rows={len(rows)} "
        f"extra_protected_rows={len(extra_protected_rows)} "
        f"threshold={args.threshold:.2f} routes={len(routes)}"
    )
    settings = Settings(
        threshold=args.threshold,
        limit=max(0, args.limit),
        min_positive_samples=max(1, args.min_positive_samples),
        max_protected_samples=max(0, args.max_protected_samples),
        max_conditions=max(1, args.max_conditions),
        beam_width=max(1, args.beam_width),
        show_examples=max(0, args.show_examples),
        show_near_misses=max(0, args.show_near_misses),
        protected_margin=max(0.0, args.protected_margin),
        protected_relative_margin=max(0.0, args.protected_relative_margin),
        excluded_fields=frozenset(field.strip() for field in args.exclude_fields.split(",") if field.strip()),
    )
    if not routes:
        return 0
    summaries: list[RouteSummary] = []
    jobs = min(max(1, args.jobs), len(routes))
    if jobs == 1:
        for route in routes:
            analysis = analyze_route(rows, extra_protected_rows, route, settings)
            print(route_text_from_analysis(analysis, settings), end="")
            summaries.extend(route_summaries(analysis, settings))
        print_ranked_summary(summaries, settings.limit)
        return 0
    outputs = [""] * len(routes)
    tasks = [
        (index, rows, extra_protected_rows, route, settings)
        for index, route in enumerate(routes)
    ]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        for index, text, route_summaries_ in executor.map(worker, tasks):
            outputs[index] = text
            summaries.extend(route_summaries_)
    for text in outputs:
        print(text, end="")
    print_ranked_summary(summaries, settings.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
