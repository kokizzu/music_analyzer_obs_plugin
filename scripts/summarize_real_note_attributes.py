#!/usr/bin/env python3
"""Summarize real-note per-buffer detector attribute TSV exports."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics


NUMERIC_FIELDS = [
    "row_conf",
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
    "rms",
    "low",
    "mid",
    "high",
    "kick",
    "snare",
    "hihat",
    "crash",
    "tom",
    "ride",
    "rim",
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
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
]


CONTEXT_SUMMARY_FIELDS = [
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
]


SUMMARY_FIELDS = [
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
]


SAMPLE_FIELDS = [
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_expected_rank",
    "partial2",
    "partial3",
    "partial4",
]


def source_key(row: dict[str, str]) -> str:
    source = row.get("source") or row.get("nsynth_family") or "unknown"
    return f"{row.get('family', 'unknown')}/{source}"


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def median_text(rows: list[dict[str, str]], field: str) -> str:
    values = [value for row in rows if (value := as_float(row, field)) is not None]
    if not values:
        return "--"
    return f"{statistics.median(values):.3f}"


def compact_counter(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def expected_pitch_class(row: dict[str, str]) -> str:
    match = re.fullmatch(r"([A-G]#?)-?\d+", row.get("expected_note", ""))
    if match:
        return match.group(1)
    return row.get("expected_note", "--") or "--"


def expected_octave(row: dict[str, str]) -> str:
    try:
        midi = int(row.get("expected_midi", ""))
    except ValueError:
        return "--"
    return str(midi // 12 - 1)


def note_range(samples: dict[str, dict[str, str]]) -> str:
    midis = []
    for row in samples.values():
        try:
            midis.append(int(row["expected_midi"]))
        except (KeyError, ValueError):
            pass
    if not midis:
        return "--"
    return f"{min(midis)}-{max(midis)}"


def median_parts(rows: list[dict[str, str]], fields: list[str]) -> str:
    return " ".join(f"{field}={median_text(rows, field)}" for field in fields)


def debug_rows_for_sample_ids(
    rows_by_sample: dict[str, list[dict[str, str]]], sample_ids: set[str]
) -> list[dict[str, str]]:
    debug_rows = []
    for sample_id in sample_ids:
        debug_rows.extend(row for row in rows_by_sample.get(sample_id, []) if row.get("debug_note"))
    return debug_rows


def unique_context_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row.get("sample_id", ""), row.get("buffer", ""))
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
    return selected


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader)


def append_detailed_breakdown(
    lines: list[str],
    rows: list[dict[str, str]],
    samples: dict[str, dict[str, str]],
    detail_limit: int,
    sample_limit: int,
) -> None:
    if detail_limit <= 0 and sample_limit <= 0:
        return

    rows_by_sample: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        rows_by_sample[row.get("sample_id", "")].append(row)

    if detail_limit > 0:
        samples_by_source: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
        for sample in samples.values():
            samples_by_source[source_key(sample)].append(sample)

        lines.append("source detail")
        for source, source_samples in sorted(samples_by_source.items()):
            source_sample_map = {row.get("sample_id", ""): row for row in source_samples}
            source_debug_rows = debug_rows_for_sample_ids(
                rows_by_sample, set(source_sample_map.keys())
            )
            status = collections.Counter(row.get("status", "unknown") for row in source_samples)
            first_rows = collections.Counter(row.get("first_row", "none") for row in source_samples)
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in source_debug_rows if row.get("debug_owner")
            )
            lines.append(
                f"  {source} samples={len(source_samples)} midi={note_range(source_sample_map)} "
                f"status={compact_counter(status)} first_rows={compact_counter(first_rows)} "
                f"debug_owners={compact_counter(owners)} {median_parts(source_debug_rows, SAMPLE_FIELDS)}"
            )

        pitch_bucket_ids: dict[tuple[str, str, str, str, str], set[str]] = collections.defaultdict(set)
        octave_bucket_ids: dict[tuple[str, str, str, str], set[str]] = collections.defaultdict(set)
        for sample_id, sample in samples.items():
            status = sample.get("status", "unknown")
            if status == "hit":
                continue
            source = source_key(sample)
            first_row = sample.get("first_row", "none")
            pitch_bucket_ids[
                (status, source, expected_pitch_class(sample), expected_octave(sample), first_row)
            ].add(sample_id)
            octave_bucket_ids[(status, source, expected_octave(sample), first_row)].add(sample_id)

        lines.append("non-hit pitch buckets")
        for (status, source, pitch_class, octave, first_row), sample_ids in sorted(
            pitch_bucket_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )[:detail_limit]:
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, sample_ids)
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            debug_notes = collections.Counter(
                row.get("debug_note", "none") for row in debug_rows if row.get("debug_note")
            )
            lines.append(
                f"  {status}:{source} note={pitch_class}{octave}->"
                f"{first_row} samples={len(sample_ids)} debug_owners={compact_counter(owners)} "
                f"debug_notes={compact_counter(debug_notes, 5)} {median_parts(debug_rows, SAMPLE_FIELDS)}"
            )

        lines.append("non-hit octave buckets")
        for (status, source, octave, first_row), sample_ids in sorted(
            octave_bucket_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )[:detail_limit]:
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, sample_ids)
            expected_notes = collections.Counter(
                samples[sample_id].get("expected_note", "--") for sample_id in sample_ids
            )
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            lines.append(
                f"  {status}:{source} octave={octave}->{first_row} samples={len(sample_ids)} "
                f"expected={compact_counter(expected_notes, 6)} debug_owners={compact_counter(owners)} "
                f"{median_parts(debug_rows, SAMPLE_FIELDS)}"
            )

    if sample_limit > 0:
        non_hit_samples = [
            sample for sample in samples.values() if sample.get("status", "hit") != "hit"
        ]
        non_hit_samples.sort(
            key=lambda row: (
                row.get("status", ""),
                source_key(row),
                int(row.get("expected_midi", "0") or "0"),
                row.get("sample_id", ""),
            )
        )
        lines.append("non-hit sample attributes")
        for sample in non_hit_samples[:sample_limit]:
            sample_id = sample.get("sample_id", "")
            debug_rows = debug_rows_for_sample_ids(rows_by_sample, {sample_id})
            owners = collections.Counter(
                row.get("debug_owner", "none") for row in debug_rows if row.get("debug_owner")
            )
            debug_notes = collections.Counter(
                row.get("debug_note", "none") for row in debug_rows if row.get("debug_note")
            )
            strongest = collections.Counter(
                row.get("buffer_strongest_row", "none")
                for row in rows_by_sample.get(sample_id, [])
                if row.get("buffer_strongest_row")
            )
            lines.append(
                f"  {sample_id} status={sample.get('status', '')} source={source_key(sample)} "
                f"expected={sample.get('expected_note', '')}/{sample.get('expected_midi', '')} "
                f"first_row={sample.get('first_row', '')} strongest={compact_counter(strongest, 4)} "
                f"debug_owners={compact_counter(owners, 4)} debug_notes={compact_counter(debug_notes, 5)} "
                f"{median_parts(debug_rows, SAMPLE_FIELDS)}"
            )


def summarize(path: pathlib.Path, detail_limit: int = 0, sample_limit: int = 0) -> list[str]:
    rows = load_rows(path)
    samples: dict[str, dict[str, str]] = {}
    for row in rows:
        samples.setdefault(row["sample_id"], row)

    status_counts = collections.Counter(row["status"] for row in samples.values())
    group_counts = collections.Counter(
        (row["status"], source_key(row), row.get("first_row", "none")) for row in samples.values()
    )
    source_counts = collections.Counter(source_key(row) for row in samples.values())

    lines = [
        f"summarize_real_note_attributes: rows {len(rows)} samples {len(samples)} note-midi-range {note_range(samples)}",
        "sample status " + " ".join(f"{key}={value}" for key, value in status_counts.most_common()),
        "sample sources " + " ".join(f"{key}={value}" for key, value in source_counts.most_common(10)),
    ]

    if group_counts:
        non_hit_groups = [
            (key, count) for key, count in group_counts.most_common() if key[0] != "hit"
        ]
        if non_hit_groups:
            lines.append(
                "top non-hit status/source/first-row "
                + " ".join(
                    f"{status}:{source}->{row_name}={count}"
                    for (status, source, row_name), count in non_hit_groups[:12]
                )
            )
        lines.append(
            "top hit status/source/first-row "
            + " ".join(
                f"{status}:{source}->{row_name}={count}"
                for (status, source, row_name), count in group_counts.most_common(12)
                if status == "hit"
            )
        )

    rows_by_group: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        if not row.get("debug_note"):
            continue
        rows_by_group[(row["status"], source_key(row), row.get("first_row", "none"))].append(row)

    context_rows_by_group: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in unique_context_rows(rows):
        context_rows_by_group[(row["status"], source_key(row), row.get("first_row", "none"))].append(row)

    median_keys = [key for key, _count in group_counts.most_common() if key[0] != "hit"][:8]
    median_keys += [key for key, _count in group_counts.most_common() if key[0] == "hit"][:5]
    seen_median_keys = set()
    for key in median_keys:
        if key in seen_median_keys:
            continue
        seen_median_keys.add(key)
        count = group_counts[key]
        debug_rows = rows_by_group.get(key, [])
        status, source, row_name = key
        if debug_rows:
            parts = [f"{field}={median_text(debug_rows, field)}" for field in SUMMARY_FIELDS]
            lines.append(
                f"debug medians {status}:{source}->{row_name} samples={count} debug_rows={len(debug_rows)} "
                + " ".join(parts)
            )
        context_rows = context_rows_by_group.get(key, [])
        if context_rows:
            context_parts = [f"{field}={median_text(context_rows, field)}" for field in CONTEXT_SUMMARY_FIELDS]
            lines.append(
                f"context medians {status}:{source}->{row_name} samples={count} "
                f"buffers={len(context_rows)} " + " ".join(context_parts)
            )

    append_detailed_breakdown(lines, rows, samples, detail_limit, sample_limit)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=0,
        help="print this many non-hit pitch and octave buckets plus per-source attribute summaries",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=0,
        help="print this many individual non-hit sample attribute summaries",
    )
    args = parser.parse_args()

    for line in summarize(
        pathlib.Path(args.path),
        detail_limit=max(0, args.detail_limit),
        sample_limit=max(0, args.sample_limit),
    ):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
