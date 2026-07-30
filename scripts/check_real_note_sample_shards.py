#!/usr/bin/env python3
"""Aggregate analyzer_real_note_samples shards and validate isolated sample gates."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


FAMILIES = ("bass", "guitar", "piano", "vocals", "other")
SUMMARY_RE = re.compile(r"^analyzer_real_note_samples: (?P<head>.+) \((?P<body>.+)\)$")
PASSED_RE = re.compile(r"^(?P<checks>\d+) checks passed$")
TOLERATED_RE = re.compile(r"^(?P<failures>\d+) tolerated failures within limit (?P<limit>\d+)$")
FAMILY_TOTAL_RE = re.compile(
    r"\b(?P<family>bass|guitar|piano|vocals|other)(?:=|\s+)(?P<hit>\d+)/(?P<total>\d+)"
)


def fail(message: str) -> None:
    print(f"check_real_note_sample_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_shard(path: pathlib.Path) -> dict[str, int]:
    summary: dict[str, int] = {"usable": 0, "failures": 0}
    for family in FAMILIES:
        summary[f"{family}_hit"] = 0
        summary[f"{family}_total"] = 0

    saw_summary = False
    for line in path.read_text(errors="replace").splitlines():
        summary_match = SUMMARY_RE.match(line)
        if not summary_match:
            continue
        head = summary_match.group("head")
        passed_match = PASSED_RE.match(head)
        tolerated_match = TOLERATED_RE.match(head)
        if passed_match:
            failures = 0
        elif tolerated_match:
            failures = int(tolerated_match.group("failures"))
        else:
            continue

        saw_summary = True
        body = summary_match.group("body")
        usable_match = re.search(r"\busable\s+(?P<usable>\d+)", body)
        if not usable_match:
            fail(f"missing usable count in shard summary: {body}")
        summary["usable"] += int(usable_match.group("usable"))
        summary["failures"] += failures
        for family, hit, total in FAMILY_TOTAL_RE.findall(body):
            summary[f"{family}_hit"] += int(hit)
            summary[f"{family}_total"] += int(total)

    if not saw_summary:
        fail(f"missing analyzer_real_note_samples summary in {path}")
    return summary


def add_summary(total: dict[str, int], part: dict[str, int]) -> None:
    for key, value in part.items():
        total[key] = total.get(key, 0) + value


def hit_percent(hit: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return (100.0 * float(hit)) / float(total)


def format_percent(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def validate(args: argparse.Namespace, summary: dict[str, int]) -> None:
    if summary["failures"] > args.max_failures:
        fail(
            f"expected isolated real-note failures <= {args.max_failures}, "
            f"got {summary['failures']}"
        )
    for family in FAMILIES:
        threshold = getattr(args, f"min_{family}")
        total = summary[f"{family}_total"]
        if total < threshold:
            fail(
                f"expected at least {threshold} {family} real note samples, "
                f"got {total}"
            )
        percent_threshold = getattr(args, f"min_{family}_hit_percent")
        percent = hit_percent(summary[f"{family}_hit"], total)
        if percent < percent_threshold:
            fail(
                f"expected {family} real-note hit rate >= "
                f"{format_percent(percent_threshold)}%, got {format_percent(percent)}% "
                f"({summary[f'{family}_hit']}/{total})"
            )

    print(
        "check_real_note_sample_shards: ok "
        f"(usable {summary['usable']}, failures {summary['failures']}/{args.max_failures}, "
        + ", ".join(
            f"{family} {summary[f'{family}_hit']}/{summary[f'{family}_total']}"
            for family in FAMILIES
        )
        + ")"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--max-failures", type=int, default=0)
    for family in FAMILIES:
        parser.add_argument(f"--min-{family}", type=int, default=0)
        parser.add_argument(f"--min-{family}-hit-percent", type=float, default=0.0)
    args = parser.parse_args()

    summary: dict[str, int] = {}
    for path in args.logs:
        add_summary(summary, parse_shard(path))
    validate(args, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
