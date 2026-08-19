#!/usr/bin/env python3
"""Measure BTT across BPM ranges on one annotated tempo fixture.

This remains an offline calibration tool.  It deliberately uses the same
probe and metadata convention as measure_permissive_beat_tracker.py, but
keeps every range result in one deterministic log so high-tempo behaviour can
be compared without enabling another live tracker.
"""
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


def parse_min_tempos(value: str) -> list[float]:
    try:
        result = [float(item) for item in value.split(",") if item]
    except ValueError as error:
        raise argparse.ArgumentTypeError("--min-tempos must be comma-separated numbers") from error
    if not result or any(item <= 0.0 for item in result) or len(set(result)) != len(result):
        raise argparse.ArgumentTypeError("--min-tempos must be unique positive numbers")
    return result


def fields(line: str) -> dict[str, str]:
    return dict(part.split("=", 1) for part in line.strip().split("\t") if "=" in part)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--metadata", default="maestro-v3.0.0.csv")
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--min-tempos", type=parse_min_tempos, required=True)
    parser.add_argument("--max-tempo", type=float, default=240.0)
    args = parser.parse_args()
    if args.seconds <= 0.0 or args.max_tempo <= 0.0:
        parser.error("--seconds and --max-tempo must be positive")
    if any(min_tempo >= args.max_tempo for min_tempo in args.min_tempos):
        parser.error("each --min-tempos value must be below --max-tempo")

    with (args.root / args.metadata).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for min_tempo in args.min_tempos:
        for index, row in enumerate(rows, 1):
            audio = args.root / row["audio_filename"]
            expected = float(row["bpm"]) if row.get("bpm") else bpm_from_midi(args.root / row["midi_filename"])
            offset = float(row.get("tempo_audio_offset_seconds", "0") or 0)
            result = subprocess.run(
                [str(args.probe), str(audio), str(offset), str(args.seconds), str(min_tempo), str(args.max_tempo)],
                check=True,
                text=True,
                capture_output=True,
            )
            probe = fields(result.stdout)
            raw = float(probe["raw"])
            confidence = float(probe["confidence"])
            print(
                "BTT range sweep"
                f"\tid={index}\texpected={expected:.2f}\traw={raw:.2f}\tconfidence={confidence:.3f}"
                f"\tmin_tempo={min_tempo:.2f}\tmax_tempo={args.max_tempo:.2f}"
                f"\terror={abs(raw - expected):.2f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
