#!/usr/bin/env python3
"""Aggregate analyzer_instrument_family_samples shard summaries."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


FAMILIES = ("guitar", "piano", "vocals", "other")
SUMMARY_RE = re.compile(
    r"^analyzer_instrument_family_samples: \d+ checks passed "
    r"\(usable (?P<usable>\d+), guitar (?P<guitar_hit>\d+)/(?P<guitar_total>\d+), "
    r"piano (?P<piano_hit>\d+)/(?P<piano_total>\d+), "
    r"vocals (?P<vocals_hit>\d+)/(?P<vocals_total>\d+), "
    r"other (?P<other_hit>\d+)/(?P<other_total>\d+); .+\)$"
)


def percent_floor(numerator: int, denominator: int) -> int:
    return numerator * 100 // denominator if denominator > 0 else 0


def fail(message: str) -> None:
    print(f"check_instrument_family_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_shard(path: pathlib.Path) -> dict[str, int]:
    summary: dict[str, int] | None = None
    for line in path.read_text(errors="replace").splitlines():
        match = SUMMARY_RE.match(line)
        if not match:
            continue
        summary = {"usable": int(match.group("usable"))}
        for family in FAMILIES:
            summary[f"{family}_hit"] = int(match.group(f"{family}_hit"))
            summary[f"{family}_total"] = int(match.group(f"{family}_total"))
    if summary is None:
        fail(f"{path}: missing analyzer_instrument_family_samples pass summary line")
    return summary


def add_summary(total: dict[str, int], part: dict[str, int]) -> None:
    for key, value in part.items():
        total[key] = total.get(key, 0) + value


def validate(args: argparse.Namespace, summary: dict[str, int]) -> None:
    usable = summary.get("usable", 0)
    if usable < args.min_samples:
        fail(f"expected at least {args.min_samples} usable samples, got {usable}")

    for family in FAMILIES:
        hits = summary.get(f"{family}_hit", 0)
        total = summary.get(f"{family}_total", 0)
        if total <= 0:
            continue
        recall = percent_floor(hits, total)
        if recall < args.min_recall_percent:
            fail(
                f"expected {family} recall >= {args.min_recall_percent}%, got "
                f"{recall}% ({hits}/{total})"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-samples", type=int, required=True)
    parser.add_argument("--min-recall-percent", type=int, required=True)
    args = parser.parse_args()

    totals: dict[str, int] = {}
    for path in args.logs:
        add_summary(totals, parse_shard(path))

    validate(args, totals)
    print(
        "check_instrument_family_shards: ok "
        f"(usable {totals['usable']}, "
        + ", ".join(
            f"{family} {totals.get(f'{family}_hit', 0)}/{totals.get(f'{family}_total', 0)}"
            for family in FAMILIES
        )
        + ")"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
