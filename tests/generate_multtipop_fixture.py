#!/usr/bin/env python3
import hashlib
import json
import os
import struct
import sys


DEFAULT_SEGMENT_COUNT = 20


def vlq(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.insert(0, 0x80 | (value & 0x7F))
        value >>= 7
    return bytes(bytes_out)


def track_chunk(events):
    payload = bytearray()
    for delta, event in events:
        payload.extend(vlq(delta))
        payload.extend(event)
    payload.extend(vlq(0))
    payload.extend(b"\xff\x2f\x00")
    return b"MTrk" + struct.pack(">I", len(payload)) + bytes(payload)


def write_midi(path, transpose):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, 480)
    melody_note = 60 + (transpose % 12)
    harmony_note = 67 + (transpose % 12)
    melody = track_chunk([
        (0, bytes([0xC0, 0])),
        (0, bytes([0x90, melody_note, 88])),
        (480, bytes([0x80, melody_note, 0])),
    ])
    harmony = track_chunk([
        (0, bytes([0xC1, 48])),
        (0, bytes([0x91, harmony_note, 82])),
        (480, bytes([0x81, harmony_note, 0])),
    ])
    data = header + melody + harmony
    with open(path, "wb") as midi_file:
        midi_file.write(data)
    return hashlib.sha256(data).hexdigest()


def write_audio_marker(path):
    with open(path, "wb") as audio_file:
        audio_file.write(b"local audio segment marker\n")


def write_segment(root, index, write_audio, split_at):
    split = "dev" if index <= split_at else "test"
    segment_id = f"fixture{index:03d}"
    segment_dir = os.path.join(root, split, segment_id)
    midi_path = os.path.join(segment_dir, "aligned.mid")
    checksum = write_midi(midi_path, index)
    meta = {
        "id": segment_id,
        "artist": "Fixture Artist",
        "name": f"Fixture Song {index:03d}",
        "section": "Chorus",
        "tempo": 120,
        "meter": 4,
        "key": {"tonic": "C", "scale": "major"},
        "youtube": {
            "id": f"fixture{index:03d}",
            "start": float(index),
            "end": float(index) + 20.0,
        },
        "chosen_method": ["melody"],
        "chosen_beat_idx": index,
        "chosen_beat_time": float(index),
        "chosen_lmd_midi_filename": f"fixture{index:03d}.mid",
        "aligned_midi_checksum": checksum,
        "split_name": split,
        "audio_length": 20.0,
    }
    with open(os.path.join(segment_dir, "meta.json"), "w", encoding="utf-8") as meta_file:
        json.dump(meta, meta_file, sort_keys=True)
        meta_file.write("\n")
    if write_audio:
        write_audio_marker(os.path.join(segment_dir, "audio.wav"))


def write_fixture(root, segment_count=DEFAULT_SEGMENT_COUNT, write_audio=False):
    os.makedirs(root, exist_ok=True)
    split_at = max(1, segment_count // 2)
    for index in range(1, segment_count + 1):
        write_segment(root, index, write_audio, split_at)


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: generate_multtipop_fixture.py OUT_DIR [--with-audio]", file=sys.stderr)
        return 2
    write_audio = len(argv) == 3 and argv[2] == "--with-audio"
    if len(argv) == 3 and not write_audio:
        print("usage: generate_multtipop_fixture.py OUT_DIR [--with-audio]", file=sys.stderr)
        return 2
    write_fixture(argv[1], write_audio=write_audio)
    suffix = " with audio markers" if write_audio else ""
    print(f"generate_multtipop_fixture: wrote {DEFAULT_SEGMENT_COUNT} MulTTiPop-shaped segments{suffix} to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
