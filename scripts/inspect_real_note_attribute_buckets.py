#!/usr/bin/env python3
"""Print feature ranges for selected real-note attribute buckets."""

from __future__ import annotations

import csv
import argparse
import collections
import pathlib
import re
import statistics
import sys


FIELDS = [
    "expected_midi",
    "debug_midi",
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
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
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "raw_expected_peak",
    "raw_expected_ratio",
    "raw_tuned_peak",
    "raw_tuned_ratio",
    "raw_tuned_cent_offset",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_midi",
    "raw_local_best_peak",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
]

DEFAULT_BUCKETS = [
    ("ownership_miss", "piano", "electronic", "guitar"),
    ("ownership_miss", "piano", "electronic", "bass"),
    ("ownership_miss", "guitar", "acoustic", "vocals"),
    ("ownership_miss", "guitar", "acoustic", "piano"),
    ("ownership_miss", "other", "acoustic", "guitar"),
    ("ownership_miss", "other", "acoustic", "bass"),
    ("hit", "piano", "electronic", "guitar"),
    ("hit", "guitar", "acoustic", "guitar"),
    ("hit", "other", "acoustic", "other"),
]


ROW_FOR_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}

CATEGORY_FIELDS = [
    "expected_note",
    "debug_note",
    "debug_owner",
    "row_label",
    "buffer_strongest_row",
    "raw_local_best_note",
]

ROW_DUMP_FIELDS = [
    "sample_id",
    "status",
    "family",
    "source",
    "expected_note",
    "expected_midi",
    "first_row",
    "buffer",
    "row_label",
    "row_grid",
    "any_grid",
    "buffer_strongest_row",
    "debug_note",
    "debug_owner",
    "debug_conf",
    "debug_delta",
    "debug_abs_delta",
    "miss_reason",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_note",
    "raw_expected_rank",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_notes",
    "guitar_notes",
    "piano_notes",
    "vocal_notes",
    "other_notes",
    "amb_notes",
]

NOTE_BASE = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")


def as_float(row: dict[str, str], field: str) -> float | None:
    try:
        value = row[field]
    except KeyError:
        return None
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def midi_from_note(value: str) -> int | None:
    match = NOTE_RE.match(value or "")
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def debug_delta(row: dict[str, str]) -> tuple[str, str]:
    expected = as_float(row, "expected_midi")
    debug_midi = as_float(row, "debug_midi")
    if debug_midi is None:
        debug_midi = midi_from_note(row.get("debug_note", ""))
    if expected is None or debug_midi is None:
        return "", ""
    delta = int(round(debug_midi - expected))
    return str(delta), str(abs(delta))


def miss_reason(row: dict[str, str], abs_delta: str) -> str:
    if row.get("status") == "hit":
        return "hit"
    row_key = ROW_FOR_FAMILY.get(row.get("family", ""), row.get("family", ""))
    if row.get("first_row") and row.get("first_row") != row_key:
        return "ownership"
    raw_rank = as_float(row, "raw_expected_rank")
    cent = as_float(row, "raw_tuned_abs_cent_offset")
    if raw_rank is not None and raw_rank >= 4.0:
        return "weak_expected_rank"
    if raw_rank is not None and raw_rank <= 1.0 and cent is not None and cent > 9.0:
        return "strict_tuning_reject"
    try:
        delta = int(abs_delta)
    except ValueError:
        delta = 99
    if delta == 12:
        return "octave_displacement"
    if delta <= 1:
        return "adjacent_candidate"
    if cent is not None and cent > 9.0:
        return "detuned"
    return "unresolved"


