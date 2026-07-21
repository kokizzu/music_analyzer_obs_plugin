#!/usr/bin/env python3
"""Summarize real-note per-buffer detector attribute TSV exports."""

from __future__ import annotations

import collections
import csv
import pathlib
import statistics
import sys


NUMERIC_FIELDS = [
    "row_conf",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
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


SUMMARY_FIELDS = [
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "fit_error",
    "noise",
    "partial1",
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


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader)


def summarize(path: pathlib.Path) -> list[str]:
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

    median_keys = [key for key, _count in group_counts.most_common() if key[0] != "hit"][:8]
    median_keys += [key for key, _count in group_counts.most_common() if key[0] == "hit"][:5]
    seen_median_keys = set()
    for key in median_keys:
        if key in seen_median_keys:
            continue
        seen_median_keys.add(key)
        count = group_counts[key]
        debug_rows = rows_by_group.get(key, [])
        if not debug_rows:
            continue
        status, source, row_name = key
        parts = [f"{field}={median_text(debug_rows, field)}" for field in SUMMARY_FIELDS]
        lines.append(
            f"debug medians {status}:{source}->{row_name} samples={count} debug_rows={len(debug_rows)} "
            + " ".join(parts)
        )

    return lines


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/real_note_full_mix_attributes.tsv")
    for line in summarize(path):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
