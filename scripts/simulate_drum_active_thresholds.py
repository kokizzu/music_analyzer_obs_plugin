#!/usr/bin/env python3
"""Simulate drum active thresholds and primary recovery rules from drum rows."""

from __future__ import annotations

import argparse
import csv
import pathlib
import statistics
from collections import Counter
from dataclasses import dataclass


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
DEFAULT_THRESHOLDS = (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90)
DEFAULT_PROFILE_FIELDS = (
    "energy_low",
    "energy_mid",
    "energy_high",
    "kick_body",
    "snare_body",
    "tom_body",
    "body_shape",
    "kick_level",
    "snare_level",
    "tom_level",
    "kick_seg",
    "snare_seg",
    "tom_seg",
)
COMPARATORS = (">=", "<=", "!=", ">", "<", "=")
WORD_COMPARATORS = (
    (".gte.", ">="),
    (".lte.", "<="),
    (".ne.", "!="),
    (".gt.", ">"),
    (".lt.", "<"),
    (".eq.", "="),
)
FIELD_COMPARATORS = (
    (".gtef.", ">="),
    (".ltef.", "<="),
    (".gtf.", ">"),
    (".ltf.", "<"),
)


@dataclass(frozen=True)
class Condition:
    field: str
    op: str
    value: str
    compare_field: str = ""
    compare_multiplier: float = 1.0

    def matches(self, row: dict[str, str]) -> bool:
        actual = row.get(self.field, "")
        if self.op == "=":
            return actual == self.value
        if self.op == "!=":
            return actual != self.value

        actual_value = optional_float(actual)
        if actual_value is None:
            return False
        expected_value = (
            optional_float(row.get(self.compare_field, ""))
            if self.compare_field
            else optional_float(self.value)
        )
        if expected_value is None:
            return False
        if self.compare_field:
            expected_value *= self.compare_multiplier
        if self.op == ">=":
            return actual_value >= expected_value
        if self.op == "<=":
            return actual_value <= expected_value
        if self.op == ">":
            return actual_value > expected_value
        if self.op == "<":
            return actual_value < expected_value
        raise ValueError(f"unsupported comparator: {self.op}")

    def text(self) -> str:
        if self.compare_field:
            return f"{self.field}{self.op}{self.compare_field}*{self.compare_multiplier:g}"
        return f"{self.field}{self.op}{self.value}"


@dataclass(frozen=True)
class CandidateCap:
    name: str
    target: str
    cap: float
    conditions: tuple[Condition, ...]
    description: str = ""

    def matches(self, row: dict[str, str]) -> bool:
        return all(condition.matches(row) for condition in self.conditions)

    def predicate_text(self) -> str:
        return ",".join(condition.text() for condition in self.conditions)


@dataclass(frozen=True)
class CandidatePromote:
    name: str
    target: str
    minimum_level: float
    conditions: tuple[Condition, ...]
    competitor_gap: float = 0.02
    description: str = ""

    def matches(self, row: dict[str, str]) -> bool:
        return all(condition.matches(row) for condition in self.conditions)

    def predicate_text(self) -> str:
        return ",".join(condition.text() for condition in self.conditions)


BUILTIN_CAPS = {
    "low-kick-primary-tom": CandidateCap(
        name="low-kick-primary-tom",
        target="tom",
        cap=0.28,
        conditions=(
            Condition("got", "=", "kick"),
            Condition("kick_level", ">=", "0.95"),
            Condition("tom_level", ">", "0.30"),
            Condition("energy_low", ">=", "0.58"),
        ),
        description="probe low-heavy kick-primary rows before suppressing tom bleed",
    ),
    "level-primary-saturated-kick-tom": CandidateCap(
        name="level-primary-saturated-kick-tom",
        target="tom",
        cap=0.28,
        conditions=(
            Condition("level_primary", "=", "kick"),
            Condition("kick_level", ">=", "0.995"),
            Condition("tom_level", ">", "0.30"),
        ),
        description="probe runtime-style saturated kick-primary tom bleed suppression",
    ),
}

