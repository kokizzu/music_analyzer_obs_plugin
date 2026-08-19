#!/usr/bin/env python3
"""Prepare BabySlakh full mixes as an E-GMD-shaped drum-truth fixture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
import inspect_slakh_dataset


FIXTURE_VERSION = "babyslakh-drums-egmd-shaped-v1"
DIVISION = 480
TEMPO_US_PER_QUARTER = 500000
SUPPORTED_DRUM_MIDI = {
    35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 57, 59,
}


def read_be_u16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


def read_be_u32(data: bytes, offset: int) -> int:
    return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]


def read_var_len(data: bytes, pos: int, end: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= end:
            raise ValueError("truncated MIDI variable-length value")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos
    raise ValueError("invalid MIDI variable-length value")


def midi_event_data_length(status: int) -> int:
    event_type = status & 0xF0
    if event_type in (0xC0, 0xD0):
        return 1
    if event_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    return -1


def build_tempo_points(events: list[tuple[int, int]], division: int) -> list[tuple[int, float, int]]:
    points = [(0, 0.0, TEMPO_US_PER_QUARTER)]
    current_tick = 0
    current_seconds = 0.0
    current_tempo = TEMPO_US_PER_QUARTER
    for tick, tempo in sorted(events):
        if tick < current_tick:
            continue
        current_seconds += (tick - current_tick) * current_tempo / (division * 1_000_000.0)
        current_tick = tick
        current_tempo = tempo
        if points[-1][0] == tick:
            points[-1] = (tick, current_seconds, tempo)
        else:
            points.append((tick, current_seconds, tempo))
    return points


def tick_to_seconds(points: list[tuple[int, float, int]], tick: int, division: int) -> float:
    point = points[0]
    for candidate in points:
        if candidate[0] > tick:
            break
        point = candidate
    point_tick, point_seconds, tempo = point
    return point_seconds + (tick - point_tick) * tempo / (division * 1_000_000.0)


def parse_drum_midi(path: Path) -> list[tuple[float, int, int]]:
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError(f"{path}: not a MIDI file")
    header_len = read_be_u32(data, 4)
    if header_len < 6 or 8 + header_len > len(data):
        raise ValueError(f"{path}: invalid MIDI header")
    track_count = read_be_u16(data, 10)
    division = read_be_u16(data, 12)
    if division & 0x8000 or division <= 0:
        raise ValueError(f"{path}: unsupported MIDI timing")

    pos = 8 + header_len
    raw_hits: list[tuple[int, int, int]] = []
    tempo_events: list[tuple[int, int]] = []
    parsed_tracks = 0
    while pos + 8 <= len(data) and parsed_tracks < track_count:
        is_track = data[pos : pos + 4] == b"MTrk"
        chunk_len = read_be_u32(data, pos + 4)
        pos += 8
        if pos + chunk_len > len(data):
            raise ValueError(f"{path}: truncated MIDI chunk")
        end = pos + chunk_len
        if not is_track:
            pos = end
            continue
        parsed_tracks += 1
        tick = 0
        running_status = 0
        while pos < end:
            delta, pos = read_var_len(data, pos, end)
            tick += delta
            if pos >= end:
                raise ValueError(f"{path}: truncated MIDI event")
            status = data[pos]
            if status & 0x80:
                pos += 1
                if status < 0xF0:
                    running_status = status
            else:
                if not running_status:
                    raise ValueError(f"{path}: MIDI running status without previous status")
                status = running_status
            if status == 0xFF:
                if pos >= end:
                    raise ValueError(f"{path}: truncated MIDI meta event")
                meta_type = data[pos]
                pos += 1
                length, pos = read_var_len(data, pos, end)
                if pos + length > end:
                    raise ValueError(f"{path}: truncated MIDI meta payload")
                if meta_type == 0x51 and length == 3:
                    tempo_events.append((tick, (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]))
                pos += length
                continue
            if status in (0xF0, 0xF7):
                length, pos = read_var_len(data, pos, end)
                if pos + length > end:
                    raise ValueError(f"{path}: truncated MIDI sysex payload")
                pos += length
                continue
            data_len = midi_event_data_length(status)
            if data_len < 0 or pos + data_len > end:
                raise ValueError(f"{path}: truncated MIDI channel event")
            midi = data[pos]
            velocity = data[pos + 1] if data_len > 1 else 0
            pos += data_len
            if (status & 0xF0) == 0x90 and velocity > 0 and midi in SUPPORTED_DRUM_MIDI:
                raw_hits.append((tick, midi, velocity))
        pos = end
    points = build_tempo_points(tempo_events, division)
    return sorted((tick_to_seconds(points, tick, division), midi, velocity) for tick, midi, velocity in raw_hits)


def var_len(value: int) -> bytes:
    value = max(0, int(value))
    encoded = [value & 0x7F]
    value >>= 7
    while value:
        encoded.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(encoded)


def write_midi(path: Path, hits: list[tuple[float, int, int]]) -> None:
    events = [(0, 0, bytes([0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20]))]
    for seconds, midi, velocity in hits:
        tick = int(round(seconds * 1_000_000.0 / TEMPO_US_PER_QUARTER * DIVISION))
        events.append((tick, 1, bytes([0x99, midi, max(1, min(127, velocity))])))
        events.append((tick + 24, 2, bytes([0x89, midi, 0])))
    events.sort(key=lambda event: (event[0], event[1], event[2]))
    track = bytearray()
    previous_tick = 0
    for tick, _order, payload in events:
        track.extend(var_len(tick - previous_tick))
        track.extend(payload)
        previous_tick = tick
    track.extend(b"\x00\xFF\x2F\x00")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") +
                     (1).to_bytes(2, "big") + DIVISION.to_bytes(2, "big") +
                     b"MTrk" + len(track).to_bytes(4, "big") + bytes(track))


def drum_stems(metadata_path: Path) -> list[str]:
    stems: list[str] = []
    current = ""
    heading = re.compile(r"^\s{2}([A-Za-z0-9_-]+):\s*$")
    for line in metadata_path.read_text(encoding="utf-8").splitlines():
        match = heading.match(line)
        if match:
            current = match.group(1)
            continue
        if current and re.match(r"^\s+is_drum:\s*true\s*$", line, re.IGNORECASE):
            stems.append(current)
            current = ""
    return stems


def resolve_root(root: Path) -> Path:
    for name in inspect_slakh_dataset.SLAKH_CHILD_NAMES:
        child = root / name
        if child.is_dir():
            return child
    return root


def signature(root: Path, tracks: list[Path]) -> str:
    digest = hashlib.sha256(FIXTURE_VERSION.encode("utf-8"))
    digest.update(str(root.resolve()).encode("utf-8"))
    for track in tracks:
        metadata = track / "metadata.yaml"
        digest.update(str(track.relative_to(root)).encode("utf-8"))
        digest.update(metadata.read_bytes())
    return digest.hexdigest()


def cached(output: Path, expected_signature: str, minimum: int) -> bool:
    marker = output / ".babyslakh_drums_signature"
    manifest = output / "e-gmd-v1.0.0.csv"
    if not marker.is_file() or marker.read_text(encoding="utf-8") != expected_signature or not manifest.is_file():
        return False
    rows = list(csv.DictReader(manifest.open("r", encoding="utf-8")))
    return len(rows) >= minimum and all((output / row["audio_filename"]).is_file() and
                                        (output / row["midi_filename"]).is_file() for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-recordings", type=int, default=20)
    args = parser.parse_args()
    root = resolve_root(args.root)
    tracks = [Path(path) for path in inspect_slakh_dataset.candidate_track_dirs(str(root))]
    tracks = sorted(track for track in tracks if (track / "metadata.yaml").is_file())
    expected_signature = signature(root, tracks)
    if cached(args.output, expected_signature, args.min_recordings):
        print(f"prepare_babyslakh_drums: reused {args.output / 'e-gmd-v1.0.0.csv'}")
        return 0
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"prepare_babyslakh_drums: existing output is not a matching fixture: {args.output}")
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for track in tracks:
        mix = inspect_slakh_dataset.find_mix_audio(inspect_slakh_dataset.find_audio_files(str(track)))
        if not mix or not mix.lower().endswith((".wav", ".wave")):
            continue
        hits: list[tuple[float, int, int]] = []
        for stem in drum_stems(track / "metadata.yaml"):
            midi = track / "MIDI" / f"{stem}.mid"
            if midi.is_file():
                hits.extend(parse_drum_midi(midi))
        if not hits:
            continue
        track_id = track.name
        audio_relative = Path("audio") / f"{track_id}.wav"
        midi_relative = Path("midi") / f"{track_id}.mid"
        audio_output = args.output / audio_relative
        audio_output.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(Path(mix).resolve(), audio_output)
        write_midi(args.output / midi_relative, hits)
        rows.append({"id": track_id, "audio_filename": str(audio_relative), "midi_filename": str(midi_relative)})
    if len(rows) < args.min_recordings:
        raise SystemExit(f"prepare_babyslakh_drums: expected {args.min_recordings} drum mixes, got {len(rows)}")
    with (args.output / "e-gmd-v1.0.0.csv").open("w", encoding="utf-8", newline="") as manifest:
        writer = csv.DictWriter(manifest, fieldnames=("id", "audio_filename", "midi_filename"))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / ".babyslakh_drums_signature").write_text(expected_signature, encoding="utf-8")
    print(f"prepare_babyslakh_drums: wrote {len(rows)} full-mix drum recordings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
