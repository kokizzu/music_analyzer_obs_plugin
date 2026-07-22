#!/usr/bin/env python3
"""Print feature ranges for selected GuitarSet chord attribute buckets."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics

from summarize_guitarset_attributes import (
    as_float,
    as_int,
    best_expected_chord,
    chord_tones,
    load_rows,
    parse_cell_levels,
    parse_pitch_classes,
)


NUMERIC_FIELDS = [
    "expected_note_count",
    "expected_pitch_class_count",
    "expected_chord_tone_count",
    "guitar_note_hits",
    "guitar_false_positive_pitch_classes",
    "cross_row_expected_hits",
    "expected_raw_peak",
    "rms",
    "low",
    "mid",
    "high",
    "guitar_pc_count",
    "analysis_pc_count",
    "smooth_pc_count",
    "visible_tones",
    "analysis_tones",
    "smooth_tones",
    "root_visible",
    "visible_root",
    "visible_third",
    "visible_fifth",
    "analysis_root",
    "analysis_third",
    "analysis_fifth",
    "smooth_root",
    "smooth_third",
    "smooth_fifth",
    "raw_root",
    "raw_third",
    "raw_fifth",
]

CATEGORY_FIELDS = [
    "expected_chords",
    "expected_chord_qualities",
    "guitar_chord",
    "global_chord",
    "expected_pitch_classes",
    "guitar_pitch_classes",
    "guitar_analysis_pitch_classes",
    "guitar_smoothed_pitch_classes",
    "visible_missing_tones",
    "analysis_missing_tones",
    "smooth_missing_tones",
    "support",
]

ROW_DUMP_FIELDS = [
    "recording_id",
    "status",
    "expected_chords",
    "expected_chord_qualities",
    "quality",
    "guitar_chord",
    "global_chord",
    "support",
    "expected_pitch_classes",
    "guitar_pitch_classes",
    "guitar_analysis_pitch_classes",
    "guitar_smoothed_pitch_classes",
    "visible_missing_tones",
    "analysis_missing_tones",
    "smooth_missing_tones",
    "visible_root",
    "visible_third",
    "visible_fifth",
    "analysis_root",
    "analysis_third",
    "analysis_fifth",
    "smooth_root",
    "smooth_third",
    "smooth_fifth",
    "raw_root",
    "raw_third",
    "raw_fifth",
    "guitar_note_hits",
    "guitar_false_positive_pitch_classes",
    "cross_row_expected_hits",
    "rms",
    "low",
    "mid",
    "high",
    "audio_path",
]

BUCKET_RE = re.compile(r"([^:]+):([^:]+):(.+)")


def normalized_quality(row: dict[str, str], expected_label: str) -> str:
    quality = row.get("expected_chord_qualities", "")
    if quality and quality != "--":
        if quality in {"min", "minor"}:
            return "m"
        if quality in {"major"}:
            return "maj"
        return quality
    if expected_label.endswith("m"):
        return "m"
    return "maj" if expected_label else "--"


def tone_key(name: str) -> str:
    if name in {"major_third", "minor_third"}:
        return "third"
    return name


def compact_missing(missing: list[str]) -> str:
    return ",".join(sorted(set(missing))) or "--"


def max_level(levels: dict[int, float], pitch_classes: list[int]) -> float:
    value = 0.0
    for pitch_class in pitch_classes:
        value = max(value, levels.get(pitch_class, 0.0))
    return value


def derive_row(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    expected_label = best_expected_chord(
        row.get("expected_chords", ""), row.get("guitar_analysis_pitch_classes", "")
    )
    quality = normalized_quality(row, expected_label)
    tone_classes: dict[str, list[int]] = collections.defaultdict(list)
    for name, pitch_class in chord_tones(expected_label):
        tone_classes[tone_key(name)].append(pitch_class)

    visible = parse_pitch_classes(row.get("guitar_pitch_classes", ""))
    analysis = parse_pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
    smooth = parse_pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))
    visible_levels = parse_cell_levels(row.get("guitar_cells", ""))
    analysis_levels = parse_cell_levels(row.get("guitar_analysis_cells", ""))
    smooth_levels = parse_cell_levels(row.get("guitar_smoothed_cells", ""))
    raw_levels = parse_cell_levels(row.get("expected_raw_cells", ""))

    expected_pitch_classes = set()
    for pitch_classes in tone_classes.values():
        expected_pitch_classes.update(pitch_classes)

    def support_count(pitch_classes: set[int]) -> int:
        return len(expected_pitch_classes & pitch_classes)

    def missing_tones(pitch_classes: set[int]) -> str:
        missing = [
            key
            for key, tone_pitch_classes in tone_classes.items()
            if not any(pitch_class in pitch_classes for pitch_class in tone_pitch_classes)
        ]
        return compact_missing(missing)

    visible_tones = support_count(visible)
    analysis_tones = support_count(analysis)
    smooth_tones = support_count(smooth)
    root_visible = int(any(pitch_class in visible for pitch_class in tone_classes.get("root", [])))
    support = (
        f"visible{visible_tones}_analysis{analysis_tones}_"
        f"smooth{smooth_tones}_rootvis{root_visible}"
    )

    result.update(
        {
            "expected_label": expected_label,
            "quality": quality,
            "support": support,
            "guitar_pc_count": str(len(visible)),
            "analysis_pc_count": str(len(analysis)),
            "smooth_pc_count": str(len(smooth)),
            "visible_tones": str(visible_tones),
            "analysis_tones": str(analysis_tones),
            "smooth_tones": str(smooth_tones),
            "root_visible": str(root_visible),
            "visible_missing_tones": missing_tones(visible),
            "analysis_missing_tones": missing_tones(analysis),
            "smooth_missing_tones": missing_tones(smooth),
        }
    )

    for key in ("root", "third", "fifth"):
        pitch_classes = tone_classes.get(key, [])
        result[f"visible_{key}"] = f"{max_level(visible_levels, pitch_classes):.6f}"
        result[f"analysis_{key}"] = f"{max_level(analysis_levels, pitch_classes):.6f}"
        result[f"smooth_{key}"] = f"{max_level(smooth_levels, pitch_classes):.6f}"
        result[f"raw_{key}"] = f"{max_level(raw_levels, pitch_classes):.6f}"
    return result


def derive_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [derive_row(row) for row in rows if row.get("expected_chords", "--") not in {"", "--"}]


def parse_bucket_spec(spec: str) -> tuple[str, str, str]:
    match = BUCKET_RE.fullmatch(spec)
    if not match:
        raise SystemExit(
            f"invalid bucket `{spec}`; expected format status:quality:support, e.g. "
            "chord_miss:maj:visible2_analysis3_smooth3_rootvis1"
        )
    return match.group(1), match.group(2), match.group(3)


def bucket_label(bucket: tuple[str, str, str]) -> str:
    return f"{bucket[0]}:{bucket[1]}:{bucket[2]}"


def bucket_matches(row: dict[str, str], bucket: tuple[str, str, str]) -> bool:
    status, quality, support = bucket
    if row.get("status") != status or row.get("quality") != quality:
        return False
    return support == "all" or row.get("support") == support


def bucket_rows(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> list[dict[str, str]]:
    return [row for row in rows if bucket_matches(row, bucket)]


def bucket_recording_count(rows: list[dict[str, str]], bucket: tuple[str, str, str]) -> int:
    return len({row.get("recording_id", "") for row in rows if bucket_matches(row, bucket)})


def top_bucket_keys(
    rows: list[dict[str, str]],
    top_misses: int,
    *,
    include_comparisons: bool,
) -> list[tuple[str, str, str]]:
    counts: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for row in rows:
        if row.get("status") != "chord_miss":
            continue
        counts[(row.get("status", ""), row.get("quality", ""), row.get("support", ""))] += 1

    keys: list[tuple[str, str, str]] = []
    for key, _count in counts.most_common(max(0, top_misses)):
        keys.append(key)
        if not include_comparisons:
            continue
        quality = key[1]
        for comparison in (("chord_hit", quality, key[2]), ("chord_hit", quality, "all")):
            if bucket_recording_count(rows, comparison) > 0:
                keys.append(comparison)

    deduped: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        if bucket_recording_count(rows, key) <= 0:
            continue
        deduped.append(key)
    return deduped


def as_float_opt(row: dict[str, str], field: str) -> float | None:
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


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def compact_counts(rows: list[dict[str, str]], field: str, limit: int = 8) -> str:
    counts = collections.Counter(row.get(field, "") for row in rows if row.get(field, ""))
    if not counts:
        return ""
    return " ".join(f"{key}={value}" for key, value in counts.most_common(limit))


def print_bucket(
    rows: list[dict[str, str]],
    bucket: tuple[str, str, str],
    *,
    example_limit: int,
    summary_only: bool,
) -> None:
    rows_for_bucket = bucket_rows(rows, bucket)
    recordings = sorted({row.get("recording_id", "") for row in rows_for_bucket})
    examples = ", ".join(recordings[: max(0, example_limit)])
    print()
    print(
        f"{bucket_label(bucket)} rows={len(rows_for_bucket)} recordings={len(recordings)} "
        f"examples={examples}"
    )
    for field in CATEGORY_FIELDS:
        counts = compact_counts(rows_for_bucket, field)
        if counts:
            print(f"  {field:31s} {counts}")
    if summary_only:
        return
    for field in NUMERIC_FIELDS:
        values = sorted(value for row in rows_for_bucket if (value := as_float_opt(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:31s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )


def format_score(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def print_recording(rows: list[dict[str, str]], recording_id: str) -> None:
    sample_rows = [row for row in rows if row.get("recording_id") == recording_id]
    print()
    if not sample_rows:
        print(f"recording {recording_id}: no rows")
        return
    for row in sample_rows:
        print(
            f"recording {recording_id}: status={row.get('status', '')} "
            f"expected={row.get('expected_chords', '')} quality={row.get('quality', '')} "
            f"guitar={row.get('guitar_chord', '')} support={row.get('support', '')}"
        )
        print(
            f"  pc visible={row.get('guitar_pitch_classes', '--')} "
            f"analysis={row.get('guitar_analysis_pitch_classes', '--')} "
            f"smooth={row.get('guitar_smoothed_pitch_classes', '--')}"
        )
        print(
            "  levels raw(root/third/fifth)="
            f"{format_score(as_float_opt(row, 'raw_root'))}/"
            f"{format_score(as_float_opt(row, 'raw_third'))}/"
            f"{format_score(as_float_opt(row, 'raw_fifth'))} "
            "analysis="
            f"{format_score(as_float_opt(row, 'analysis_root'))}/"
            f"{format_score(as_float_opt(row, 'analysis_third'))}/"
            f"{format_score(as_float_opt(row, 'analysis_fifth'))} "
            "visible="
            f"{format_score(as_float_opt(row, 'visible_root'))}/"
            f"{format_score(as_float_opt(row, 'visible_third'))}/"
            f"{format_score(as_float_opt(row, 'visible_fifth'))}"
        )


def dump_rows(
    rows: list[dict[str, str]],
    *,
    buckets: list[tuple[str, str, str]],
    recording_ids: list[str],
    misses_only: bool,
    limit: int,
) -> None:
    bucket_filter = set(buckets)
    recording_filter = set(recording_ids)
    printed = 0
    print("\t".join(ROW_DUMP_FIELDS))
    for row in rows:
        if misses_only and row.get("status") != "chord_miss":
            continue
        if bucket_filter and not any(bucket_matches(row, bucket) for bucket in bucket_filter):
            continue
        if recording_filter and row.get("recording_id", "") not in recording_filter:
            continue
        print("\t".join(row.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--top-misses", type=int, default=8)
    parser.add_argument(
        "--bucket",
        action="append",
        default=[],
        help="print only this bucket, formatted as status:quality:support; repeatable",
    )
    parser.add_argument(
        "--recording-id",
        action="append",
        default=[],
        help="print detailed derived attributes for this recording id; repeatable",
    )
    parser.add_argument("--examples", type=int, default=12)
    parser.add_argument(
        "--misses-only",
        action="store_true",
        help="print only largest chord-miss buckets, without chord-hit comparisons",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print bucket counts and categorical summaries without numeric feature ranges",
    )
    parser.add_argument(
        "--dump-rows",
        action="store_true",
        help="print compact per-recording chord attributes as TSV and skip bucket summaries",
    )
    parser.add_argument(
        "--dump-limit",
        type=int,
        default=0,
        help="maximum rows to print in --dump-rows mode; 0 means all",
    )
    args = parser.parse_args()

    rows = derive_rows(load_rows(pathlib.Path(args.path)))
    explicit_buckets = [parse_bucket_spec(spec) for spec in args.bucket]
    if args.dump_rows:
        dump_rows(
            rows,
            buckets=explicit_buckets,
            recording_ids=args.recording_id,
            misses_only=args.misses_only,
            limit=max(0, args.dump_limit),
        )
        return 0

    if explicit_buckets:
        buckets = explicit_buckets
    elif args.recording_id:
        buckets = []
    else:
        buckets = top_bucket_keys(rows, args.top_misses, include_comparisons=not args.misses_only)

    for bucket in buckets:
        print_bucket(
            rows,
            bucket,
            example_limit=args.examples,
            summary_only=args.summary_only,
        )
    for recording_id in args.recording_id:
        print_recording(rows, recording_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
