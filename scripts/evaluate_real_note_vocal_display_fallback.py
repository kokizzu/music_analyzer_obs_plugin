#!/usr/bin/env python3
"""Score candidate vocal-display fallback rules on real-note TSV exports."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import statistics

from inspect_real_note_attribute_buckets import derive_row, midi_from_note, note_row_levels
from measure_real_note_attribute_rule import (
    apply_numeric_buckets,
    matches_condition,
    parse_condition,
    parse_numeric_bucket,
)


Condition = tuple[str, str, str]


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def as_int(row: dict[str, str], field: str) -> int | None:
    value = as_float(row, field)
    if value is None:
        return None
    return int(round(value))


def debug_midi(row: dict[str, str]) -> int | None:
    value = as_int(row, "debug_midi")
    if value is not None:
        return value
    return midi_from_note(row.get("debug_note", ""))


def expected_midi(row: dict[str, str]) -> int | None:
    return as_int(row, "expected_midi")


def same_expected_debug_pitch(row: dict[str, str]) -> bool:
    expected = expected_midi(row)
    debug = debug_midi(row)
    return expected is not None and debug is not None and expected == debug


def vocal_visual_exact_level(row: dict[str, str]) -> float:
    midi = debug_midi(row)
    if midi is None:
        return 0.0
    exact, _pitch, _delta = note_row_levels(row, "vocals", midi, visual=True)
    return exact


def row_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row.get("sample_id", ""), row.get("buffer", ""), row.get("debug_note", "")


def sample_count(rows: list[dict[str, str]]) -> int:
    return len({row.get("sample_id", "") for row in rows if row.get("sample_id", "")})


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{numerator * 100.0 / denominator:.1f}%"


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def range_summary(values: list[float]) -> str:
    if not values:
        return "--"
    ordered = sorted(values)
    return (
        f"min={ordered[0]:.3f} q25={quantile(ordered, 0.25):.3f} "
        f"med={statistics.median(ordered):.3f} q75={quantile(ordered, 0.75):.3f} "
        f"max={ordered[-1]:.3f}"
    )


def load_rows(path: pathlib.Path, numeric_buckets: list[tuple[str, object, int]]) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return [
            apply_numeric_buckets(derive_row(row), numeric_buckets)
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def matching_candidate_rows(rows: list[dict[str, str]], conditions: list[Condition]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if same_expected_debug_pitch(row)
        and all(matches_condition(row, condition) for condition in conditions)
    ]


def examples(rows: list[dict[str, str]], limit: int) -> str:
    keys = sorted({row.get("sample_id", "") for row in rows if row.get("sample_id", "")})
    if not keys or limit <= 0:
        return "--"
    return " ".join(keys[:limit])


def print_groups(label: str, rows: list[dict[str, str]], group_by: list[str], top: int) -> None:
    if not rows or top <= 0:
        return
    counts: collections.Counter[tuple[str, ...]] = collections.Counter()
    grouped_samples: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    for row in rows:
        key = tuple(row.get(field, "") for field in group_by)
        counts[key] += 1
        sample_id = row.get("sample_id", "")
        if sample_id:
            grouped_samples[key].add(sample_id)
    print(f"{label} groups " + "/".join(group_by))
    for key, count in counts.most_common(top):
        group_label = "/".join(value or "-" for value in key)
        print(f"  {group_label} rows={count} samples={len(grouped_samples[key])}")


def split_primary(
    rows: list[dict[str, str]], visibility_threshold: float
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    positive: list[dict[str, str]] = []
    already_visible: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") != "vocals":
            continue
        if vocal_visual_exact_level(row) >= visibility_threshold:
            already_visible.append(row)
        else:
            positive.append(row)
    return positive, already_visible


def split_side_effects(
    rows: list[dict[str, str]], visibility_threshold: float
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    side_effect: list[dict[str, str]] = []
    already_false: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") == "vocals":
            continue
        if vocal_visual_exact_level(row) >= visibility_threshold:
            already_false.append(row)
        else:
            side_effect.append(row)
    return side_effect, already_false


def print_metric(label: str, rows: list[dict[str, str]], denominator_samples: int) -> None:
    print(
        f"{label} rows={len(rows)} samples={sample_count(rows)} "
        f"sample_rate={pct(sample_count(rows), denominator_samples)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="primary TSV path; normally Vocadito full-mix attributes")
    parser.add_argument(
        "--compare-path",
        action="append",
        default=[],
        help="non-vocal side-effect TSV path; defaults to the primary path when omitted",
    )
    parser.add_argument(
        "--condition",
        action="append",
        default=[],
        help="candidate rule condition: field=value, field!=value, field>=number, field<=number, or field:min:max",
    )
    parser.add_argument(
        "--visibility-threshold",
        type=float,
        default=0.25,
        help="visual note level considered visible",
    )
    parser.add_argument(
        "--group-by",
        action="append",
        default=None,
        help="field to group matches by; repeatable",
    )
    parser.add_argument(
        "--numeric-bucket",
        action="append",
        default=[],
        help="derive FIELD_bucket from numeric FIELD using WIDTH-sized ranges",
    )
    parser.add_argument("--top", type=int, default=20, help="number of groups to print")
    parser.add_argument("--examples", type=int, default=8, help="number of sample ids to print")
    parser.add_argument("--summary-only", action="store_true", help="hide examples and field ranges")
    args = parser.parse_args()

    primary_path = pathlib.Path(args.path)
    compare_paths = [pathlib.Path(path) for path in args.compare_path] or [primary_path]
    conditions = [parse_condition(spec) for spec in args.condition]
    numeric_buckets = [parse_numeric_bucket(spec) for spec in args.numeric_bucket]
    group_by = args.group_by or ["debug_owner", "expected_octave", "visual_first_row"]

    primary_candidates = matching_candidate_rows(load_rows(primary_path, numeric_buckets), conditions)
    compare_candidates: list[dict[str, str]] = []
    seen_side_effect_rows: set[tuple[str, str, str, str]] = set()
    for path in compare_paths:
        for row in matching_candidate_rows(load_rows(path, numeric_buckets), conditions):
            key = (str(path), *row_key(row))
            if key in seen_side_effect_rows:
                continue
            seen_side_effect_rows.add(key)
            compare_candidates.append(row)

    positive, already_visible = split_primary(primary_candidates, args.visibility_threshold)
    side_effect, already_false = split_side_effects(compare_candidates, args.visibility_threshold)
    vocal_sample_denominator = sample_count(
        [row for row in primary_candidates if row.get("family") == "vocals"]
    )
    non_vocal_sample_denominator = sample_count(
        [row for row in compare_candidates if row.get("family") != "vocals"]
    )

    print(f"primary path={primary_path}")
    print("compare paths=" + " ".join(str(path) for path in compare_paths))
    print(
        f"settings visibility_threshold={args.visibility_threshold:.3f} "
        f"conditions={' '.join(args.condition) if args.condition else '--'}"
    )
    print_metric("positive_missing_vocal", positive, vocal_sample_denominator)
    print_metric("already_visible_vocal", already_visible, vocal_sample_denominator)
    print_metric("side_effect_non_vocal", side_effect, non_vocal_sample_denominator)
    print_metric("already_false_vocal", already_false, non_vocal_sample_denominator)
    print(
        f"utility net_rows={len(positive) - len(side_effect)} "
        f"net_samples={sample_count(positive) - sample_count(side_effect)}"
    )

    if not args.summary_only:
        print(f"positive examples {examples(positive, args.examples)}")
        print(f"side_effect examples {examples(side_effect, args.examples)}")
        for field in (
            "debug_conf",
            "spectral_level",
            "pitch_confidence",
            "periodicity",
            "fit_error",
            "centroid",
            "slope",
            "noise",
            "partial2",
            "partial3",
            "partial4",
            "partial5",
        ):
            values = [value for row in positive if (value := as_float(row, field)) is not None]
            if values:
                print(f"positive {field} {range_summary(values)}")

    print_groups("positive", positive, group_by, args.top)
    print_groups("side_effect", side_effect, group_by, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