BUILTIN_PROMOTES = {
    "tom-primary-from-close-snare": CandidatePromote(
        name="tom-primary-from-close-snare",
        target="tom",
        minimum_level=0.90,
        conditions=(
            Condition("body_shape", "=", "4.000000"),
            Condition("tom_level", ">", "0.30"),
            Condition("snare_level", ">", "0.30"),
            Condition("tom_body", ">=", "snare_body", compare_field="snare_body", compare_multiplier=1.25),
            Condition("upper_tom_body", ">=", "snare_crack", compare_field="snare_crack", compare_multiplier=6.0),
        ),
        description="probe tom-body rows where snare wins by level but tom has stronger shell evidence",
    ),
}


def as_float(value: str) -> float:
    parsed = optional_float(value)
    return parsed if parsed is not None else 0.0


def optional_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        add_level_primary(row)
        add_ratios(row)
    return rows


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
            lhs_value = optional_float(row.get(f"{lhs}_{field}", ""))
            rhs_value = optional_float(row.get(f"{rhs}_{field}", ""))
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
        lhs_value = optional_float(row.get(lhs_field, ""))
        rhs_value = optional_float(row.get(rhs_field, ""))
        if lhs_value is None or rhs_value is None or abs(rhs_value) < 1.0e-6:
            continue
        row[label] = f"{lhs_value / rhs_value:.9f}"


def add_level_primary(row: dict[str, str]) -> None:
    primary = "none"
    primary_level = 0.0
    for category in CATEGORIES:
        level = as_float(row.get(f"{category}_level", ""))
        if level <= 0.30 or level <= primary_level:
            continue
        primary = category
        primary_level = level
    if primary == "none":
        row["level_primary"] = primary
        row["level_primary_level"] = "0"
        return
    tied = sum(
        1
        for category in CATEGORIES
        if as_float(row.get(f"{category}_level", "")) > 0.30
        and abs(as_float(row.get(f"{category}_level", "")) - primary_level) <= 0.005
    )
    row["level_primary"] = "ambiguous" if tied > 1 else primary
    row["level_primary_level"] = f"{primary_level:.9f}"


def levels_from_row(row: dict[str, str]) -> dict[str, float]:
    return {
        category: as_float(row.get(f"{category}_level", ""))
        for category in CATEGORIES
    }


def primary_from_level_map(row: dict[str, str], levels: dict[str, float]) -> str:
    primary = "none"
    primary_level = 0.0
    for category in CATEGORIES:
        level = levels.get(category, 0.0)
        if level <= 0.30 or level <= primary_level:
            continue
        primary = category
        primary_level = level
    if primary == "none":
        return primary

    expected = row.get("expected", "")
    if (
        row.get("merged_expected") == "1"
        and expected in CATEGORIES
        and levels.get(expected, 0.0) > 0.30
        and levels.get(expected, 0.0) >= 0.90
        and levels.get(expected, 0.0) + 0.025 >= primary_level
    ):
        return expected

    tied = sum(
        1
        for category in CATEGORIES
        if levels.get(category, 0.0) > 0.30
        and abs(levels.get(category, 0.0) - primary_level) <= 0.005
    )
    return "ambiguous" if tied > 1 else primary


def before_primary(row: dict[str, str]) -> str:
    return primary_from_level_map(row, levels_from_row(row))


def apply_promote(
    levels: dict[str, float],
    candidate: CandidatePromote,
) -> dict[str, float]:
    promoted = dict(levels)
    target = candidate.target
    strongest_competing_level = max(
        (level for category, level in promoted.items() if category != target),
        default=0.0,
    )
    target_level = max(
        promoted.get(target, 0.0),
        candidate.minimum_level,
        strongest_competing_level + candidate.competitor_gap,
    )
    promoted[target] = min(max(target_level, 0.0), 1.0)
    for category in CATEGORIES:
        if category == target or promoted[category] <= 0.30:
            continue
        promoted[category] = min(
            promoted[category],
            max(0.31, promoted[target] - candidate.competitor_gap),
        )
    return promoted


