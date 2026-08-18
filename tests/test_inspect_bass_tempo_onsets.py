#!/usr/bin/env python3
"""Regression tests for the offline bass-attack tempo diagnostic."""

from __future__ import annotations

import csv
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import wave


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_bass_tempo_onsets.py"


def make_tempo_midi(bpm: int) -> bytes:
    microseconds = round(60_000_000 / bpm)
    track = b"\x00\xff\x51\x03" + microseconds.to_bytes(3, "big") + b"\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def write_impulse_bass(path: Path, bpm: int) -> None:
    sample_rate = 44100
    samples = [0] * (sample_rate * 20)
    beat = round(sample_rate * 60 / bpm)
    for start in range(0, len(samples), beat):
        for offset in range(min(1200, len(samples) - start)):
            samples[start + offset] = int(26000 * (1.0 - offset / 1200.0))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(struct.pack("<" + "h" * len(samples), *samples))


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        fixture = Path(temp)
        (fixture / "audio").mkdir()
        (fixture / "midi").mkdir()
        write_impulse_bass(fixture / "audio" / "filobass_test.wav", 120)
        (fixture / "midi" / "filobass_test.mid").write_bytes(make_tempo_midi(120))
        with (fixture / "maestro-v3.0.0.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["audio_filename", "midi_filename", "tempo_audio_offset_seconds"])
            writer.writeheader()
            writer.writerow({"audio_filename": "audio/filobass_test.wav", "midi_filename": "midi/filobass_test.mid", "tempo_audio_offset_seconds": "0"})
        output = fixture / "diagnostics.tsv"
        subprocess.run([sys.executable, str(SCRIPT), "--root", str(fixture), "--output", str(output)], check=True)
        with output.open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle, delimiter="\t"))
        assert int(row["top_bpm"]) in range(116, 125), row
        assert int(row["expected_rank"]) == 1, row
        assert row["top_or_double_hit"] == "1", row
    print("test_inspect_bass_tempo_onsets: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
