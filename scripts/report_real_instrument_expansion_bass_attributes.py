#!/usr/bin/env python3
"""Measure physical-bass ownership evidence from the expansion corpus."""

from __future__ import annotations

import csv
import os
import statistics
import subprocess
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "build" / "real_instrument_expansion_samples"
SHARD_COUNT = 4
NUMERIC_FIELDS = (
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "bass_visual_level",
    "piano_visual_level",
    "guitar_visual_level",
    "bass_spectral_confidence",
    "bass_displayed_confidence",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "onset_strength",
    "decay_rate",
    "pitch_stability",
    "simultaneous_onset",
    "harmonic_product_score",
    "lower_subharmonic_product_ratio",
    "adjacent_lower_ratio",
    "adjacent_upper_ratio",
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "raw_expected_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
    "raw_second_octave_up_ratio",
)


def output_path(family: str, index: int) -> Path:
    return ROOT / "build" / f"real_instrument_expansion_{family}_attributes_{index}.tsv"


def run_shard(family: str, index: int) -> None:
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=str(SAMPLE_ROOT),
        MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER=family,
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=str(SHARD_COUNT),
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=str(index),
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(output_path(family, index)),
    )
    subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                   env=environment, check=True, stdout=subprocess.DEVNULL)


def read_rows(family: str) -> list[dict[str, str]]:
    by_sample: dict[str, dict[str, str]] = {}
    for index in range(SHARD_COUNT):
        with output_path(family, index).open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                by_sample.setdefault(row["sample_id"], row)
    return list(by_sample.values())


def median(rows: list[dict[str, str]], field: str) -> str:
    values = [float(row[field]) for row in rows if field in row and row[field]]
    return f"{statistics.median(values):.3f}" if values else "n/a"


def number(row: dict[str, str], field: str) -> str:
    value = row.get(field)
    return f"{float(value):.3f}" if value else "n/a"


def print_group(name: str, rows: list[dict[str, str]]) -> None:
    print(f"{name}=count:{len(rows)} " + " ".join(
        f"{field.removeprefix('bass_debug_')}:{median(rows, field)}" for field in NUMERIC_FIELDS
    ))


def print_octave_offset_groups(family: str, rows: list[dict[str, str]]) -> None:
    groups: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        try:
            delta = int(row["debug_midi"]) - int(row["expected_midi"])
        except (KeyError, ValueError):
            continue
        groups.setdefault(delta, []).append(row)
    print("debug-midi-offsets:")
    for delta, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        routes = Counter(row["first_row"] for row in group)
        visual_routes = Counter(row["visual_first_row"] for row in group)
        print(
            f"  {delta:+d}=count:{len(group)} raw="
            + " ".join(f"{name}={count}" for name, count in routes.most_common())
            + " visual="
            + " ".join(f"{name}={count}" for name, count in visual_routes.most_common())
        )
        print_group(f"  {family}-offset-{delta:+d}", group)


def print_expected_row_by_source(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["source"], []).append(row)
    print("expected-row-by-source:")
    for source, group in sorted(grouped.items()):
        hits = sum(row["detected_expected_row"] == "1" for row in group)
        print(f"  {source}={hits}/{len(group)} ({100 * hits // len(group)}%)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("bass", "guitar", "piano", "other"), default="bass")
    parser.add_argument("--source", help="restrict the final diagnostic report to one manifest source")
    arguments = parser.parse_args()
    family = arguments.family
    if not (SAMPLE_ROOT / "manifest.tsv").is_file():
        raise SystemExit("missing expansion manifest; run make apply-real-instrument-expansion-fixtures first")
    with ThreadPoolExecutor(max_workers=SHARD_COUNT) as executor:
        list(executor.map(lambda index: run_shard(family, index), range(SHARD_COUNT)))
    rows = read_rows(family)
    if arguments.source:
        rows = [row for row in rows if row["source"] == arguments.source]
        if not rows:
            raise SystemExit(f"no {family} fixtures found for source {arguments.source!r}")
    print("fields=" + ",".join(sorted(rows[0])) if rows else "fields=[none]")
    raw = Counter(row["first_row"] for row in rows)
    visual = Counter(row["visual_first_row"] for row in rows)
    print(f"fixtures={len(rows)} raw=" + " ".join(f"{name}={count}" for name, count in raw.most_common()))
    print("visual=" + " ".join(f"{name}={count}" for name, count in visual.most_common()))
    print_group(f"raw-{family}", [row for row in rows if row["first_row"] == family])
    print_group("raw-piano", [row for row in rows if row["first_row"] == "piano"])
    print_group(
        "expected-row-hit",
        [row for row in rows if row["detected_expected_row"] == "1"],
    )
    print_group(
        "expected-row-miss",
        [row for row in rows if row["detected_expected_row"] != "1"],
    )
    print_octave_offset_groups(family, rows)
    print_expected_row_by_source(rows)
    for label, predicate in (("low", lambda midi: midi <= 40), ("upper", lambda midi: midi >= 41)):
        subset = [row for row in rows if predicate(int(row["expected_midi"]))]
        routes = Counter(row["first_row"] for row in subset)
        print(f"range-{label}=count:{len(subset)} " + " ".join(
            f"{name}={count}" for name, count in routes.most_common()
        ))
    print("expected-row-miss-examples:")
    misses = sorted(
        (row for row in rows if row["detected_expected_row"] != "1"),
        key=lambda row: (row["source"], int(row["expected_midi"]), row["sample_id"]),
    )
    for row in misses[:30]:
        print(
            f"  {row['sample_id']} note={row['expected_note']} debug={row['debug_note']} "
            f"owner={row['debug_owner']} "
            f"conf={number(row, 'debug_conf')} bass={number(row, 'bass_score')} "
            f"piano={number(row, 'keyboard_score')} guitar={number(row, 'guitar_score')} "
            f"vocal={number(row, 'vocal_score')} other={number(row, 'other_score')} "
            f"spectral_bass={row.get('bass_spectral_midi', 'n/a')} "
            f"displayed_bass={row.get('bass_displayed_midi', 'n/a')} "
            f"level={number(row, 'spectral_level')} pitch={number(row, 'pitch_confidence')} "
            f"period={number(row, 'periodicity')} centroid={number(row, 'centroid')} "
            f"slope={number(row, 'slope')} noise={number(row, 'noise')} "
            f"p2={number(row, 'partial2')} p3={number(row, 'partial3')} "
            f"p4={number(row, 'partial4')} p5={number(row, 'partial5')}"
        )


if __name__ == "__main__":
    main()
