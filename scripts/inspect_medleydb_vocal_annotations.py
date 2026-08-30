#!/usr/bin/env python3
"""Report stable chromatic windows from the MedleyDB Rainfall vocal F0 annotation."""

from __future__ import annotations

import csv
import math
import os
import tarfile
from pathlib import Path


CACHE_ROOT = Path(os.environ.get(
    "MUSIC_ANALYZER_FIXTURE_CACHE", "/media/kyz/sshflashtor/InstrumentSamples/build-cache"
))
ARCHIVE = CACHE_ROOT / "medleydb_sample" / "MedleyDB_Sample.tar.gz"
ANNOTATION = "MedleyDB_sample/Annotations/Pitch_Annotations/LizNelson_Rainfall_STEM_01.csv"
MAX_CENTS = 35.0
MIN_DURATION_SECONDS = 0.5


def midi_and_cents(frequency: float) -> tuple[int, float]:
    semitones = 69.0 + 12.0 * math.log2(frequency / 440.0)
    midi = round(semitones)
    return midi, (semitones - midi) * 100.0


def stable_runs() -> list[tuple[int, float, float]]:
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        member = archive.extractfile(ANNOTATION)
        if member is None:
            raise RuntimeError(f"missing annotation {ANNOTATION}")
        rows = [(float(row[0]), float(row[1])) for row in csv.reader(
            (line.decode("utf-8") for line in member), delimiter=",") if len(row) >= 2]
    runs: list[tuple[int, float, float]] = []
    start = 0
    current: int | None = None
    for index, (time, frequency) in enumerate(rows):
        midi, cents = midi_and_cents(frequency) if frequency > 0.0 else (-1, 0.0)
        stable = frequency > 0.0 and abs(cents) <= MAX_CENTS
        if current is None or not stable or midi != current:
            if current is not None and rows[index - 1][0] - rows[start][0] >= MIN_DURATION_SECONDS:
                runs.append((current, rows[start][0], rows[index - 1][0]))
            current = midi if stable else None
            start = index
    if current is not None and rows[-1][0] - rows[start][0] >= MIN_DURATION_SECONDS:
        runs.append((current, rows[start][0], rows[-1][0]))
    return runs


def main() -> int:
    runs = stable_runs()
    print(f"annotation={ANNOTATION}")
    print(f"stable-runs={len(runs)}")
    for midi, start_time, end_time in runs:
        print(f"midi={midi} start={start_time:.3f} end={end_time:.3f} duration={end_time - start_time:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
