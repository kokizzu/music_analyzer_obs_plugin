#!/usr/bin/env python3
"""Inspect coverage-blocked detector route candidates against cached TSV rows."""

from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import pathlib
import re
from statistics import median

from inspect_real_note_candidate_rows import (
    Condition,
    matches_condition,
    normalize_row,
    parse_rule,
    sample_key,
    summarize_numeric,
)


COVERAGE_NEED_RE = re.compile(
    r"^\s+coverage_need (?P<kind>\S+) (?P<section>.+?) "
    r"observed_samples=(?P<observed>\d+) need_samples=(?P<needed>\d+) "
    r"\+rows=(?P<rows>\d+) side_rows=(?P<side_rows>\d+) "
    r"net_rows=(?P<net_rows>-?\d+) gain_per_side=(?P<gain>\S+) :: (?P<rule>.+)$"
)

DEFAULT_FIELDS = [
    "expected_row_score",
    "first_row_score",
    "visual_first_row_score",
    "expected_first_score_ratio",
    "expected_visual_first_score_ratio",
    "first_expected_score_margin",
    "visual_first_expected_score_margin",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "raw_tuned_abs_cent_offset",
]

DEFAULT_EXAMPLE_FIELDS = [
    "sample_id",
    "recording_id",
    "status",
    "family",
    "source",
    "expected_note",
    "expected_label",
    "expected_chords",
    "debug_note",
    "first_row",
    "visual_first_row",
    "debug_owner",
    "owner_status",
    "miss_reason",
    "quality",
    "guitar_match_kind",
    "support",
    "guitar_chord",
]


@dataclasses.dataclass(frozen=True)
class CoverageNeed:
    kind: str
    section: str
    observed_samples: int
    needed_samples: int
    rows: int
    side_rows: int
    net_rows: int
    gain_per_side: str
    rule: str
    conditions: tuple[Condition, ...]


def parse_summary(path: pathlib.Path) -> list[CoverageNeed]:
    candidates: list[CoverageNeed] = []
    for line in path.read_text(errors="replace").splitlines():
        match = COVERAGE_NEED_RE.match(line)
        if not match:
            continue
        candidates.append(
            CoverageNeed(
                kind=match.group("kind"),
                section=match.group("section"),
                observed_samples=int(match.group("observed")),
                needed_samples=int(match.group("needed")),
                rows=int(match.group("rows")),
                side_rows=int(match.group("side_rows")),
                net_rows=int(match.group("net_rows")),
                gain_per_side=match.group("gain"),
                rule=match.group("rule"),
                conditions=tuple(parse_rule(match.group("rule"))),
            )
        )
    return candidates


def rule_fields(conditions: tuple[Condition, ...]) -> list[str]:
    fields: list[str] = []
    for field, _op_name, _expected in conditions:
        for part in field.split("/", 1):
            if part and part not in fields:
                fields.append(part)
    return fields


def row_matches(row: dict[str, str], conditions: tuple[Condition, ...]) -> bool:
    return all(matches_condition(row, condition) for condition in conditions)


def guitar_bucket_matches(row: dict[str, str], section: str) -> bool:
    if not section.startswith("bucket "):
        return True
    parts = section.removeprefix("bucket ").split(":", 2)
    if len(parts) != 3:
        return True
    expected_status, expected_quality, expected_support = parts
    if expected_status != "any" and row.get("status", "") != expected_status:
        return False
    if expected_quality != "any" and row.get("quality", "") != expected_quality:
        return False
    if expected_support != "any" and row.get("support", "") != expected_support:
        return False
    return True


def candidate_matches_row(row: dict[str, str], candidate: CoverageNeed) -> bool:
    if candidate.kind == "guitar" and not guitar_bucket_matches(row, candidate.section):
        return False
    return row_matches(row, candidate.conditions)


def read_matching_rows(
    paths: list[pathlib.Path], candidates: list[CoverageNeed]
) -> dict[CoverageNeed, list[dict[str, str]]]:
    matches: dict[CoverageNeed, list[dict[str, str]]] = {
        candidate: [] for candidate in candidates
    }
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="", errors="replace") as handle:
            for raw_row in csv.DictReader(handle, delimiter="\t"):
                row = normalize_row(
                    {
                        key: value
                        for key, value in raw_row.items()
                        if key and value is not None
                    }
                )
                row["_coverage_path"] = str(path)
                for candidate in candidates:
                    if candidate_matches_row(row, candidate):
                        matches[candidate].append(row)
    return matches


def grouped_counts(
    rows: list[dict[str, str]], fields: list[str]
) -> collections.Counter[tuple[str, ...]]:
    counts: collections.Counter[tuple[str, ...]] = collections.Counter()
    for row in rows:
        counts[tuple(row.get(field, "") for field in fields)] += 1
    return counts


