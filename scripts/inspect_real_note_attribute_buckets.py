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
    "third_octave_ratio",
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
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
    "raw_best_debug_delta",
    "raw_best_debug_abs_delta",
    "expected_row_exact_level",
    "expected_row_pitch_level",
    "expected_row_pitch_delta",
    "strongest_row_exact_level",
    "strongest_row_pitch_level",
    "strongest_row_pitch_delta",
    "expected_exact_row_count",
    "expected_pitch_row_count",
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
    "debug_score_state",
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
    "visual_first_row",
    "buffer",
    "row_label",
    "row_grid",
    "any_grid",
    "buffer_strongest_row",
    "buffer_visual_strongest_row",
    "debug_note",
    "debug_owner",
    "debug_conf",
    "debug_score_state",
    "debug_delta",
    "debug_abs_delta",
    "miss_reason",
    "expected_row_exact_level",
    "expected_row_pitch_level",
    "expected_row_pitch_delta",
    "strongest_row_exact_level",
    "strongest_row_pitch_level",
    "strongest_row_pitch_delta",
    "expected_exact_row_count",
    "expected_pitch_row_count",
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
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_note",
    "raw_expected_rank",
    "raw_best_debug_delta",
    "raw_best_debug_abs_delta",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_visual_level",
    "guitar_visual_level",
    "piano_visual_level",
    "vocal_visual_level",
    "other_visual_level",
    "amb_visual_level",
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
NOTE_CELL_RE = re.compile(r"([A-G]#?-?\d+):([0-9.]+)")

ROW_NOTE_FIELDS = {
    "bass": "bass_notes",
    "guitar": "guitar_notes",
    "piano": "piano_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
    "amb": "amb_notes",
}


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


def parse_note_cells(value: str) -> list[tuple[int, float]]:
    cells: list[tuple[int, float]] = []
    for note, level in NOTE_CELL_RE.findall(value or ""):
        midi = midi_from_note(note)
        if midi is None:
            continue
        try:
            cells.append((midi, float(level)))
        except ValueError:
            continue
    return cells


