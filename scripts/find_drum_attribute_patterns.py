#!/usr/bin/env python3
"""Find candidate attribute patterns in drum primary debug rows."""

from __future__ import annotations

import argparse
import dataclasses
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
    positive_rows: int
    positive_samples: int
    negative_rows: int
    negative_samples: int
    positive_examples: list[dict[str, str]]
    negative_examples: list[dict[str, str]]


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


def parse_rows(path: pathlib.Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(errors="replace").splitlines():
        row_match = ROW_RE.search(line)
        transient_match = TRANSIENT_RE.search(line)
        if not row_match or not transient_match:
            continue
        row: dict[str, str] = {
            "sample": row_match.group("sample"),
            "expected": row_match.group("expected"),
        }
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
            row[f"{lhs}_{rhs}_{field}_ratio"] = f"{lhs_value / (rhs_value + 1.0e-9):.9f}"


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


def numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    fields = set()
    for row in rows:
        for field, value in row.items():
            if field in {"sample", "expected", "primary"}:
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


def sample_bit_map(rows: list[dict[str, str]]) -> list[int]:
    bits: dict[str, int] = {}
    row_bits: list[int] = []
    for row in rows:
        sample = row.get("sample", "")
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


def selected_samples_from_mask(rows: list[dict[str, str]], row_mask: int, limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    while row_mask and len(selected) < limit:
        bit = row_mask & -row_mask
        index = bit.bit_length() - 1
        row = rows[index]
        sample = row.get("sample", "")
        if sample not in seen:
            seen.add(sample)
            selected.append(row)
        row_mask ^= bit
    return selected


def result_from_masks(
    rule: str,
    positive_mask: int,
    negative_mask: int,
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    max_negative_samples: int,
    show_examples: int,
) -> RuleResult | None:
    positive_samples, _positive_exceeded = sample_count_for_mask(positive_mask, positive_sample_bits)
    if positive_samples <= 0:
        return None
    negative_samples, negative_exceeded = sample_count_for_mask(
        negative_mask, negative_sample_bits, max_negative_samples
    )
    if negative_exceeded:
        return None
    return RuleResult(
        rule=rule,
        positive_rows=positive_mask.bit_count(),
        positive_samples=positive_samples,
        negative_rows=negative_mask.bit_count(),
        negative_samples=negative_samples,
        positive_examples=selected_samples_from_mask(positive_rows, positive_mask, show_examples),
        negative_examples=selected_samples_from_mask(negative_rows, negative_mask, show_examples),
    )


def ranked_state_key(
    state: SearchState,
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    max_negative_samples: int,
) -> tuple[int, int, int, int, str]:
    negative_samples = bounded_sample_count(state.negative_mask, negative_sample_bits, max_negative_samples)
    positive_samples = bounded_sample_count(state.positive_mask, positive_sample_bits, None)
    return (
        negative_samples,
        -positive_samples,
        state.negative_mask.bit_count(),
        len(state.labels),
        " AND ".join(state.labels),
    )


def extend_condition_search(
    matches: list[PatternMatch],
    positive_rows: list[dict[str, str]],
    negative_rows: list[dict[str, str]],
    positive_sample_bits: list[int],
    negative_sample_bits: list[int],
    min_positive_samples: int,
    max_negative_samples: int,
    max_conditions: int,
    beam_width: int,
    show_examples: int,
) -> list[RuleResult]:
    if max_conditions < 2 or not matches:
        return []
    ordered = sorted(matches, key=lambda match: match.label)
    states: list[SearchState] = []
    for index, match in enumerate(ordered):
        if bounded_sample_count(match.positive_mask, positive_sample_bits, None) < min_positive_samples:
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
                if bounded_sample_count(positive_mask, positive_sample_bits, None) < min_positive_samples:
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
                    candidate, positive_sample_bits, negative_sample_bits, max_negative_samples
                ) < ranked_state_key(existing, positive_sample_bits, negative_sample_bits, max_negative_samples):
                    next_states[key] = candidate
        states = sorted(
            next_states.values(),
            key=lambda state: ranked_state_key(
                state, positive_sample_bits, negative_sample_bits, max_negative_samples
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
                positive_sample_bits,
                negative_sample_bits,
                max_negative_samples,
                show_examples,
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


def parse_route(route: str) -> tuple[str, str]:
    match = re.fullmatch(r"([a-z]+)->([a-z]+|ambiguous|none)", route)
    if not match:
        raise SystemExit(f"invalid route `{route}`; expected e.g. tom->snare")
    return match.group(1), match.group(2)


def top_routes(rows: list[dict[str, str]], limit: int) -> list[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        expected = row.get("expected", "")
        got = row.get("primary", "")
        if not expected or not got or expected == got:
            continue
        counts[(expected, got)] += 1
    return [route for route, _count in counts.most_common(max(1, limit))]


def format_example(row: dict[str, str]) -> str:
    expected = row.get("expected", "")
    got = row.get("primary", "")
    parts = [
        f"{row.get('sample', '')} {expected}->{got}",
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


def print_route_patterns(
    rows: list[dict[str, str]],
    route: tuple[str, str],
    limit: int,
    min_positive_samples: int,
    max_negative_samples: int,
    max_conditions: int,
    beam_width: int,
    show_examples: int,
) -> None:
    expected, got = route
    positive_rows = [
        row for row in rows if row.get("expected") == expected and row.get("primary") == got
    ]
    negative_rows = [row for row in rows if row.get("expected") == row.get("primary")]
    protected_by_expected = Counter(row.get("expected", "") for row in negative_rows)
    print(
        f"route {expected}->{got} positives={len({row.get('sample', '') for row in positive_rows})} "
        f"rows={len(positive_rows)} protected_correct={len({row.get('sample', '') for row in negative_rows})} "
        f"rows={len(negative_rows)}"
    )
    if not positive_rows:
        print("  --")
        return
    print(
        "  protected_by_expected="
        + " ".join(f"{key}={value}" for key, value in sorted(protected_by_expected.items()))
    )

    positive_sample_bits = sample_bit_map(positive_rows)
    negative_sample_bits = sample_bit_map(negative_rows)
    patterns = build_patterns(positive_rows)
    matches = [
        PatternMatch(
            label=pattern.label,
            positive_mask=mask_for_pattern(positive_rows, pattern),
            negative_mask=mask_for_pattern(negative_rows, pattern),
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
            negative_rows,
            positive_sample_bits,
            negative_sample_bits,
            max_negative_samples,
            show_examples,
        )
        if result is not None and result.positive_samples >= min_positive_samples:
            results.append(result)
    results.extend(
        extend_condition_search(
            matches,
            positive_rows,
            negative_rows,
            positive_sample_bits,
            negative_sample_bits,
            min_positive_samples,
            max_negative_samples,
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
    ranked = sorted(deduped.values(), key=rank_result)[:limit]
    if not ranked:
        print("  --")
        return
    for result in ranked:
        print(
            f"  +{result.positive_samples} rows={result.positive_rows} "
            f"-{result.negative_samples} rows={result.negative_rows} :: {result.rule}"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--route", action="append", default=[], help="route like tom->snare; repeatable")
    parser.add_argument("--top-routes", type=int, default=5)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-positive-samples", type=int, default=3)
    parser.add_argument("--max-negative-samples", type=int, default=0)
    parser.add_argument("--max-conditions", type=int, default=3)
    parser.add_argument("--beam-width", type=int, default=220)
    parser.add_argument("--show-examples", type=int, default=0)
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for path in args.logs:
        rows.extend(parse_rows(path))
    routes = [parse_route(route) for route in args.route] if args.route else top_routes(rows, args.top_routes)
    for route in routes:
        print_route_patterns(
            rows,
            route,
            max(1, args.limit),
            max(1, args.min_positive_samples),
            max(0, args.max_negative_samples),
            max(1, args.max_conditions),
            max(1, args.beam_width),
            max(0, args.show_examples),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