def apply_promotes(
    row: dict[str, str],
    candidates: list[CandidatePromote],
) -> tuple[dict[str, float], list[CandidatePromote]]:
    levels = levels_from_row(row)
    matched: list[CandidatePromote] = []
    for candidate in candidates:
        if not candidate.matches(row):
            continue
        levels = apply_promote(levels, candidate)
        matched.append(candidate)
    return levels, matched


def percent(hit: int, total: int) -> float:
    return 100.0 * hit / total if total else 0.0


def level_for(
    row: dict[str, str],
    category: str,
    candidate: CandidateCap | None = None,
) -> float:
    level = as_float(row.get(f"{category}_level", ""))
    if candidate and category == candidate.target and candidate.matches(row):
        return min(level, candidate.cap)
    return level


def active_stats(
    rows: list[dict[str, str]],
    category: str,
    threshold: float,
    candidate: CandidateCap | None = None,
) -> tuple[int, int, int, int]:
    total = sum(1 for row in rows if row.get("expected") == category)
    hit = sum(
        1
        for row in rows
        if row.get("expected") == category
        and level_for(row, category, candidate) > threshold
    )
    active = sum(1 for row in rows if level_for(row, category, candidate) > threshold)
    false = sum(
        1
        for row in rows
        if row.get("expected") != category
        and level_for(row, category, candidate) > threshold
    )
    return total, hit, active, false


def print_threshold(rows: list[dict[str, str]], threshold: float) -> None:
    print(f"threshold {threshold:.2f}")
    for category in CATEGORIES:
        total, hit, active, false = active_stats(rows, category, threshold)
        print(
            f"  {category}: recall={hit}/{total} {percent(hit, total):.2f}% "
            f"precision={hit}/{active} {percent(hit, active):.2f}% false={false}"
        )


def parse_thresholds(values: list[str]) -> list[float]:
    if not values:
        return list(DEFAULT_THRESHOLDS)
    thresholds: list[float] = []
    for value in values:
        for part in value.split(","):
            part = part.strip()
            if part:
                thresholds.append(float(part))
    return thresholds


def compact_counter(counter: Counter[str], limit: int = 5) -> str:
    if not counter:
        return "--"
    return " ".join(f"{name}={count}" for name, count in counter.most_common(limit))


def median_text(rows: list[dict[str, str]], field: str) -> str:
    values = [as_float(row.get(field, "")) for row in rows if row.get(field, "") != ""]
    if not values:
        return "--"
    return f"{statistics.median(values):.3f}"