def derive_row(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    delta, abs_delta = debug_delta(row)
    result["debug_delta"] = delta
    result["debug_abs_delta"] = abs_delta
    result["miss_reason"] = miss_reason(row, abs_delta)
    return result


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def bucket_rows(
    rows: list[dict[str, str]], status: str, family: str, source: str, first_row: str
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("status") == status
        and row.get("family") == family
        and row.get("source") == source
        and row.get("first_row") == first_row
        and row.get("debug_note")
    ]


def bucket_sample_count(rows: list[dict[str, str]], key: tuple[str, str, str, str]) -> int:
    status, family, source, first_row = key
    return len(
        {
            row["sample_id"]
            for row in rows
            if row.get("status") == status
            and row.get("family") == family
            and row.get("source") == source
            and row.get("first_row") == first_row
        }
    )


def compact_counts(rows: list[dict[str, str]], field: str, limit: int = 8) -> str:
    counts = collections.Counter(row.get(field, "") for row in rows if row.get(field, ""))
    if not counts:
        return ""
    return " ".join(f"{key}={value}" for key, value in counts.most_common(limit))


def print_bucket(
    rows: list[dict[str, str]],
    status: str,
    family: str,
    source: str,
    first_row: str,
    *,
    example_limit: int,
    summary_only: bool,
) -> None:
    rows_for_bucket = bucket_rows(rows, status, family, source, first_row)
    samples = sorted({row["sample_id"] for row in rows_for_bucket})
    examples = ", ".join(samples[: max(0, example_limit)])
    print()
    print(
        f"{status}:{family}/{source}->{first_row} rows={len(rows_for_bucket)} "
        f"samples={len(samples)} examples={examples}"
    )
    for field in CATEGORY_FIELDS:
        counts = compact_counts(rows_for_bucket, field)
        if counts:
            print(f"  {field:16s} {counts}")
    if summary_only:
        return
    for field in FIELDS:
        values = sorted(value for row in rows_for_bucket if (value := as_float(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:16s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )


def parse_bucket_spec(spec: str) -> tuple[str, str, str, str]:
    match = re.fullmatch(r"([^:]+):([^/]+)/(.+)->(.+)", spec)
    if not match:
        raise SystemExit(
            f"invalid bucket `{spec}`; expected format status:family/source->first_row"
        )
    return match.group(1), match.group(2), match.group(3), match.group(4)


def format_score(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def print_sample(rows: list[dict[str, str]], sample_id: str) -> None:
    sample_rows = [row for row in rows if row.get("sample_id") == sample_id]
    print()
    if not sample_rows:
        print(f"sample {sample_id}: no rows")
        return

    first = sample_rows[0]
    print(
        f"sample {sample_id}: status={first.get('status', '')} "
        f"source={first.get('family', '')}/{first.get('source', '')} "
        f"expected={first.get('expected_note', '') or first.get('expected_midi', '')} "
        f"first_row={first.get('first_row', '')}"
    )
    for row in sample_rows:
        debug_note = row.get("debug_note", "")
        if not debug_note:
            continue
        scores = (
            format_score(as_float(row, "bass_score")),
            format_score(as_float(row, "keyboard_score")),
            format_score(as_float(row, "guitar_score")),
            format_score(as_float(row, "vocal_score")),
            format_score(as_float(row, "other_score")),
        )
        partials = (
            format_score(as_float(row, "partial1")),
            format_score(as_float(row, "partial2")),
            format_score(as_float(row, "partial3")),
            format_score(as_float(row, "partial4")),
            format_score(as_float(row, "partial5")),
        )
        print(
            f"  buffer={row.get('buffer', '')} row_label=`{row.get('row_label', '')}` "
            f"row_grid={row.get('row_grid', '')} any_grid={row.get('any_grid', '')} "
            f"strongest={row.get('buffer_strongest_row', '')} debug={debug_note} "
            f"owner={row.get('debug_owner', '')} conf={format_score(as_float(row, 'debug_conf'))} "
            f"scores(b/k/g/v/o)={scores[0]}/{scores[1]}/{scores[2]}/{scores[3]}/{scores[4]} "
            f"spec={format_score(as_float(row, 'spectral_level'))} "
            f"pitch={format_score(as_float(row, 'pitch_confidence'))} "
            f"per={format_score(as_float(row, 'periodicity'))} "
            f"fit={format_score(as_float(row, 'fit_error'))} "
            f"cent={format_score(as_float(row, 'centroid'))} "
            f"slope={format_score(as_float(row, 'slope'))} "
            f"noise={format_score(as_float(row, 'noise'))} "
            f"raw={format_score(as_float(row, 'raw_expected_ratio'))}/"
            f"{format_score(as_float(row, 'raw_tuned_ratio'))} "
            f"raw_best={row.get('raw_local_best_note', '')}/"
            f"{format_score(as_float(row, 'raw_local_best_peak'))} "
            f"raw_rank={format_score(as_float(row, 'raw_expected_rank'))} "
            f"partials={partials[0]},{partials[1]},{partials[2]},{partials[3]},{partials[4]}"
        )


def dump_rows(
    rows: list[dict[str, str]],
    *,
    buckets: list[tuple[str, str, str, str]],
    sample_ids: list[str],
    misses_only: bool,
    limit: int,
) -> None:
    bucket_filter = set(buckets)
    sample_filter = set(sample_ids)
    printed = 0
    print("\t".join(ROW_DUMP_FIELDS))
    for row in rows:
        if not row.get("debug_note"):
            continue
        if misses_only and row.get("status") != "ownership_miss":
            continue
        if bucket_filter:
            key = (
                row.get("status", ""),
                row.get("family", ""),
                row.get("source", ""),
                row.get("first_row", ""),
            )
            if key not in bucket_filter:
                continue
        if sample_filter and row.get("sample_id", "") not in sample_filter:
            continue
        derived = derive_row(row)
        print("\t".join(derived.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def top_bucket_keys(
    rows: list[dict[str, str]],
    top_misses: int,
    *,
    include_comparisons: bool,
    include_defaults: bool,
) -> list[tuple[str, str, str, str]]:
    counts: collections.Counter[tuple[str, str, str, str]] = collections.Counter()
    for row in rows:
        key = (row.get("status", ""), row.get("family", ""), row.get("source", ""), row.get("first_row", ""))
        if "" in key:
            continue
        counts[key] += 1

    keys: list[tuple[str, str, str, str]] = []
    for key, _row_count in counts.most_common():
        status, family, source, first_row = key
        if status != "ownership_miss":
            continue
        keys.append(key)
        if include_comparisons:
            expected_row = ROW_FOR_FAMILY.get(family)
            comparisons = [
                ("hit", family, source, first_row),
                ("hit", family, source, expected_row or first_row),
            ]
            for comparison in comparisons:
                if comparison in counts:
                    keys.append(comparison)
        if len({key for key in keys if key[0] == "ownership_miss"}) >= top_misses:
            break

    if include_defaults:
        for bucket in DEFAULT_BUCKETS:
            keys.append(bucket)

    deduped = []
    seen = set()
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        if bucket_sample_count(rows, key) <= 0:
            continue
        deduped.append(key)
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--top-misses",
        type=int,
        default=12,
        help="number of largest ownership-miss buckets to print before fixed comparison buckets",
    )
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="print only this bucket, formatted as status:family/source->first_row; repeatable",
    )
    parser.add_argument(
        "--sample-id",
        action="append",
        default=[],
        help="print per-buffer detector attributes for this sample id; repeatable",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=12,
        help="number of sample IDs to include in each bucket header",
    )
    parser.add_argument(
        "--misses-only",
        action="store_true",
        help="print only the largest ownership-miss buckets, without comparison or fixed buckets",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print bucket counts and categorical summaries without numeric feature ranges",
    )
    parser.add_argument(
        "--dump-rows",
        action="store_true",
        help="print compact per-buffer detected attributes as TSV and skip bucket summaries",
    )
    parser.add_argument(
        "--dump-limit",
        type=int,
        default=0,
        help="maximum rows to print in --dump-rows mode; 0 means all",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    rows = load_rows(path)
    explicit_buckets = [parse_bucket_spec(spec) for spec in args.bucket]
    if args.dump_rows:
        dump_rows(
            rows,
            buckets=explicit_buckets,
            sample_ids=args.sample_id,
            misses_only=args.misses_only,
            limit=max(0, args.dump_limit),
        )
        return 0

    if explicit_buckets:
        buckets = explicit_buckets
    elif args.sample_id:
        buckets = []
    else:
        buckets = top_bucket_keys(
            rows,
            max(0, args.top_misses),
            include_comparisons=not args.misses_only,
            include_defaults=not args.misses_only,
        )

    for bucket in buckets:
        print_bucket(
            rows,
            *bucket,
            example_limit=args.examples,
            summary_only=args.summary_only,
        )
    for sample_id in args.sample_id:
        print_sample(rows, sample_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
