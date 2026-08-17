#!/usr/bin/env python3
"""Create a tiny MAESTRO-compatible tempo fixture from KRAISLER beat annotations.

The fixture contains only CSV/MIDI metadata and relative symlinks to the source WAVs.
It never copies the KRAISLER audio out of the external InstrumentSamples store.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import struct
from pathlib import Path


def vlq(value: int) -> bytes:
    encoded = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        encoded.append((value & 0x7F) | 0x80)
    return bytes(reversed(encoded))


def midi_with_tempo(bpm: float) -> bytes:
    microseconds = round(60_000_000 / bpm)
    track = b"\x00\xff\x51\x03" + microseconds.to_bytes(3, "big")
    # A long C4 makes the normal MAESTRO candidate-window checks harmless when
    # this compatibility fixture is used solely for tempo diagnostics.
    track += b"\x00\x90\x3c\x40" + vlq(480 * 64) + b"\x80\x3c\x00"
    track += b"\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def stable_segment(beats: list[float], minimum_seconds: float) -> tuple[float, float] | None:
    for begin in range(len(beats) - 1):
        intervals: list[float] = []
        for end in range(begin + 1, len(beats)):
            interval = beats[end] - beats[end - 1]
            if interval <= 0.20 or interval >= 2.00:
                break
            intervals.append(interval)
            duration = beats[end] - beats[begin]
            if duration < minimum_seconds or len(intervals) < 12:
                continue
            mean = sum(intervals) / len(intervals)
            if max(abs(item - mean) for item in intervals) <= mean * 0.12:
                return beats[begin], 60.0 / mean
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="extracted KRAISLER directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--configuration", default="dry")
    parser.add_argument("--minimum-seconds", type=float, default=14.0)
    args = parser.parse_args()

    metadata = args.root / "metadata.csv"
    if not metadata.is_file():
        raise SystemExit(f"missing KRAISLER metadata: {metadata}")
    output = args.output
    if output.exists():
        shutil.rmtree(output)
    (output / "audio").mkdir(parents=True)
    (output / "midi").mkdir()

    rows: list[dict[str, str]] = []
    with metadata.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle):
            track = source["track"]
            beat_path = args.root / source["beats_csv"]
            audio_path = args.root / source[f"audio_mix_{args.configuration}"]
            if not beat_path.is_file() or not audio_path.is_file():
                continue
            with beat_path.open(newline="", encoding="utf-8") as beats_handle:
                beats = [float(row["beat_time"]) for row in csv.DictReader(beats_handle)]
            segment = stable_segment(beats, args.minimum_seconds)
            if segment is None:
                continue
            offset, bpm = segment
            audio_name = f"audio/{track}_{args.configuration}.wav"
            midi_name = f"midi/{track}.mid"
            link = output / audio_name
            os.symlink(os.path.relpath(audio_path, link.parent), link)
            (output / midi_name).write_bytes(midi_with_tempo(bpm))
            rows.append({
                "audio_filename": audio_name,
                "midi_filename": midi_name,
                "tempo_audio_offset_seconds": f"{offset:.6f}",
            })

    if not rows:
        raise SystemExit("no KRAISLER tracks with a stable annotated beat interval")
    with (output / "maestro-v3.0.0.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"prepare_kraisler_tempo_fixture: tracks={len(rows)} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
