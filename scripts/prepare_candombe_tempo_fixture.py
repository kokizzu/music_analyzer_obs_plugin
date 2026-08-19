#!/usr/bin/env python3
"""Create an external labelled Candombe BPM fixture without playing audio."""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import struct
import subprocess
from pathlib import Path


def stem(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "", path.stem.lower())


def vlq(value: int) -> bytes:
    result = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        result.append((value & 0x7F) | 0x80)
    return bytes(reversed(result))


def tempo_midi(bpm: float) -> bytes:
    track = b"\x00\xff\x51\x03" + round(60_000_000 / bpm).to_bytes(3, "big")
    track += b"\x00\x90\x3c\x40" + vlq(480 * 64) + b"\x80\x3c\x00\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def beats(path: Path) -> list[float]:
    values: list[float] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            try: value = float(row[0])
            except (IndexError, ValueError): continue
            if not values or value > values[-1]: values.append(value)
    return values


def stable(values: list[float], minimum: float) -> tuple[float, float, float] | None:
    for begin in range(len(values) - 1):
        intervals: list[float] = []
        candidate = None
        for end in range(begin + 1, len(values)):
            interval = values[end] - values[end - 1]
            if not 0.20 < interval < 2.00: break
            intervals.append(interval)
            duration = values[end] - values[begin]
            if duration < minimum or len(intervals) < 12: continue
            mean = sum(intervals) / len(intervals)
            if max(abs(item - mean) for item in intervals) > mean * .10: break
            candidate = values[begin], 60.0 / mean, duration
        if candidate is not None: return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--minimum-seconds", type=float, default=14.0)
    parser.add_argument("--limit", type=int, default=35)
    args = parser.parse_args()
    audio = {stem(path): path for path in sorted((args.root / "audio").rglob("*.flac"))}
    eligible = [(audio[stem(label)], *segment) for label in sorted((args.root / "annotations").rglob("*.csv")) if stem(label) in audio if (segment := stable(beats(label), args.minimum_seconds))]
    if len(eligible) < min(args.limit, 35): raise SystemExit(f"prepare_candombe_tempo_fixture: only {len(eligible)} stable paired recordings")
    if args.output.exists(): shutil.rmtree(args.output)
    (args.output / "audio").mkdir(parents=True); (args.output / "midi").mkdir()
    rows: list[dict[str, str]] = []
    for number, (source, offset, bpm, duration) in enumerate(eligible[:args.limit], 1):
        identity = f"candombe_{number:02d}_{stem(source)}"
        wav, midi = f"audio/{identity}.wav", f"midi/{identity}.mid"
        subprocess.run([args.ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(source), str(args.output / wav)], check=True)
        (args.output / midi).write_bytes(tempo_midi(bpm))
        rows.append({"audio_filename": wav, "midi_filename": midi, "tempo_audio_offset_seconds": f"{offset:.6f}", "tempo_duration_seconds": f"{duration:.6f}"})
    with (args.output / "maestro-v3.0.0.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    print(f"prepare_candombe_tempo_fixture: tracks={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