def format_derived_float(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def note_row_cells(row: dict[str, str], row_name: str) -> list[tuple[int, float]]:
    field = ROW_NOTE_FIELDS.get(row_name)
    if not field:
        return []
    return parse_note_cells(row.get(field, ""))


def note_row_levels(row: dict[str, str], row_name: str, target_midi: int) -> tuple[float, float, int | None]:
    cells = note_row_cells(row, row_name)
    if not cells:
        return 0.0, 0.0, None

    target_pitch = ((target_midi % 12) + 12) % 12
    exact_level = 0.0
    pitch_level = 0.0
    pitch_delta: int | None = None
    for midi, level in cells:
        if midi == target_midi:
            exact_level = max(exact_level, level)
        if ((midi % 12) + 12) % 12 != target_pitch:
            continue
        if level > pitch_level:
            pitch_level = level
            pitch_delta = midi - target_midi
    return exact_level, pitch_level, pitch_delta


def note_row_counts(row: dict[str, str], target_midi: int) -> tuple[int, int]:
    exact_rows = 0
    pitch_rows = 0
    target_pitch = ((target_midi % 12) + 12) % 12
    for row_name in ("bass", "guitar", "piano", "vocals", "other"):
        exact_seen = False
        pitch_seen = False
        for midi, _level in note_row_cells(row, row_name):
            if midi == target_midi:
                exact_seen = True
            if ((midi % 12) + 12) % 12 == target_pitch:
                pitch_seen = True
        exact_rows += int(exact_seen)
        pitch_rows += int(pitch_seen)
    return exact_rows, pitch_rows


def debug_delta(row: dict[str, str]) -> tuple[str, str]:
    expected = as_float(row, "expected_midi")
    debug_midi = as_float(row, "debug_midi")
    if debug_midi is None:
        debug_midi = midi_from_note(row.get("debug_note", ""))
    if expected is None or debug_midi is None:
        return "", ""
    delta = int(round(debug_midi - expected))
    return str(delta), str(abs(delta))


def numeric_delta(row: dict[str, str], left_field: str, right_field: str) -> tuple[str, str]:
    left = as_float(row, left_field)
    right = as_float(row, right_field)
    if left is None or right is None:
        return "", ""
    delta = int(round(left - right))
    return str(delta), str(abs(delta))


def debug_score_state(row: dict[str, str]) -> str:
    if not row.get("debug_note") and not row.get("debug_midi"):
        return "no_debug"
    score_fields = ("bass_score", "keyboard_score", "guitar_score", "vocal_score", "other_score")
    has_score = any((as_float(row, field) or 0.0) > 1.0e-6 for field in score_fields)
    owner = row.get("debug_owner", "")
    if owner == "amb":
        return "scored_amb" if has_score else "unscored_amb"
    return "scored_owner" if has_score else "unscored_owner"


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
    raw_best_delta, raw_best_abs_delta = numeric_delta(row, "raw_local_best_midi", "debug_midi")
    result["raw_best_debug_delta"] = raw_best_delta
    result["raw_best_debug_abs_delta"] = raw_best_abs_delta
    result["debug_score_state"] = debug_score_state(row)
    result["miss_reason"] = miss_reason(row, abs_delta)
    expected = as_float(row, "expected_midi")
    if expected is not None:
        expected_midi = int(round(expected))
        expected_row = ROW_FOR_FAMILY.get(row.get("family", ""), row.get("family", ""))
        strongest_row = row.get("buffer_strongest_row", "")
        expected_exact, expected_pitch, expected_delta = note_row_levels(row, expected_row, expected_midi)
        strongest_exact, strongest_pitch, strongest_delta = note_row_levels(row, strongest_row, expected_midi)
        exact_count, pitch_count = note_row_counts(row, expected_midi)
        result["expected_row_exact_level"] = format_derived_float(expected_exact)
        result["expected_row_pitch_level"] = format_derived_float(expected_pitch)
        result["expected_row_pitch_delta"] = "" if expected_delta is None else str(expected_delta)
        result["strongest_row_exact_level"] = format_derived_float(strongest_exact)
        result["strongest_row_pitch_level"] = format_derived_float(strongest_pitch)
        result["strongest_row_pitch_delta"] = "" if strongest_delta is None else str(strongest_delta)
        result["expected_exact_row_count"] = str(exact_count)
        result["expected_pitch_row_count"] = str(pitch_count)
    return result


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def bucket_rows(
    rows: list[dict[str, str]], status: str, family: str, source: str, first_row: str
) -> list[dict[str, str]]:
    return [row for row in rows if row_matches_bucket(row, status, family, source, first_row)]


def row_matches_bucket(
    row: dict[str, str], status: str, family: str, source: str, target_row: str
) -> bool:
    if row.get("family") != family or row.get("source") != source or not row.get("debug_note"):
        return False
    if status == "row_confusion":
        expected_row = ROW_FOR_FAMILY.get(family, family)
        strongest_row = row.get("buffer_strongest_row", "")
        return row.get("status") == "hit" and strongest_row == target_row and strongest_row != expected_row
    if status == "visual_row_confusion":
        expected_row = ROW_FOR_FAMILY.get(family, family)
        strongest_row = row.get("buffer_visual_strongest_row", "")
        return row.get("status") == "hit" and strongest_row == target_row and strongest_row != expected_row
    return row.get("status") == status and row.get("first_row") == target_row


def bucket_sample_count(rows: list[dict[str, str]], key: tuple[str, str, str, str]) -> int:
    status, family, source, first_row = key
    return len({row["sample_id"] for row in rows if row_matches_bucket(row, status, family, source, first_row)})


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
    rows_for_bucket = [derive_row(row) for row in bucket_rows(rows, status, family, source, first_row)]
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
            if not any(row_matches_bucket(row, *key) for key in bucket_filter):
                continue
        if sample_filter and row.get("sample_id", "") not in sample_filter:
            continue
        derived = derive_row(row)
        print("\t".join(derived.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


def filter_rows(
    rows: list[dict[str, str]],
    *,
    statuses: set[str],
    families: set[str],
    sources: set[str],
    first_rows: set[str],
    visual_first_rows: set[str],
    row_labels: set[str],
    miss_reasons: set[str],
) -> list[dict[str, str]]:
    if not any((statuses, families, sources, first_rows, visual_first_rows, row_labels, miss_reasons)):
        return rows

    filtered: list[dict[str, str]] = []
    for row in rows:
        if statuses and row.get("status", "") not in statuses:
            continue
        if families and row.get("family", "") not in families:
            continue
        if sources and row.get("source", "") not in sources:
            continue
        if first_rows and row.get("first_row", "") not in first_rows:
            continue
        if visual_first_rows and row.get("visual_first_row", "") not in visual_first_rows:
            continue
        if row_labels and row.get("row_label", "") not in row_labels:
            continue
        if miss_reasons and derive_row(row).get("miss_reason", "") not in miss_reasons:
            continue
        filtered.append(row)
    return filtered


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def top_bucket_keys(
    rows: list[dict[str, str]],
    top_misses: int,
    *,
    bucket_status: str,
    include_comparisons: bool,
    include_defaults: bool,
) -> list[tuple[str, str, str, str]]:
    counts: collections.Counter[tuple[str, str, str, str]] = collections.Counter()
    for row in rows:
        family = row.get("family", "")
        expected_row = ROW_FOR_FAMILY.get(family, family)
        if bucket_status == "row_confusion":
            target_row = row.get("buffer_strongest_row", "")
            if row.get("status") != "hit" or not target_row or target_row == expected_row:
                continue
            key = ("row_confusion", family, row.get("source", ""), target_row)
        elif bucket_status == "visual_row_confusion":
            target_row = row.get("buffer_visual_strongest_row", "")
            if row.get("status") != "hit" or not target_row or target_row == expected_row:
                continue
            key = ("visual_row_confusion", family, row.get("source", ""), target_row)
        else:
            key = (row.get("status", ""), family, row.get("source", ""), row.get("first_row", ""))
        if "" in key:
            continue
        counts[key] += 1

    keys: list[tuple[str, str, str, str]] = []
    for key, _row_count in counts.most_common():
        status, family, source, first_row = key
        if status != bucket_status:
            continue
        keys.append(key)
        if include_comparisons and bucket_status == "ownership_miss":
            expected_row = ROW_FOR_FAMILY.get(family)
            comparisons = [
                ("hit", family, source, first_row),
                ("hit", family, source, expected_row or first_row),
            ]
            for comparison in comparisons:
                if comparison in counts:
                    keys.append(comparison)
        if len({key for key in keys if key[0] == bucket_status}) >= top_misses:
            break

    if include_defaults and bucket_status == "ownership_miss":
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
        "--bucket-status",
        choices=("ownership_miss", "row_confusion", "visual_row_confusion"),
        default="ownership_miss",
        help="status used for automatically selected top buckets",
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
    parser.add_argument("--status", action="append", default=[], help="include only this row status; repeatable")
    parser.add_argument("--family", action="append", default=[], help="include only this expected family; repeatable")
    parser.add_argument("--source", action="append", default=[], help="include only this source subtype; repeatable")
    parser.add_argument("--first-row", action="append", default=[], help="include only this first detected row; repeatable")
    parser.add_argument(
        "--visual-first-row",
        action="append",
        default=[],
        help="include only this first visually displayed row; repeatable",
    )
    parser.add_argument("--row-label", action="append", default=[], help="include only this per-buffer row label; repeatable")
    parser.add_argument(
        "--miss-reason",
        action="append",
        default=[],
        help="include only this derived miss reason in --dump-rows or bucket summaries; repeatable",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    rows = filter_rows(
        load_rows(path),
        statuses=set(args.status),
        families=set(args.family),
        sources=set(args.source),
        first_rows=set(args.first_row),
        visual_first_rows=set(args.visual_first_row),
        row_labels=set(args.row_label),
        miss_reasons=set(args.miss_reason),
    )
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
            bucket_status=args.bucket_status,
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
