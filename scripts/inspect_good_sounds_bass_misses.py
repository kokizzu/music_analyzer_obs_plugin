#!/usr/bin/env python3
"""Inspect Good Sounds full-mix bass samples that miss their expected row.

This is deliberately sample-level: a detector change acts on consecutive audio
buffers, whereas the benchmark score counts a sample as recovered if any buffer
lights its expected row.  The output distinguishes pitches that cannot reach the
current upper-bass path from those that already can but lose ownership later.
"""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import statistics
import sys


DEFAULT_BASS_MAX_MIDI = 52
CLEAN_UPPER_BASS_MAX_MIDI = 64


def as_int(row: dict[str, str], field: str) -> int | None:
    try:
        return int(row.get(field, ""))
    except ValueError:
        return None


def as_float(row: dict[str, str], field: str) -> float | None:
    try:
        return float(row.get(field, ""))
    except ValueError:
        return None


def fraction(count: int, total: int) -> str:
    percent = count * 100.0 / total if total else 0.0
    return f"{count}/{total} ({percent:.1f}%)"


def compact_counter(counter: collections.Counter[str], limit: int = 3) -> str:
    return ",".join(f"{key}:{count}" for key, count in counter.most_common(limit)) or "--"


def sample_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        sample_id = row.get("sample_id", "")
        if sample_id:
            grouped[sample_id].append(row)
    return grouped


def print_report(rows: list[dict[str, str]], limit: int) -> None:
    grouped = sample_rows(rows)
    bass_samples = {
        sample_id: sample
        for sample_id, sample in grouped.items()
        if sample[0].get("family") == "bass"
    }
    misses = {
        sample_id: sample
        for sample_id, sample in bass_samples.items()
        if sample[0].get("detected_expected_row") != "1"
    }
    print(
        "Good Sounds bass expected-row misses: "
        f"{fraction(len(misses), len(bass_samples))}"
    )
    if not misses:
        return

    bands = collections.Counter()
    status = collections.Counter()
    for sample in misses.values():
        first = sample[0]
        midi = as_int(first, "expected_midi")
        status[first.get("status", "unknown")] += 1
        if midi is None:
            bands["missing MIDI"] += 1
        elif midi <= DEFAULT_BASS_MAX_MIDI:
            bands[f"default range <= {DEFAULT_BASS_MAX_MIDI}"] += 1
        elif midi <= CLEAN_UPPER_BASS_MAX_MIDI:
            bands[f"current upper-recovery {DEFAULT_BASS_MAX_MIDI + 1}-{CLEAN_UPPER_BASS_MAX_MIDI}"] += 1
        else:
            bands[f"above current recovery > {CLEAN_UPPER_BASS_MAX_MIDI}"] += 1

    print("status: " + compact_counter(status, 8))
    print("pitch band:")
    for band in (
        f"default range <= {DEFAULT_BASS_MAX_MIDI}",
        f"current upper-recovery {DEFAULT_BASS_MAX_MIDI + 1}-{CLEAN_UPPER_BASS_MAX_MIDI}",
        f"above current recovery > {CLEAN_UPPER_BASS_MAX_MIDI}",
        "missing MIDI",
    ):
        if band in bands:
            print(f"  {band}: {fraction(bands[band], len(misses))}")

    print(
        "sample_id\texpected\tstatus\tbuffers\texpected-buffers\t"
        "debug-exact\traw-expected-median\tfirst-rows\tdebug-owners"
    )
    samples = sorted(
        misses.items(),
        key=lambda item: (as_int(item[1][0], "expected_midi") or -1, item[0]),
    )
    for sample_id, sample in samples[:limit]:
        first = sample[0]
        expected_midi = as_int(first, "expected_midi")
        expected_buffers = sum(row.get("detected_expected_row") == "1" for row in sample)
        debug_exact = sum(as_int(row, "debug_midi") == expected_midi for row in sample)
        ratios = [value for row in sample if (value := as_float(row, "raw_expected_ratio")) is not None]
        median_ratio = statistics.median(ratios) if ratios else 0.0
        first_rows = collections.Counter(row.get("first_row", "--") or "--" for row in sample)
        owners = collections.Counter(row.get("debug_owner", "--") or "--" for row in sample)
        print(
            f"{sample_id}\t{first.get('expected_note', '--')} ({expected_midi})\t"
            f"{first.get('status', '--')}\t{len(sample)}\t{expected_buffers}\t{debug_exact}\t"
            f"{median_ratio:.3f}\t{compact_counter(first_rows)}\t{compact_counter(owners)}"
        )
    if len(samples) > limit:
        print(f"... {len(samples) - limit} more samples; pass --limit {len(samples)} to show all")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=pathlib.Path, help="Good Sounds full-mix attribute TSV")
    parser.add_argument("--limit", type=int, default=32, help="maximum miss samples to print")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    try:
        with args.input.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
    except OSError as exc:
        print(f"could not read {args.input}: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print(f"no rows in {args.input}", file=sys.stderr)
        return 2
    print_report(rows, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