def coverage_sample_key(row: dict[str, str]) -> str:
    return (
        sample_key(row)
        or row.get("recording_id", "")
        or row.get("audio_path", "")
        or row.get("path", "")
    )


def selected_samples(rows: list[dict[str, str]]) -> set[str]:
    return {key for key in (coverage_sample_key(row) for row in rows) if key}


def default_group_fields(rows: list[dict[str, str]]) -> list[str]:
    if any(
        row.get("guitar_match_kind") or row.get("support") or row.get("quality")
        for row in rows
    ):
        return ["_coverage_path", "status", "quality", "guitar_match_kind", "support"]
    return [
        "_coverage_path",
        "status",
        "family",
        "source",
        "first_row",
        "visual_first_row",
    ]


def print_group_summary(rows: list[dict[str, str]], fields: list[str], top: int) -> None:
    samples_by_key: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    for row in rows:
        key = tuple(row.get(field, "") for field in fields)
        row_sample = coverage_sample_key(row)
        if row_sample:
            samples_by_key[key].add(row_sample)

    print(f"  groups {'/'.join(fields)}")
    for key, count in grouped_counts(rows, fields).most_common(max(0, top)):
        label = "/".join(value or "-" for value in key)
        print(f"    {label} rows={count} samples={len(samples_by_key[key])}")


def print_examples(rows: list[dict[str, str]], fields: list[str], examples: int) -> None:
    for row in rows[: max(0, examples)]:
        parts = []
        for field in fields:
            value = row.get(field, "")
            if value:
                parts.append(f"{field}={value}")
        if parts:
            print("  example " + " ".join(parts))


def summarize_sample_delta(candidate: CoverageNeed, rows: list[dict[str, str]]) -> str:
    samples = len(selected_samples(rows))
    delta = samples - candidate.observed_samples
    if delta > 0:
        return f"expanded_samples=+{delta}"
    if delta < 0:
        return f"expanded_samples={delta}"
    return "expanded_samples=0"


def median_numeric(rows: list[dict[str, str]], field: str) -> float | None:
    values: list[float] = []
    for row in rows:
        try:
            values.append(float(row.get(field, "") or ""))
        except ValueError:
            pass
    return median(values) if values else None


def candidate_sort_key(candidate: CoverageNeed) -> tuple[int, int, int, str]:
    return (
        candidate.needed_samples,
        -candidate.observed_samples,
        -candidate.net_rows,
        candidate.section,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=pathlib.Path)
    parser.add_argument("rows", nargs="*", type=pathlib.Path)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--field", action="append", default=[])
    parser.add_argument(
        "--group-by",
        action="append",
        default=None,
        help="field to group selected rows by; may be repeated",
    )
    parser.add_argument("--example-field", action="append", default=[])
    args = parser.parse_intermixed_args()

    candidates = sorted(parse_summary(args.summary), key=candidate_sort_key)[
        : max(0, args.limit)
    ]
    existing_rows = [path for path in args.rows if path.exists()]
    print(
        f"coverage_candidate_inspection: candidates={len(candidates)} "
        f"row_paths={len(existing_rows)}/{len(args.rows)}"
    )
    if not candidates:
        print("  --")
        return 0
    if not existing_rows:
        print("  no existing row TSV paths supplied")
        return 0

    matches = read_matching_rows(existing_rows, candidates)
    configured_group_by = args.group_by
    example_fields = args.example_field or DEFAULT_EXAMPLE_FIELDS

    for candidate in candidates:
        rows = matches[candidate]
        samples = selected_samples(rows)
        print(
            f"coverage_candidate {candidate.kind} {candidate.section} "
            f"observed_samples={candidate.observed_samples} "
            f"selected_samples={len(samples)} selected_rows={len(rows)} "
            f"need_samples={candidate.needed_samples} "
            f"{summarize_sample_delta(candidate, rows)} :: {candidate.rule}"
        )
        group_by = configured_group_by or default_group_fields(rows)
        print_group_summary(rows, group_by, args.top)
        fields = args.field or list(
            dict.fromkeys(rule_fields(candidate.conditions) + DEFAULT_FIELDS)
        )
        for field in fields:
            summary = summarize_numeric(rows, field)
            if summary != "--" or field in rule_fields(candidate.conditions):
                print(f"  {field}: {summary}")
        for field in ["spectral_level", "pitch_confidence", "periodicity", "fit_error"]:
            value = median_numeric(rows, field)
            if value is not None:
                print(f"  quick_pattern {field}_median={value:.3f}")
        print_examples(rows, example_fields, args.examples)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
