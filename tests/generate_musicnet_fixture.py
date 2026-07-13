#!/usr/bin/env python3
import csv
import math
import os
import struct
import sys
import wave


SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
RECORDING_COUNT = 20
WINDOWS = [
    (0.30, [60, 64, 67]),
    (0.70, [62, 65, 69]),
    (1.10, [55, 59, 62]),
    (1.50, [57, 60, 64]),
]
INSTRUMENTS = [41, 42, 43]


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
    return start, end


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            clipped = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", int(clipped * 32767.0)))
        wav.writeframes(bytes(frames))


def write_recording(root, recording_id):
    data_dir = os.path.join(root, "train_data")
    label_dir = os.path.join(root, "train_labels")
    samples = [0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))]
    rows = []

    transpose = recording_id % 12
    for center, chord in WINDOWS:
        for index, midi in enumerate(chord):
            shifted = midi + transpose
            start, end = add_tone(samples, shifted, center, 0.34, 0.20)
            rows.append(
                {
                    "start_time": start,
                    "end_time": end,
                    "instrument": INSTRUMENTS[index],
                    "note": shifted,
                    "start_beat": 0.0,
                    "end_beat": 0.0,
                    "note_value": 0.0,
                }
            )

    write_wav(os.path.join(data_dir, f"{recording_id}.wav"), samples)
    os.makedirs(label_dir, exist_ok=True)
    with open(os.path.join(label_dir, f"{recording_id}.csv"), "w", newline="", encoding="utf-8") as label_file:
        writer = csv.DictWriter(
            label_file,
            fieldnames=[
                "start_time",
                "end_time",
                "instrument",
                "note",
                "start_beat",
                "end_beat",
                "note_value",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    os.makedirs(root, exist_ok=True)
    for recording_id in range(1, RECORDING_COUNT + 1):
        write_recording(root, recording_id)
    print(f"generate_musicnet_fixture: wrote {RECORDING_COUNT} recordings to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
