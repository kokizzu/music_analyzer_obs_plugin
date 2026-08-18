#!/usr/bin/env python3
"""Create a real-bass BPM fixture from FiloBass downbeat annotations.

FiloBass supplies bass stems, a score-aligned MIDI file, and reviewed
Soundslice syncpoints.  The syncpoints give audio-time downbeats; the MIDI
time signature supplies the beats per bar.  We derive the reference BPM only
from those two corpus annotations, never from the bass-note onsets.

Converted WAVs and the fixture remain below the external InstrumentSamples
store.  The script does not play audio.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess


def normalized_stem(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "", path.stem.lower())


def vlq(value: int) -> bytes:
    encoded = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        encoded.append((value & 0x7F) | 0x80)
    return bytes(reversed(encoded))


def midi_with_tempo(bpm: float) -> bytes:
    microseconds = round(60_000_000 / bpm)
    track = b"\x00\xff\x51\x03" + microseconds.to_bytes(3, "big")
    track += b"\x00\x90\x3c\x40" + vlq(480 * 64) + b"\x80\x3c\x00"
    track += b"\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def read_vlq(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if offset >= len(data):
            raise ValueError("truncated variable-length MIDI value")
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, offset
    raise ValueError("invalid variable-length MIDI value")


def midi_beats_per_bar(path: Path) -> float | None:
    """Read the first SMF time signature, without depending on MIDI packages."""
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        return None
    header_size = struct.unpack(">I", data[4:8])[0]
    if header_size < 6 or len(data) < 8 + header_size:
        return None
    tracks = struct.unpack(">H", data[10:12])[0]
    offset = 8 + header_size
    for _ in range(tracks):
        if offset + 8 > len(data) or data[offset:offset + 4] != b"MTrk":
            return None
        length = struct.unpack(">I", data[offset + 4:offset + 8])[0]
        track_end = offset + 8 + length
        if track_end > len(data):
            return None
        cursor = offset + 8
        running_status: int | None = None
        while cursor < track_end:
            _, cursor = read_vlq(data, cursor)
            if cursor >= track_end:
                return None
            status = data[cursor]
            if status < 0x80:
                if running_status is None:
                    return None
                status = running_status
            else:
                cursor += 1
                if status < 0xF0:
                    running_status = status
                else:
                    running_status = None
            if status == 0xFF:
                if cursor >= track_end:
                    return None
                meta_type = data[cursor]
                cursor += 1
                length, cursor = read_vlq(data, cursor)
                if cursor + length > track_end:
                    return None
                if meta_type == 0x58 and length >= 2:
                    return float(data[cursor]) * (4.0 / (2 ** data[cursor + 1]))
                cursor += length
            elif status in (0xF0, 0xF7):
                length, cursor = read_vlq(data, cursor)
                cursor += length
            else:
                cursor += 1 if 0xC0 <= status <= 0xDF else 2
        offset = track_end
    return None


def syncpoint_downbeats(path: Path) -> list[float]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("syncpoints are not a list")
    result: list[float] = []
    for point in raw:
        if not isinstance(point, list) or len(point) < 2:
            continue
        # Soundslice omits position-in-bar for downbeats.  When it is present,
        # 0 is the only downbeat value.
        if len(point) >= 3 and point[2] not in (0, 0.0, None):
            continue
        try:
            seconds = float(point[1])
        except (TypeError, ValueError):
            continue
        if not result or seconds > result[-1]:
            result.append(seconds)
    return result


def stable_segment(downbeats: list[float], beats_per_bar: float, minimum_seconds: float) -> tuple[float, float] | None:
    """Return a stable reviewed downbeat interval as (audio_offset, BPM)."""
    for begin in range(len(downbeats) - 1):
        intervals: list[float] = []
        for end in range(begin + 1, len(downbeats)):
            interval = downbeats[end] - downbeats[end - 1]
            if interval <= 0.50 or interval >= 16.0:
                break
            intervals.append(interval)
            duration = downbeats[end] - downbeats[begin]
            if duration < minimum_seconds or len(intervals) < 4:
                continue
            mean = sum(intervals) / len(intervals)
            if max(abs(item - mean) for item in intervals) <= mean * 0.12:
                return downbeats[begin], 60.0 * beats_per_bar / mean
    return None


def syncpoints_by_stem(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for directory in sorted(root.rglob("syncpoints")):
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            key = normalized_stem(path).removesuffix("syncpoints")
            if key and key not in result:
                result[key] = path
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--minimum-seconds", type=float, default=14.0)
    parser.add_argument("--limit", type=int, default=24)
    args = parser.parse_args(argv)
    if not args.root.is_dir() or not args.pairs.is_file():
        raise SystemExit("prepare_filobass_tempo_fixture: missing extracted dataset or inspected pairs TSV")
    if args.output.exists():
        shutil.rmtree(args.output)
    (args.output / "audio").mkdir(parents=True)
    (args.output / "midi").mkdir()
    syncpoints = syncpoints_by_stem(args.root)
    rows: list[dict[str, str]] = []
    with args.pairs.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            key = source["track_id"]
            syncpoint = syncpoints.get(key)
            audio = Path(source["audio_path"])
            midi = Path(source["downbeat_midi_path"])
            if syncpoint is None or not audio.is_file() or not midi.is_file():
                continue
            beats_per_bar = midi_beats_per_bar(midi)
            if beats_per_bar is None:
                continue
            try:
                segment = stable_segment(syncpoint_downbeats(syncpoint), beats_per_bar, args.minimum_seconds)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if segment is None:
                continue
            offset, bpm = segment
            identity = f"filobass_{key}"
            audio_name = f"audio/{identity}.wav"
            midi_name = f"midi/{identity}.mid"
            destination = args.output / audio_name
            # Decode exactly the selected bounded diagnostic subset.  ffmpeg is
            # invoked without an audio-output device, so it cannot play sound.
            subprocess.run(
                [args.ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(audio), str(destination)], check=True
            )
            (args.output / midi_name).write_bytes(midi_with_tempo(bpm))
            rows.append({
                "audio_filename": audio_name,
                "midi_filename": midi_name,
                "tempo_audio_offset_seconds": f"{offset:.6f}",
            })
            if len(rows) >= args.limit:
                break
    if not rows:
        raise SystemExit("prepare_filobass_tempo_fixture: no paired FiloBass tracks with reviewed stable downbeats")
    with (args.output / "maestro-v3.0.0.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"prepare_filobass_tempo_fixture: tracks={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
