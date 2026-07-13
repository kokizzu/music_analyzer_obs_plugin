#!/usr/bin/env python3
import hashlib
import json
import math
import os
import struct
import sys
import wave


DEFAULT_SEGMENT_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
WINDOWS = [
    (0.30, [60, 64, 67]),
    (0.70, [62, 65, 69]),
    (1.10, [55, 59, 62]),
    (1.50, [57, 60, 64]),
]
PROGRAMS = [0, 24, 48]
TICKS_PER_QUARTER = 480
TICKS_PER_SECOND = 960


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


def seconds_to_ticks(seconds):
    return int(round(seconds * TICKS_PER_SECOND))


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(samples, midi, center_seconds, duration_seconds, amplitude):
    start = max(0, int((center_seconds - duration_seconds / 2.0) * SAMPLE_RATE))
    end = min(len(samples), int((center_seconds + duration_seconds / 2.0) * SAMPLE_RATE))
    freq = midi_frequency(midi)
    for i in range(start, end):
        rel = (i - start) / max(1, end - start)
        envelope = min(1.0, rel * 12.0, (1.0 - rel) * 12.0)
        samples[i] += amplitude * envelope * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)


def write_wav(path, samples):
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            clipped = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", int(clipped * 32767.0)))
        wav.writeframes(bytes(frames))


def write_midi(path, transpose):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(PROGRAMS), TICKS_PER_QUARTER)
    chunks = []
    for part_index, program in enumerate(PROGRAMS):
        absolute_events = [(0, bytes([0xC0 | part_index, program]))]
        for center, chord in WINDOWS:
            midi = chord[part_index] + (transpose % 12)
            start = seconds_to_ticks(center - 0.17)
            end = seconds_to_ticks(center + 0.17)
            absolute_events.append((start, bytes([0x90 | part_index, midi, 88 - part_index * 4])))
            absolute_events.append((end, bytes([0x80 | part_index, midi, 0])))
        absolute_events.sort(key=lambda item: (item[0], item[1][0]))

        track_events = []
        previous_tick = 0
        for tick, event in absolute_events:
            track_events.append((tick - previous_tick, event))
            previous_tick = tick
        chunks.append(track_chunk(track_events))

    data = header + b"".join(chunks)
    with open(path, "wb") as midi_file:
        midi_file.write(data)
    return hashlib.sha256(data).hexdigest()


def write_audio(path, transpose):
    samples = [0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))]
    for center, chord in WINDOWS:
        for midi in chord:
            add_tone(samples, midi + (transpose % 12), center, 0.34, 0.18)
    write_wav(path, samples)


def write_segment(root, index, write_audio_files, split_at, audio_root=None):
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
    if write_audio_files:
        audio_dir = os.path.join(audio_root, split, segment_id) if audio_root else segment_dir
        os.makedirs(audio_dir, exist_ok=True)
        write_audio(os.path.join(audio_dir, "audio.wav"), index)


def write_fixture(root, segment_count=DEFAULT_SEGMENT_COUNT, write_audio=False, audio_root=None):
    os.makedirs(root, exist_ok=True)
    if audio_root:
        os.makedirs(audio_root, exist_ok=True)
    split_at = max(1, segment_count // 2)
    for index in range(1, segment_count + 1):
        write_segment(root, index, write_audio, split_at, audio_root=audio_root)


def main(argv):
    if len(argv) not in (2, 3, 4):
        print("usage: generate_multtipop_fixture.py OUT_DIR [--with-audio [AUDIO_ROOT]]", file=sys.stderr)
        return 2
    write_audio = len(argv) == 3 and argv[2] == "--with-audio"
    if len(argv) == 4:
        write_audio = argv[2] == "--with-audio"
    if len(argv) >= 3 and not write_audio:
        print("usage: generate_multtipop_fixture.py OUT_DIR [--with-audio [AUDIO_ROOT]]", file=sys.stderr)
        return 2
    audio_root = argv[3] if len(argv) == 4 else None
    write_fixture(argv[1], write_audio=write_audio, audio_root=audio_root)
    suffix = " with WAV audio" if write_audio else ""
    if audio_root:
        suffix += f" under {audio_root}"
    print(f"generate_multtipop_fixture: wrote {DEFAULT_SEGMENT_COUNT} MulTTiPop-shaped segments{suffix} to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
