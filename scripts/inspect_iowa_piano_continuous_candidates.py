#!/usr/bin/env python3
"""List sustained Iowa piano files suitable for continuous ownership controls."""

from __future__ import annotations

import csv
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "build" / "iowa_piano_samples"
TARGET_MIDIS = {48, 52, 55, 60, 64, 67}


def duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as source:
        return source.getnframes() / source.getframerate()


def main() -> int:
    manifest = FIXTURE_ROOT / "manifest.tsv"
    if not manifest.is_file():
        raise SystemExit(f"missing Iowa piano manifest: {manifest}")
    rows: list[tuple[int, str, Path, float]] = []
    with manifest.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            midi = int(row["midi"])
            if midi not in TARGET_MIDIS:
                continue
            path = FIXTURE_ROOT / row["path"]
            if not path.is_file():
                continue
            duration = duration_seconds(path)
            if duration >= 2.0:
                rows.append((midi, row["id"], path, duration))
    print(f"fixture-root={FIXTURE_ROOT.resolve()}")
    print("midi\tid\tduration\tpath")
    for midi, sample_id, path, duration in rows:
        print(f"{midi}\t{sample_id}\t{duration:.3f}\t{path}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
