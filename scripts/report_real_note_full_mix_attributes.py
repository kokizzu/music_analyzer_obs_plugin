#!/usr/bin/env python3
"""Export historic full-mix attributes and audit candidate routing profiles."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "build" / "real_note_samples"
SHARD_COUNT = 8


def output_path(index: int) -> Path:
    return ROOT / "build" / f"real_note_full_mix_attributes_{index}.tsv"


def run_shard(index: int) -> None:
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=str(SAMPLE_ROOT),
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=str(SHARD_COUNT),
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=str(index),
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(output_path(index)),
    )
    subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                   env=environment, check=True, stdout=subprocess.DEVNULL)


def read_rows() -> list[dict[str, str]]:
    by_sample: dict[str, dict[str, str]] = {}
    for index in range(SHARD_COUNT):
        with output_path(index).open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                by_sample.setdefault(row["sample_id"], row)
    return list(by_sample.values())


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, ValueError):
        return 0.0


def is_pure_upper_flute_shape(row: dict[str, str]) -> bool:
    try:
        midi = int(row["debug_midi"])
    except (KeyError, ValueError):
        return False
    return (
        84 <= midi <= 94 and
        number(row, "spectral_level") >= 0.90 and
        number(row, "pitch_confidence") >= 0.90 and
        0.68 <= number(row, "periodicity") <= 0.76 and
        number(row, "fit_error") <= 0.060 and
        number(row, "noise") <= 0.035 and
        number(row, "centroid") <= 0.065 and
        number(row, "slope") <= 0.050 and
        number(row, "partial2") <= 0.070 and
        number(row, "partial3") <= 0.055 and
        number(row, "partial4") <= 0.005 and
        number(row, "partial5") <= 0.005
    )


def is_muted_plucked_guitar_shape(row: dict[str, str]) -> bool:
    try:
        midi = int(row["debug_midi"])
    except (KeyError, ValueError):
        return False
    return (
        45 <= midi <= 67 and
        0.84 <= number(row, "pitch_confidence") <= 0.95 and
        0.68 <= number(row, "periodicity") <= 0.82 and
        number(row, "fit_error") <= 0.10 and
        0.04 <= number(row, "noise") <= 0.19 and
        0.04 <= number(row, "centroid") <= 0.13 and
        0.008 <= number(row, "slope") <= 0.11 and
        0.08 <= number(row, "partial2") <= 0.28 and
        0.005 <= number(row, "partial3") <= 0.065 and
        number(row, "partial4") <= 0.035 and
        number(row, "partial5") <= 0.025
    )


def print_counter(label: str, values: Counter[str]) -> None:
    print(label + "=" + " ".join(f"{name}={count}" for name, count in values.most_common()))


def main() -> None:
    if not (SAMPLE_ROOT / "manifest.tsv").is_file():
        raise SystemExit("missing historic fixtures; run make setup-real-note-samples first")
    reuse = "--reuse" in sys.argv[1:]
    if reuse and not all(output_path(index).is_file() for index in range(SHARD_COUNT)):
        raise SystemExit("missing historic attribute exports; run make report-real-note-full-mix-attributes first")
    if not reuse:
        with ThreadPoolExecutor(max_workers=SHARD_COUNT) as executor:
            list(executor.map(run_shard, range(SHARD_COUNT)))
    rows = read_rows()
    matches = [row for row in rows if is_pure_upper_flute_shape(row)]
    print(f"fixtures={len(rows)} pure-upper-flute-shape={len(matches)}")
    print_counter("families", Counter(row["family"] for row in matches))
    print_counter("sources", Counter(f"{row['family']}/{row['source']}" for row in matches))
    print_counter("owners", Counter(row["debug_owner"] or "none" for row in matches))
    print_counter("visual-routes", Counter(row["visual_first_row"] for row in matches))
    print("examples:")
    for row in sorted(matches, key=lambda item: (item["family"], item["source"], item["sample_id"]))[:50]:
        print(
            f"  {row['sample_id']} family={row['family']} source={row['source']} "
            f"expected={row['expected_note']} debug={row['debug_note']} owner={row['debug_owner']} "
            f"visual={row['visual_first_row']} period={number(row, 'periodicity'):.3f} "
            f"centroid={number(row, 'centroid'):.3f} slope={number(row, 'slope'):.3f} "
            f"p2={number(row, 'partial2'):.3f} p3={number(row, 'partial3'):.3f}"
        )

    muted_matches = [row for row in rows if is_muted_plucked_guitar_shape(row)]
    print(f"muted-plucked-guitar-shape={len(muted_matches)}")
    print_counter("muted-families", Counter(row["family"] for row in muted_matches))
    print_counter("muted-sources", Counter(f"{row['family']}/{row['source']}" for row in muted_matches))
    print_counter("muted-owners", Counter(row["debug_owner"] or "none" for row in muted_matches))
    print_counter("muted-visual-routes", Counter(row["visual_first_row"] for row in muted_matches))

    guitar_raw = [
        row for row in rows
        if row["family"] == "guitar" and row["first_row"] == "guitar"
    ]
    guitar_visual_misses = [
        row for row in guitar_raw if row["visual_first_row"] != "guitar"
    ]
    print(
        f"guitar-raw-visual-gap={len(guitar_visual_misses)}/{len(guitar_raw)}"
    )
    print_counter(
        "guitar-gap-sources",
        Counter(f"{row['family']}/{row['source']}" for row in guitar_visual_misses),
    )
    print_counter(
        "guitar-gap-owners",
        Counter(row["debug_owner"] or "none" for row in guitar_visual_misses),
    )
    print_counter(
        "guitar-gap-visual-routes",
        Counter(row["visual_first_row"] for row in guitar_visual_misses),
    )
    print("guitar-gap-examples:")
    for row in sorted(guitar_visual_misses, key=lambda item: (item["source"], item["sample_id"]))[:50]:
        print(
            f"  {row['sample_id']} source={row['source']} expected={row['expected_note']} "
            f"debug={row['debug_note']} owner={row['debug_owner']} "
            f"conf={number(row, 'debug_conf'):.3f} visual={row['visual_first_row']} "
            f"keyboard={number(row, 'keyboard_score'):.3f} guitar={number(row, 'guitar_score'):.3f} "
            f"vocal={number(row, 'vocal_score'):.3f} other={number(row, 'other_score'):.3f} "
            f"level={number(row, 'spectral_level'):.3f} period={number(row, 'periodicity'):.3f} "
            f"p2={number(row, 'partial2'):.3f} p3={number(row, 'partial3'):.3f}"
        )


if __name__ == "__main__":
    main()
