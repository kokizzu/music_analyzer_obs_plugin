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
    positive_rows: int
    positive_samples: int
    protected_rows: int
    protected_samples: int
    positive_examples: list[dict[str, str]]
    protected_examples: list[dict[str, str]]


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


def numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    fields: set[str] = set()
    for row in rows:
        for field, value in row.items():
            if field in SKIP_FIELDS:
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
    seen: set[str] = set()
    deduped: list[Pattern] = []
    for pattern in patterns:
        if pattern.label in seen:
            continue
        seen.add(pattern.label)
        deduped.append(pattern)
    return deduped


def mask_for(rows: list[dict[str, str]], pattern: Pattern) -> int:
    mask = 0
    for index, row in enumerate(rows):
        if pattern.predicate(row):
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
    for pattern in build_patterns(positive_rows):
        positive_mask = mask_for(positive_rows, pattern)
        if sample_count(positive_mask, positive_bits) < settings.min_positive_samples:
            continue
        matches.append(
            Match(
                label=pattern.label,
                positive_mask=positive_mask,
                protected_mask=mask_for(protected_rows, pattern),
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


def route_text(rows: list[dict[str, str]], route: tuple[str, str], settings: Settings) -> str:
    expected, active = route
    positive_rows = false_rows_for_route(rows, expected, active, settings.threshold)
    protected_rows = protected_rows_for_active(rows, active, settings.threshold)
    positive_samples = len({sample_key(row) for row in positive_rows})
    protected_samples = len({sample_key(row) for row in protected_rows})
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print(
            f"route {expected}->{active} positives={positive_samples} rows={len(positive_rows)} "
            f"protected_true_{active}={protected_samples} rows={len(protected_rows)}"
        )
        if positive_samples < settings.min_positive_samples:
            print("  --")
            return buffer.getvalue()
        candidates = search_results(positive_rows, protected_rows, settings)
        accepted = [
            result
            for result in candidates
            if result.protected_samples <= settings.max_protected_samples
        ][: settings.limit]
        if not accepted:
            print("  --")
            near = [
                result
                for result in candidates
                if result.protected_samples > settings.max_protected_samples
            ][: settings.show_near_misses]
            if near:
                print("  nearest over-budget rules:")
                print_results(near, active, settings.show_examples)
            return buffer.getvalue()
        print_results(accepted, active, settings.show_examples)
    return buffer.getvalue()


def print_results(results: list[Result], active: str, show_examples: int) -> None:
    for result in results:
        print(
            f"  +{result.positive_samples} rows={result.positive_rows} "
            f"-{result.protected_samples} rows={result.protected_rows} :: {result.rule}"
        )
        if show_examples <= 0:
            continue
        if result.positive_examples:
            print("    false-active examples:")
            for row in result.positive_examples:
                print(f"      {format_example(row, active)}")
        if result.protected_examples:
            print("    protected true-active examples:")
            for row in result.protected_examples:
                print(f"      {format_example(row, active)}")


def worker(task: tuple[int, list[dict[str, str]], tuple[str, str], Settings]) -> tuple[int, str]:
    index, rows, route, settings = task
    return index, route_text(rows, route, settings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", type=pathlib.Path)
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
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()

    rows = list(itertools.chain.from_iterable(read_rows(path) for path in args.rows))
    routes = [parse_route(route) for route in args.route] if args.route else top_routes(
        rows, args.threshold, args.top_routes
    )
    print(
        f"drum active false pattern candidates: rows={len(rows)} "
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
    )
    if not routes:
        return 0
    jobs = min(max(1, args.jobs), len(routes))
    if jobs == 1:
        for route in routes:
            print(route_text(rows, route, settings), end="")
        return 0
    outputs = [""] * len(routes)
    tasks = [(index, rows, route, settings) for index, route in enumerate(routes)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        for index, text in executor.map(worker, tasks):
            outputs[index] = text
    for text in outputs:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
