#!/usr/bin/env python3
import csv
import math
import os
import struct
import sys
import wave


DEFAULT_RECORDING_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
TICKS_PER_QUARTER = 480
TICKS_PER_SECOND = 960
WINDOWS = [
    (0.30, [60, 64, 67]),
    (0.70, [62, 65, 69]),
    (1.10, [55, 59, 62, 67]),
    (1.50, [57, 60, 64]),
]


def vlq(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.insert(0, 0x80 | (value & 0x7F))
        value >>= 7
    return bytes(bytes_out)


def seconds_to_ticks(seconds):
    return int(round(seconds * TICKS_PER_SECOND))


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
    absolute_events = [
        (0, b"\xff\x51\x03\x07\xa1\x20"),
        (0, b"\xc0\x00"),
    ]
    for center, chord in WINDOWS:
        start = seconds_to_ticks(center - 0.17)
        end = seconds_to_ticks(center + 0.17)
        for midi in chord:
            note = midi + (transpose % 12)
            absolute_events.append((start, bytes([0x90, note, 88])))
            absolute_events.append((end, bytes([0x80, note, 0])))
    absolute_events.sort(key=lambda item: (item[0], item[1][0], item[1][1] if len(item[1]) > 1 else 0))

    events = []
    previous_tick = 0
    for tick, event in absolute_events:
        events.append((tick - previous_tick, event))
        previous_tick = tick

    header = b"MThd" + struct.pack(">IHHH", 6, 1, 1, TICKS_PER_QUARTER)
    with open(path, "wb") as midi_file:
        midi_file.write(header + track_chunk(events))


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(samples, midi, center_seconds, duration_seconds, amplitude):
    start = max(0, int((center_seconds - duration_seconds / 2.0) * SAMPLE_RATE))
    end = min(len(samples), int((center_seconds + duration_seconds / 2.0) * SAMPLE_RATE))
    freq = midi_frequency(midi)
    for i in range(start, end):
        rel = (i - start) / max(1, end - start)
        envelope = min(1.0, rel * 10.0, (1.0 - rel) * 10.0)
        harmonic = 0.35 * math.sin(2.0 * math.pi * freq * 2.0 * i / SAMPLE_RATE)
        samples[i] += amplitude * envelope * (math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE) + harmonic)


def write_wav(path, transpose):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    samples = [0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))]
    for center, chord in WINDOWS:
        for midi in chord:
            add_tone(samples, midi + (transpose % 12), center, 0.34, 0.14)
    with wave.open(path, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            clipped = max(-1.0, min(1.0, sample))
            value = int(clipped * 32767.0)
            frames.extend(struct.pack("<hh", value, value))
        wav.writeframes(bytes(frames))


def write_fixture(root, recording_count=DEFAULT_RECORDING_COUNT):
    os.makedirs(os.path.join(root, "2018"), exist_ok=True)
    rows = []
    for index in range(1, recording_count + 1):
        stem = f"fixture_maestro_{index:03d}"
        midi_filename = f"2018/{stem}.midi"
        audio_filename = f"2018/{stem}.wav"
        transpose = index % 12
        write_midi(os.path.join(root, midi_filename), transpose)
        write_wav(os.path.join(root, audio_filename), transpose)
        rows.append(
            {
                "canonical_composer": "Fixture Composer",
                "canonical_title": f"Fixture Piano Piece {index:03d}",
                "split": "train" if index <= recording_count // 2 else "test",
                "year": "2018",
                "midi_filename": midi_filename,
                "audio_filename": audio_filename,
                "duration": f"{DURATION_SECONDS:.3f}",
            }
        )

    with open(os.path.join(root, "maestro-v3.0.0.csv"), "w", encoding="utf-8", newline="") as metadata:
        writer = csv.DictWriter(
            metadata,
            fieldnames=[
                "canonical_composer",
                "canonical_title",
                "split",
                "year",
                "midi_filename",
                "audio_filename",
                "duration",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_maestro_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    write_fixture(argv[1])
    print(f"generate_maestro_fixture: wrote {DEFAULT_RECORDING_COUNT} MAESTRO-shaped recordings to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
