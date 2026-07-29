#!/usr/bin/env python3
"""Simulate drum active thresholds from analyzer_drum_samples attribute rows."""

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


@dataclass(frozen=True)
class Condition:
    field: str
    op: str
    value: str

    def matches(self, row: dict[str, str]) -> bool:
        actual = row.get(self.field, "")
        if self.op == "=":
            return actual == self.value
        if self.op == "!=":
            return actual != self.value

        actual_value = as_float(actual)
        expected_value = as_float(self.value)
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
}


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
            "comparators: .eq. .ne. .gt. .gte. .lt. .lte."
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
