#!/usr/bin/env python3
"""Measure the optional MIT beat tracker on a MAESTRO-compatible BPM fixture."""
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


def bpm_from_midi(path: Path) -> float:
    data = path.read_bytes()
    marker = data.find(b"\xff\x51\x03")
    if marker < 0 or marker + 6 > len(data):
        raise ValueError(f"missing MIDI tempo: {path}")
    return 60_000_000.0 / int.from_bytes(data[marker + 3:marker + 6], "big")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--metadata", default="maestro-v3.0.0.csv")
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--min-tempo", type=float, default=40.0)
    parser.add_argument("--max-tempo", type=float, default=240.0)
    parser.add_argument("--start-index", type=int, default=0,
                        help="zero-based metadata row offset for resumable measurements")
    parser.add_argument("--limit", type=int,
                        help="maximum metadata rows to measure after --start-index")
    args = parser.parse_args()
    if args.min_tempo <= 0.0 or args.max_tempo <= args.min_tempo:
        parser.error("--min-tempo must be positive and below --max-tempo")
    if args.start_index < 0 or args.limit is not None and args.limit <= 0:
        parser.error("--start-index must be non-negative and --limit must be positive")
    with (args.root / args.metadata).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = rows[args.start_index:]
    if args.limit is not None:
        rows = rows[:args.limit]
    for index, row in enumerate(rows, args.start_index + 1):
        audio = args.root / row["audio_filename"]
        expected = float(row["bpm"]) if row.get("bpm") else bpm_from_midi(args.root / row["midi_filename"])
        offset = float(row.get("tempo_audio_offset_seconds", "0") or 0)
        result = subprocess.run([str(args.probe), str(audio), str(offset), str(args.seconds),
                                 str(args.min_tempo), str(args.max_tempo)],
                                check=True, text=True, capture_output=True)
        fields = dict(part.split("=", 1) for part in result.stdout.strip().split("\t") if "=" in part)
        raw = float(fields["raw"])
        confidence = float(fields["confidence"])
        error = abs(raw - expected)
        print(f"BTT tempo diag\tid={index}\texpected={expected:.2f}\traw={raw:.2f}\tconfidence={confidence:.3f}\tmin_tempo={args.min_tempo:.2f}\tmax_tempo={args.max_tempo:.2f}\terror={error:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
