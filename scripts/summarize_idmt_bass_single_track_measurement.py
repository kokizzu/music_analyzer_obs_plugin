#!/usr/bin/env python3
"""Summarize compact-IDMT bass recall from exported real-note attributes."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "build/idmt_bass_single_track_fixture"
ATTRIBUTES = ROOT / "build/idmt_bass_single_track_attributes.tsv"
MEASUREMENT = ROOT / "build/idmt_bass_single_track_measurement.out"


def percent(numerator: int, denominator: int) -> str:
    return f"{(100.0 * numerator / denominator) if denominator else 0.0:.1f}%"


def main() -> int:
    if not ATTRIBUTES.is_file() or not MEASUREMENT.is_file():
        raise SystemExit("missing IDMT bass measurement; run make measure-idmt-bass-single-track")
    styles: dict[str, str] = {}
    for row in csv.DictReader((FIXTURE / "metadata.tsv").open(encoding="utf-8"), delimiter="\t"):
        styles[row["id"]] = row["excitation"]
    rows = list(csv.DictReader(ATTRIBUTES.open(encoding="utf-8"), delimiter="\t"))
    if not rows:
        raise SystemExit("IDMT bass attribute export is empty")
    id_key = next((key for key in ("id", "sample_id") if key in rows[0]), None)
    if id_key is None:
        raise SystemExit("IDMT bass attributes have no sample-id field: " + ", ".join(rows[0]))
    midi_key = next((key for key in ("midi", "expected_midi") if key in rows[0]), None)
    if midi_key is None:
        raise SystemExit("IDMT bass attributes have no MIDI field: " + ", ".join(rows[0]))
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        by_id.setdefault(row[id_key], row)
    hits_by_style: Counter[str] = Counter()
    total_by_style: Counter[str] = Counter()
    hits_by_octave: Counter[int] = Counter()
    total_by_octave: Counter[int] = Counter()
    status_counts: Counter[str] = Counter()
    misses: list[dict[str, str]] = []
    miss_windows: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "hit":
            miss_windows[row[id_key]].append(row)
    for sample_id, row in sorted(by_id.items()):
        status = row.get("status", "unknown")
        status_counts[status] += 1
        style = styles.get(sample_id, "unknown")
        total_by_style[style] += 1
        midi = int(row[midi_key])
        octave = midi // 12 - 1
        total_by_octave[octave] += 1
        if status == "hit":
            hits_by_style[style] += 1
            hits_by_octave[octave] += 1
        else:
            misses.append(row)
    hits = status_counts["hit"]
    total = len(by_id)
    measurement_lines = [line for line in MEASUREMENT.read_text(encoding="utf-8").splitlines()
                         if line.startswith("analyzer_real_note_samples")]
    if measurement_lines:
        print(measurement_lines[-1])
    print(f"unique clips: {total}; hit={hits} ({percent(hits, total)})")
    print(f"status: {dict(sorted(status_counts.items()))}")
    print("recall by plucking style:")
    for style in sorted(total_by_style):
        print(f"  {style}: {hits_by_style[style]}/{total_by_style[style]} ({percent(hits_by_style[style], total_by_style[style])})")
    print("recall by octave:")
    for octave in sorted(total_by_octave):
        print(f"  {octave}: {hits_by_octave[octave]}/{total_by_octave[octave]} ({percent(hits_by_octave[octave], total_by_octave[octave])})")
    print("attribute fields: " + ", ".join(rows[0]))
    print("representative misses:")
    for row in misses[:16]:
        sample_id = row.get(id_key, "")
        style = styles.get(sample_id, "unknown")
        details = " ".join(
            f"{key}={row[key]}" for key in (
                "sample_id", "expected_midi", "buffer", "first_row", "raw_expected_ratio", "raw_tuned_ratio",
                "raw_tuned_cent_offset", "raw_expected_rank") if key in row)
        print(f"  style={style} {details}")
    if miss_windows:
        tune_outside = 0
        strong_wrong_rank = 0
        per_recording: Counter[str] = Counter()
        for sample_id, windows in miss_windows.items():
            min_cents = min(float(row["raw_tuned_abs_cent_offset"]) for row in windows)
            best_rank = min(int(row["raw_expected_rank"]) for row in windows)
            if min_cents > 9.0:
                tune_outside += 1
            if min_cents <= 9.0 and best_rank <= 3:
                strong_wrong_rank += 1
            per_recording[sample_id.split("_")[2]] += 1
        print("miss groups:")
        print(f"  all analysis windows outside +/-9 cents: {tune_outside}/{len(miss_windows)}")
        print(f"  within +/-9 cents with expected rank <=3: {strong_wrong_rank}/{len(miss_windows)}")
        print("  misses by recording: " + ", ".join(
            f"{recording}={count}" for recording, count in sorted(per_recording.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
