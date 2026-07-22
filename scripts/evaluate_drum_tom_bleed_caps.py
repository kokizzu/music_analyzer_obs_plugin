#!/usr/bin/env python3
"""Evaluate candidate post-detection tom bleed caps from verbose drum rows."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import Counter
from collections.abc import Callable


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
DETAIL_RE = re.compile(
    r"(?P<cat>kick|snare|hihat|crash|tom|ride|rim) "
    r"band=(?P<band>[0-9.]+) "
    r"seg=(?P<seg>[0-9.]+) "
    r"shape_score=(?P<shape_score>[0-9.]+) "
    r"trigger=(?P<trigger>[0-9.]+)/(?P<threshold>[0-9.]+) "
    r"shape=(?P<shape>[01]) "
    r"level=(?P<level>[0-9.]+)"
)
ROW_RE = re.compile(r"debug 100ms (?P<sample>\S+) expected (?P<expected>\w+)")
BODY_RE = re.compile(
    r"energy=(?P<low>[0-9.]+)/(?P<mid>[0-9.]+)/(?P<high>[0-9.]+) "
    r"body=(?P<kick_body>[0-9.]+)/(?P<snare_body>[0-9.]+)/(?P<tom_body>[0-9.]+) "
    r"crack=(?P<snare_crack>[0-9.]+) upper_tom=(?P<upper_tom_body>[0-9.]+) "
    r"body_shape=(?P<body_shape>-?[0-9]+)"
)


def parse_rows(paths: list[pathlib.Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in paths:
        for line in path.read_text(errors="replace").splitlines():
            row_match = ROW_RE.search(line)
            body_match = BODY_RE.search(line)
            if not row_match or not body_match:
                continue
            metrics = {
                match.group("cat"): {
                    key: float(match.group(key))
                    for key in ("band", "seg", "shape_score", "trigger", "threshold", "shape", "level")
                }
                for match in DETAIL_RE.finditer(line)
            }
            if not metrics:
                continue
            body = {
                key: float(body_match.group(key))
                for key in (
                    "low",
                    "mid",
                    "high",
                    "kick_body",
                    "snare_body",
                    "tom_body",
                    "snare_crack",
                    "upper_tom_body",
                    "body_shape",
                )
            }
            rows.append(
                {
                    "sample": row_match.group("sample"),
                    "expected": row_match.group("expected"),
                    "metrics": metrics,
                    **body,
                }
            )
    return rows


def metric(row: dict[str, object], category: str, field: str) -> float:
    metrics = row["metrics"]
    assert isinstance(metrics, dict)
    values = metrics.get(category, {})
    assert isinstance(values, dict)
    return float(values.get(field, 0.0))


def value(row: dict[str, object], field: str) -> float:
    return float(row[field])


def primary(levels: dict[str, float]) -> str:
    best = "none"
    best_level = 0.0
    for category in CATEGORIES:
        level = levels.get(category, 0.0)
        if level <= 0.30 or level <= best_level:
            continue
        best = category
        best_level = level
    if best == "none":
        return best
    ties = sum(
        1
        for category in CATEGORIES
        if levels.get(category, 0.0) > 0.30 and abs(levels[category] - best_level) <= 0.005
    )
    return "ambiguous" if ties > 1 else best


def levels_for(row: dict[str, object]) -> dict[str, float]:
    return {category: metric(row, category, "level") for category in CATEGORIES}


def cap_tom(levels: dict[str, float], cap: float) -> bool:
    old = levels.get("tom", 0.0)
    levels["tom"] = min(old, cap)
    return levels["tom"] < old


def snare_crack_clear(row: dict[str, object]) -> bool:
    return (
        metric(row, "tom", "level") > 0.30
        and metric(row, "snare", "level") >= 0.70
        and value(row, "snare_body") > 1.0e-6
        and value(row, "snare_crack") >= value(row, "snare_body") * 0.18
        and value(row, "tom_body") <= value(row, "snare_body") * 1.70
    )


def kick_low_clear(row: dict[str, object]) -> bool:
    return (
        metric(row, "tom", "level") > 0.30
        and metric(row, "kick", "level") >= 0.70
        and value(row, "low") >= 0.50
        and value(row, "kick_body") >= value(row, "snare_body") * 0.70
        and value(row, "tom_body") <= value(row, "kick_body") * 1.70
    )


def snare_or_kick_clear(row: dict[str, object]) -> bool:
    return snare_crack_clear(row) or kick_low_clear(row)


RULES: dict[str, Callable[[dict[str, object]], bool]] = {
    "snare_crack_clear": snare_crack_clear,
    "kick_low_clear": kick_low_clear,
    "snare_or_kick_clear": snare_or_kick_clear,
}


def summarize(rows: list[dict[str, object]], rule_name: str, cap: float) -> str:
    rule = RULES[rule_name]
    by_expected: dict[str, Counter[str]] = {category: Counter() for category in ("kick", "snare", "tom")}
    changed = 0
    false_tom_before = 0
    false_tom_after = 0
    tom_hit_before = 0
    tom_hit_after = 0
    primary_before = 0
    primary_after = 0
    for row in rows:
        expected = str(row["expected"])
        if expected not in by_expected:
            continue
        base_levels = levels_for(row)
        levels = dict(base_levels)
        if rule(row):
            changed += int(cap_tom(levels, cap))
        base_primary = primary(base_levels)
        capped_primary = primary(levels)
        by_expected[expected][f"base_primary:{base_primary}"] += 1
        by_expected[expected][f"capped_primary:{capped_primary}"] += 1
        if base_primary == expected:
            primary_before += 1
        if capped_primary == expected:
            primary_after += 1
        if expected != "tom" and base_levels["tom"] > 0.30:
            false_tom_before += 1
        if expected != "tom" and levels["tom"] > 0.30:
            false_tom_after += 1
        if expected == "tom" and base_levels["tom"] > 0.30:
            tom_hit_before += 1
        if expected == "tom" and levels["tom"] > 0.30:
            tom_hit_after += 1
    parts = [
        f"rule={rule_name}",
        f"cap={cap:.2f}",
        f"changed={changed}",
        f"false_tom={false_tom_before}->{false_tom_after}",
        f"tom_hit={tom_hit_before}->{tom_hit_after}",
        f"primary={primary_before}->{primary_after}",
    ]
    for expected, counts in by_expected.items():
        parts.append(
            f"{expected}_primary={counts[f'base_primary:{expected}']}->"
            f"{counts[f'capped_primary:{expected}']}"
        )
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--cap", type=float, default=0.28)
    parser.add_argument("--rule", choices=tuple(RULES), action="append", default=[])
    args = parser.parse_args()

    rows = parse_rows(args.logs)
    print(f"rows={len(rows)}")
    rule_names = args.rule or list(RULES)
    for rule_name in rule_names:
        print(summarize(rows, rule_name, args.cap))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