def profile_text(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "--"
    return " ".join(f"{field}={median_text(rows, field)}" for field in fields)


def parse_condition(text: str) -> Condition:
    for token, op in FIELD_COMPARATORS:
        if token in text:
            field, value = text.split(token, 1)
            field = field.strip()
            value = value.strip()
            if not field or not value:
                raise ValueError(f"invalid candidate condition: {text}")
            compare_field, multiplier_text = (
                value.split("@", 1) if "@" in value else (value, "1.0")
            )
            compare_field = compare_field.strip()
            multiplier_text = multiplier_text.strip()
            if not compare_field or not multiplier_text:
                raise ValueError(f"invalid candidate condition: {text}")
            return Condition(
                field,
                op,
                value,
                compare_field=compare_field,
                compare_multiplier=float(multiplier_text),
            )

    for token, op in WORD_COMPARATORS:
        if token in text:
            field, value = text.split(token, 1)
            field = field.strip()
            value = value.strip()
            if not field or not value:
                raise ValueError(f"invalid candidate condition: {text}")
            return Condition(field, op, value)

    for op in COMPARATORS:
        if op in text:
            field, value = text.split(op, 1)
            field = field.strip()
            value = value.strip()
            if not field or not value:
                raise ValueError(f"invalid candidate condition: {text}")
            return Condition(field, op, value)
    raise ValueError(f"invalid candidate condition: {text}")


def parse_candidate_cap(value: str) -> CandidateCap:
    if value in BUILTIN_CAPS:
        return BUILTIN_CAPS[value]

    parts = value.split(":", 3)
    if len(parts) != 4:
        names = ", ".join(sorted(BUILTIN_CAPS))
        raise ValueError(
            "candidate cap must be a built-in name or "
            f"`name:target:cap:field=value,...`; built-ins: {names}"
        )

    name, target, cap_text, condition_text = (part.strip() for part in parts)
    if target not in CATEGORIES:
        raise ValueError(f"unknown candidate target: {target}")
    conditions = tuple(
        parse_condition(part.strip())
        for part in condition_text.split(",")
        if part.strip()
    )
    if not name or not conditions:
        raise ValueError(f"invalid candidate cap: {value}")
    return CandidateCap(name=name, target=target, cap=float(cap_text), conditions=conditions)


def parse_candidate_caps(values: list[str]) -> list[CandidateCap]:
    return [parse_candidate_cap(value) for value in values]


def parse_candidate_promote(value: str) -> CandidatePromote:
    if value in BUILTIN_PROMOTES:
        return BUILTIN_PROMOTES[value]

    parts = value.split(":", 3)
    if len(parts) != 4:
        names = ", ".join(sorted(BUILTIN_PROMOTES))
        raise ValueError(
            "candidate promote must be a built-in name or "
            f"`name:target:minimum_level:field=value,...`; built-ins: {names}"
        )

    name, target, minimum_level_text, condition_text = (part.strip() for part in parts)
    if target not in CATEGORIES:
        raise ValueError(f"unknown candidate target: {target}")
    conditions = tuple(
        parse_condition(part.strip())
        for part in condition_text.split(",")
        if part.strip()
    )
    if not name or not conditions:
        raise ValueError(f"invalid candidate promote: {value}")
    return CandidatePromote(
        name=name,
        target=target,
        minimum_level=float(minimum_level_text),
        conditions=conditions,
    )


def parse_candidate_promotes(values: list[str]) -> list[CandidatePromote]:
    return [parse_candidate_promote(value) for value in values]


def print_candidate(
    rows: list[dict[str, str]],
    threshold: float,
    candidate: CandidateCap,
    profile_fields: tuple[str, ...],
) -> None:
    matched = [row for row in rows if candidate.matches(row)]
    target = candidate.target
    before_total, before_hit, before_active, before_false = active_stats(rows, target, threshold)
    after_total, after_hit, after_active, after_false = active_stats(
        rows,
        target,
        threshold,
        candidate,
    )
    removed_false = [
        row
        for row in rows
        if row.get("expected") != target
        and level_for(row, target) > threshold
        and level_for(row, target, candidate) <= threshold
    ]
    lost_true = [
        row
        for row in rows
        if row.get("expected") == target
        and level_for(row, target) > threshold
        and level_for(row, target, candidate) <= threshold
    ]
    removed_routes = Counter(f"{row.get('expected', '--')}->{target}" for row in removed_false)

    print(
        f"candidate {candidate.name} threshold {threshold:.2f} "
        f"target={target} cap={candidate.cap:.2f} matched={len(matched)}"
    )
    print(f"  predicate: {candidate.predicate_text()}")
    if candidate.description:
        print(f"  description: {candidate.description}")
    print(
        f"  matched expected={compact_counter(Counter(row.get('expected', '') for row in matched))} "
        f"got={compact_counter(Counter(row.get('got', '') for row in matched))}"
    )
    print(
        f"  before {target}: recall={before_hit}/{before_total} "
        f"{percent(before_hit, before_total):.2f}% precision={before_hit}/{before_active} "
        f"{percent(before_hit, before_active):.2f}% false={before_false}"
    )
    print(
        f"  after {target}: recall={after_hit}/{after_total} "
        f"{percent(after_hit, after_total):.2f}% precision={after_hit}/{after_active} "
        f"{percent(after_hit, after_active):.2f}% false={after_false}"
    )
    print(
        f"  false-active removed={len(removed_false)} "
        f"routes={compact_counter(removed_routes)} true-active lost={len(lost_true)}"
    )
    if profile_fields:
        print(f"  removed medians: {profile_text(removed_false, profile_fields)}")
        print(f"  lost medians: {profile_text(lost_true, profile_fields)}")
    for row in removed_false[:3]:
        print(
            f"    removed sample={row.get('sample', '--')} expected={row.get('expected', '--')} "
            f"got={row.get('got', '--')} {target}_level="
            f"{level_for(row, target):.3f}->{level_for(row, target, candidate):.3f}"
        )
    for row in lost_true[:3]:
        print(
            f"    lost sample={row.get('sample', '--')} expected={row.get('expected', '--')} "
            f"got={row.get('got', '--')} {target}_level="
            f"{level_for(row, target):.3f}->{level_for(row, target, candidate):.3f}"
        )


def primary_summary(rows: list[dict[str, str]], after: dict[int, str] | None = None) -> tuple[int, int]:
    total = 0
    hits = 0
    for index, row in enumerate(rows):
        expected = row.get("expected", "")
        if expected not in CATEGORIES:
            continue
        total += 1
        got = after[index] if after is not None else before_primary(row)
        if got == expected:
            hits += 1
    return hits, total


def print_primary_promote_candidate(
    rows: list[dict[str, str]],
    candidate: CandidatePromote,
    profile_fields: tuple[str, ...],
) -> None:
    after: dict[int, str] = {}
    matched: list[dict[str, str]] = []
    fixed: list[dict[str, str]] = []
    regressed: list[dict[str, str]] = []
    changed: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        levels = levels_from_row(row)
        if candidate.matches(row):
            matched.append(row)
            levels = apply_promote(levels, candidate)
        before = before_primary(row)
        now = primary_from_level_map(row, levels)
        after[index] = now
        expected = row.get("expected", "")
        if now != before:
            changed.append(row)
        if before != expected and now == expected:
            fixed.append(row)
        if before == expected and now != expected:
            regressed.append(row)

    before_hits, total = primary_summary(rows)
    after_hits, _ = primary_summary(rows, after)
    fixed_routes = Counter(f"{row.get('expected', '--')}->{before_primary(row)}" for row in fixed)
    regressed_routes = Counter(
        f"{row.get('expected', '--')}->{primary_from_level_map(row, apply_promote(levels_from_row(row), candidate))}"
        for row in regressed
    )
    changed_routes = Counter(
        f"{before_primary(row)}->{primary_from_level_map(row, apply_promote(levels_from_row(row), candidate))}"
        for row in changed
    )

    print(
        f"candidate-promote {candidate.name} target={candidate.target} "
        f"minimum={candidate.minimum_level:.2f} matched={len(matched)}"
    )
    print(f"  predicate: {candidate.predicate_text()}")
    if candidate.description:
        print(f"  description: {candidate.description}")
    print(
        f"  matched expected={compact_counter(Counter(row.get('expected', '') for row in matched))} "
        f"got={compact_counter(Counter(before_primary(row) for row in matched))}"
    )
    print(
        f"  primary before={before_hits}/{total} {percent(before_hits, total):.2f}% "
        f"after={after_hits}/{total} {percent(after_hits, total):.2f}% "
        f"delta={after_hits - before_hits:+d}"
    )
    print(
        f"  fixed={len(fixed)} routes={compact_counter(fixed_routes)} "
        f"regressed={len(regressed)} routes={compact_counter(regressed_routes)} "
        f"changed={len(changed)} routes={compact_counter(changed_routes)}"
    )
    if profile_fields:
        print(f"  fixed medians: {profile_text(fixed, profile_fields)}")
        print(f"  regressed medians: {profile_text(regressed, profile_fields)}")
    for row in fixed[:3]:
        levels = apply_promote(levels_from_row(row), candidate)
        print(
            f"    fixed sample={row.get('sample', '--')} expected={row.get('expected', '--')} "
            f"got={before_primary(row)}->{primary_from_level_map(row, levels)}"
        )
    for row in regressed[:3]:
        levels = apply_promote(levels_from_row(row), candidate)
        print(
            f"    regressed sample={row.get('sample', '--')} expected={row.get('expected', '--')} "
            f"got={before_primary(row)}->{primary_from_level_map(row, levels)}"
        )


def print_primary_promote_combined(
    rows: list[dict[str, str]],
    candidates: list[CandidatePromote],
) -> None:
    if not candidates:
        return
    after: dict[int, str] = {}
    matched_names: Counter[str] = Counter()
    fixed = 0
    regressed = 0
    changed = 0
    fixed_routes: Counter[str] = Counter()
    regressed_routes: Counter[str] = Counter()
    for index, row in enumerate(rows):
        levels, matched = apply_promotes(row, candidates)
        for candidate in matched:
            matched_names[candidate.name] += 1
        before = before_primary(row)
        now = primary_from_level_map(row, levels)
        after[index] = now
        expected = row.get("expected", "")
        if now != before:
            changed += 1
        if before != expected and now == expected:
            fixed += 1
            fixed_routes[f"{expected}->{before}"] += 1
        if before == expected and now != expected:
            regressed += 1
            regressed_routes[f"{expected}->{now}"] += 1
    before_hits, total = primary_summary(rows)
    after_hits, _ = primary_summary(rows, after)
    print(
        "candidate-promote combined "
        f"rules={len(candidates)} matched={sum(matched_names.values())} "
        f"primary before={before_hits}/{total} {percent(before_hits, total):.2f}% "
        f"after={after_hits}/{total} {percent(after_hits, total):.2f}% "
        f"delta={after_hits - before_hits:+d}"
    )
    print(
        f"  matched={compact_counter(matched_names, len(candidates))} "
        f"fixed={fixed} routes={compact_counter(fixed_routes)} "
        f"regressed={regressed} routes={compact_counter(regressed_routes)} changed={changed}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", type=pathlib.Path)
    parser.add_argument(
        "--threshold",
        action="append",
        default=[],
        help="threshold value or comma-separated values; defaults to 0.30..0.90",
    )
    parser.add_argument(
        "--candidate-cap",
        action="append",
        default=[],
        help=(
            "simulate a candidate active cap. Use a built-in name such as "
            "`low-kick-primary-tom`, or custom `name:target:cap:field.eq.value,...`; "
            "comparators: .eq. .ne. .gt. .gte. .lt. .lte.; "
            "field comparators: .gtf. .gtef. .ltf. .ltef. with `other_field@multiplier`."
        ),
    )
    parser.add_argument(
        "--candidate-promote",
        action="append",
        default=[],
        help=(
            "simulate a candidate primary promotion. Use a built-in name, or custom "
            "`name:target:minimum_level:field.eq.value,...`; comparators match --candidate-cap."
        ),
    )
    parser.add_argument(
        "--profile-fields",
        default=",".join(DEFAULT_PROFILE_FIELDS),
        help="comma-separated candidate median fields to print; use `none` to disable",
    )
    args = parser.parse_args()

    rows = read_rows(args.rows)
    candidates = parse_candidate_caps(args.candidate_cap)
    promote_candidates = parse_candidate_promotes(args.candidate_promote)
    profile_fields = tuple(
        field.strip()
        for field in args.profile_fields.split(",")
        if field.strip() and field.strip().lower() != "none"
    )
    print(f"drum active threshold simulation: rows={len(rows)} source={args.rows}")
    for threshold in parse_thresholds(args.threshold):
        print_threshold(rows, threshold)
        for candidate in candidates:
            print_candidate(rows, threshold, candidate, profile_fields)
    for candidate in promote_candidates:
        print_primary_promote_candidate(rows, candidate, profile_fields)
    print_primary_promote_combined(rows, promote_candidates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
