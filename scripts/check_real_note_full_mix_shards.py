#!/usr/bin/env python3
"""Aggregate analyzer_real_note_samples full-mix shards and validate ownership gates."""

from __future__ import annotations

import argparse
from collections import Counter
import pathlib
import re
import sys


FAMILIES = ("bass", "guitar", "piano", "vocals", "other")
ROWS = ("bass", "guitar", "piano", "vocals", "other", "amb", "none")
SUMMARY_RE = re.compile(r"^analyzer_real_note_samples full-mix: .*\((?P<body>.+)\)$")
ROW_CONFUSION_RE = re.compile(r"^analyzer_real_note_samples full-mix row-confusion: (?P<body>.+)$")
FAMILY_TOTAL_RE = re.compile(
    r"\b(?P<family>bass|guitar|piano|vocals|other)(?:=|\s+)(?P<hit>\d+)/(?P<total>\d+)"
)
DRUM_RE = re.compile(r"\b(?P<name>kick|snare|hihat|crash|tom|ride|rim)=(?P<count>\d+)")


def percent(hit: int, total: int) -> int:
    return hit * 100 // total if total > 0 else 0


def fail(message: str) -> None:
    print(f"check_real_note_full_mix_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_pair(body: str, name: str) -> tuple[int, int]:
    match = re.search(rf"\b{re.escape(name)}\s+(?P<hit>\d+)/(?P<total>\d+)", body)
    if not match:
        fail(f"missing `{name}` pair in shard summary: {body}")
    return int(match.group("hit")), int(match.group("total"))


def parse_family_pairs(section: str) -> dict[str, tuple[int, int]]:
    pairs: dict[str, tuple[int, int]] = {}
    for match in FAMILY_TOTAL_RE.finditer(section):
        pairs[match.group("family")] = (int(match.group("hit")), int(match.group("total")))
    return pairs


def empty_confusion() -> dict[str, dict[str, int]]:
    return {family: {row: 0 for row in ROWS} for family in FAMILIES}


def parse_confusion(body: str) -> dict[str, dict[str, int]]:
    confusion = empty_confusion()
    for family in FAMILIES:
        match = re.search(rf"{family}\[(?P<counts>[^\]]+)\]", body)
        if not match:
            fail(f"missing `{family}` row-confusion block: {body}")
        for token in match.group("counts").split(","):
            if "=" not in token:
                continue
            row, value = token.split("=", 1)
            if row in ROWS:
                confusion[family][row] += int(value)
    return confusion


def add_confusion(total: dict[str, dict[str, int]], part: dict[str, dict[str, int]]) -> None:
    for family in FAMILIES:
        for row in ROWS:
            total[family][row] += part[family][row]


def parse_shard(path: pathlib.Path) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    summary: dict[str, int] = {
        "usable": 0,
        "any_hit": 0,
        "any_total": 0,
        "expected_hit": 0,
        "expected_total": 0,
        "first_hit": 0,
        "first_total": 0,
        "drum_active": 0,
        "drum_windows": 0,
    }
    for family in FAMILIES:
        summary[f"{family}_hit"] = 0
        summary[f"{family}_total"] = 0
        summary[f"{family}_expected_hit"] = 0
        summary[f"{family}_expected_total"] = 0
        summary[f"{family}_first_hit"] = 0
        summary[f"{family}_first_total"] = 0
    for drum in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim"):
        summary[f"drum_{drum}"] = 0

    confusion = empty_confusion()
    saw_summary = False
    saw_confusion = False
    for line in path.read_text(errors="replace").splitlines():
        summary_match = SUMMARY_RE.match(line)
        if summary_match:
            saw_summary = True
            body = summary_match.group("body")
            usable_match = re.search(r"\busable\s+(?P<usable>\d+)", body)
            if not usable_match:
                fail(f"missing usable count in shard summary: {body}")
            summary["usable"] += int(usable_match.group("usable"))
            for name, prefix in (("any-row", "any"), ("expected-row", "expected"),
                                 ("first-row", "first"), ("drum-active-windows", "drum")):
                hit, total = parse_pair(body, name)
                if prefix == "drum":
                    summary["drum_active"] += hit
                    summary["drum_windows"] += total
                else:
                    summary[f"{prefix}_hit"] += hit
                    summary[f"{prefix}_total"] += total
            for family, hit, total in FAMILY_TOTAL_RE.findall(body.split(";", 1)[0]):
                summary[f"{family}_hit"] += int(hit)
                summary[f"{family}_total"] += int(total)
            for section_name, prefix in (("expected-row-by-family", "expected"),
                                         ("first-row-by-family", "first")):
                section_match = re.search(rf"{section_name}\s+(?P<section>[^,)]*)", body)
                if not section_match:
                    fail(f"missing `{section_name}` in shard summary: {body}")
                for family, (hit, total) in parse_family_pairs(section_match.group("section")).items():
                    summary[f"{family}_{prefix}_hit"] += hit
                    summary[f"{family}_{prefix}_total"] += total
            drums_match = re.search(r", drums (?P<section>[^)]*)", body)
            if drums_match:
                for drum, count in DRUM_RE.findall(drums_match.group("section")):
                    summary[f"drum_{drum}"] += int(count)
            continue

        confusion_match = ROW_CONFUSION_RE.match(line)
        if confusion_match:
            saw_confusion = True
            add_confusion(confusion, parse_confusion(confusion_match.group("body")))

    if not saw_summary:
        fail(f"missing analyzer_real_note_samples full-mix summary in {path}")
    if not saw_confusion:
        fail(f"missing analyzer_real_note_samples full-mix row-confusion in {path}")
    return summary, confusion


def add_summary(total: dict[str, int], part: dict[str, int]) -> None:
    for key, value in part.items():
        total[key] = total.get(key, 0) + value


def arg_threshold(args: argparse.Namespace, family: str, name: str) -> int:
    value = getattr(args, f"{family}_{name}")
    if value is not None:
        return value
    return getattr(args, name)


def validate(args: argparse.Namespace, summary: dict[str, int],
             confusion: dict[str, dict[str, int]]) -> None:
    checks = [
        ("any-row", summary["any_hit"], summary["any_total"], args.min_any_hit_percent),
        ("expected-row", summary["expected_hit"], summary["expected_total"],
         args.min_expected_row_percent),
        ("first-row", summary["first_hit"], summary["first_total"], args.min_first_row_percent),
    ]
    for name, hit, total, threshold in checks:
        value = percent(hit, total)
        if value < threshold:
            fail(f"expected full-mix {name} >= {threshold}%, got {value}% ({hit}/{total})")

    for family in FAMILIES:
        expected_threshold = arg_threshold(args, family, "min_expected_row_percent")
        first_threshold = arg_threshold(args, family, "min_first_row_percent")
        expected_hit = summary[f"{family}_expected_hit"]
        expected_total = summary[f"{family}_expected_total"]
        first_hit = summary[f"{family}_first_hit"]
        first_total = summary[f"{family}_first_total"]
        expected_value = percent(expected_hit, expected_total)
        first_value = percent(first_hit, first_total)
        if expected_value < expected_threshold:
            fail(
                f"expected full-mix {family} expected-row >= {expected_threshold}%, "
                f"got {expected_value}% ({expected_hit}/{expected_total})"
            )
        if first_value < first_threshold:
            fail(
                f"expected full-mix {family} first-row >= {first_threshold}%, "
                f"got {first_value}% ({first_hit}/{first_total})"
            )

    drum_percent = percent(summary["drum_active"], summary["drum_windows"])
    if drum_percent > args.max_drum_active_percent:
        fail(
            f"expected full-mix melodic drum-active windows <= {args.max_drum_active_percent}%, "
            f"got {drum_percent}% ({summary['drum_active']}/{summary['drum_windows']})"
        )

    print(
        "check_real_note_full_mix_shards: ok "
        f"(usable {summary['usable']}, any-row {summary['any_hit']}/{summary['any_total']}, "
        f"expected-row {summary['expected_hit']}/{summary['expected_total']}, "
        f"first-row {summary['first_hit']}/{summary['first_total']}, "
        f"drum-active-windows {summary['drum_active']}/{summary['drum_windows']})"
    )
    print(
        "check_real_note_full_mix_shards: expected-row-by-family "
        + " ".join(
            f"{family}={summary[f'{family}_expected_hit']}/{summary[f'{family}_expected_total']}"
            for family in FAMILIES
        )
    )
    print(
        "check_real_note_full_mix_shards: first-row-by-family "
        + " ".join(
            f"{family}={summary[f'{family}_first_hit']}/{summary[f'{family}_first_total']}"
            for family in FAMILIES
        )
    )
    print("check_real_note_full_mix_shards: row-confusion")
    for family in FAMILIES:
        print(
            f"  {family}["
            + ",".join(f"{row}={confusion[family][row]}" for row in ROWS)
            + "]"
        )
    row_confusion: Counter[str] = Counter()
    for family in FAMILIES:
        for row, value in confusion[family].items():
            if value <= 0 or row == family:
                continue
            row_confusion[f"{family}->{row}"] += value
    if row_confusion:
        print(
            "check_real_note_full_mix_shards: row-confusion routes "
            + " ".join(f"{route}={value}" for route, value in row_confusion.most_common(12))
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-any-hit-percent", type=int, default=99)
    parser.add_argument("--min-expected-row-percent", type=int, default=80)
    parser.add_argument("--min-first-row-percent", type=int, default=25)
    parser.add_argument("--max-drum-active-percent", type=int, default=25)
    for family in FAMILIES:
        parser.add_argument(f"--{family}-min-expected-row-percent", type=int)
        parser.add_argument(f"--{family}-min-first-row-percent", type=int)
    args = parser.parse_args()

    summary: dict[str, int] = {}
    confusion = empty_confusion()
    for path in args.logs:
        shard_summary, shard_confusion = parse_shard(path)
        add_summary(summary, shard_summary)
        add_confusion(confusion, shard_confusion)
    validate(args, summary, confusion)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
