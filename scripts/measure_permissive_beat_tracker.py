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
    parser.add_argument("--seconds", type=float, default=20.0)
    args = parser.parse_args()
    with (args.root / "maestro-v3.0.0.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for index, row in enumerate(rows, 1):
        audio = args.root / row["audio_filename"]
        expected = bpm_from_midi(args.root / row["midi_filename"])
        offset = float(row.get("tempo_audio_offset_seconds", "0") or 0)
        result = subprocess.run([str(args.probe), str(audio), str(offset), str(args.seconds)],
                                check=True, text=True, capture_output=True)
        fields = dict(part.split("=", 1) for part in result.stdout.strip().split("\t") if "=" in part)
        raw = float(fields["raw"])
        confidence = float(fields["confidence"])
        error = abs(raw - expected)
        print(f"BTT tempo diag\tid={index}\texpected={expected:.2f}\traw={raw:.2f}\tconfidence={confidence:.3f}\terror={error:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
