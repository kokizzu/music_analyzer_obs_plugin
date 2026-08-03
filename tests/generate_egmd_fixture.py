#!/usr/bin/env python3
import csv
import math
import os
import struct
import sys
import wave


DEFAULT_RECORDING_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 8.0
TICKS_PER_QUARTER = 480
TEMPOS = [
    64,
    72,
    84,
    92,
    100,
    108,
    116,
    120,
    128,
    137,
    145,
    156,
    168,
    184,
    205,
]


def vlq(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.insert(0, 0x80 | (value & 0x7F))
        value >>= 7
    return bytes(bytes_out)


def tempo_us_per_quarter(bpm):
    return int(round(60000000.0 / bpm))


def seconds_to_ticks(seconds, bpm):
    return int(round(seconds * bpm / 60.0 * TICKS_PER_QUARTER))


def track_chunk(events):
    payload = bytearray()
    for delta, event in events:
        payload.extend(vlq(delta))
        payload.extend(event)
    payload.extend(vlq(0))
    payload.extend(b"\xff\x2f\x00")
    return b"MTrk" + struct.pack(">I", len(payload)) + bytes(payload)


def build_hits(bpm, variant):
    beat_seconds = 60.0 / bpm
    hits = []
    beat = 0
    seconds = beat_seconds * 0.50
    while seconds < DURATION_SECONDS - 0.12:
        position = beat % 4
        if position == 0:
            hits.append((seconds, 36, 112))
            if variant % 3 == 0:
                hits.append((seconds + beat_seconds * 0.50, 42, 82))
        elif position == 1:
            hits.append((seconds, 42, 88))
        elif position == 2:
            hits.append((seconds, 38, 114))
            if variant % 4 == 0:
                hits.append((seconds + beat_seconds * 0.50, 42, 78))
        else:
            hits.append((seconds, 45 if variant % 2 == 0 else 51, 96))
        seconds += beat_seconds
        beat += 1
    return hits


def write_midi(path, hits, bpm):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tempo = tempo_us_per_quarter(bpm)
    absolute_events = [
        (
            0,
            bytes(
                [
                    0xFF,
                    0x51,
                    0x03,
                    (tempo >> 16) & 0xFF,
                    (tempo >> 8) & 0xFF,
                    tempo & 0xFF,
                ]
            ),
        )
    ]
    for seconds, midi, velocity in hits:
        start = seconds_to_ticks(seconds, bpm)
        end = seconds_to_ticks(seconds + 0.08, bpm)
        absolute_events.append((start, bytes([0x99, midi, velocity])))
        absolute_events.append((end, bytes([0x89, midi, 0])))
    absolute_events.sort(key=lambda item: (item[0], item[1][0], item[1][1] if len(item[1]) > 1 else 0))

    events = []
    previous_tick = 0
    for tick, event in absolute_events:
        events.append((tick - previous_tick, event))
        previous_tick = tick

    header = b"MThd" + struct.pack(">IHHH", 6, 1, 1, TICKS_PER_QUARTER)
    with open(path, "wb") as midi_file:
        midi_file.write(header + track_chunk(events))


def add_decaying_sine(samples, freq, start_seconds, duration_seconds, amplitude):
    start = max(0, int(start_seconds * SAMPLE_RATE))
    end = min(len(samples), int((start_seconds + duration_seconds) * SAMPLE_RATE))
    for i in range(start, end):
        rel = (i - start) / max(1, end - start)
        envelope = (1.0 - rel) ** 2
        samples[i] += amplitude * envelope * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)


def add_background_floor(samples):
    floor_freqs = (55.0, 90.0, 120.0, 160.0, 220.0, 3600.0, 5600.0, 7600.0)
    for i in range(len(samples)):
        value = 0.0
        for index, freq in enumerate(floor_freqs):
            value += math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE + index * 0.37)
        samples[i] += 0.0007 * value / len(floor_freqs)


def add_hit(samples, midi, seconds):
    if midi in (35, 36):
        add_decaying_sine(samples, 55.0, seconds, 0.13, 0.95)
        add_decaying_sine(samples, 70.0, seconds, 0.09, 0.48)
        add_decaying_sine(samples, 650.0, seconds, 0.018, 0.32)
    elif midi in (38, 40):
        add_decaying_sine(samples, 220.0, seconds, 0.10, 0.55)
        add_decaying_sine(samples, 1100.0, seconds, 0.08, 0.45)
        add_decaying_sine(samples, 2200.0, seconds, 0.06, 0.30)
    elif midi in (41, 43, 45, 47, 48, 50):
        add_decaying_sine(samples, 120.0, seconds, 0.14, 0.55)
        add_decaying_sine(samples, 160.0, seconds, 0.12, 0.60)
        add_decaying_sine(samples, 220.0, seconds, 0.09, 0.35)
    else:
        add_decaying_sine(samples, 7600.0, seconds, 0.07, 0.35)
        add_decaying_sine(samples, 9800.0, seconds, 0.06, 0.30)


def write_wav(path, hits):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    samples = [0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))]
    add_background_floor(samples)
    for seconds, midi, _velocity in hits:
        add_hit(samples, midi, seconds)
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
    os.makedirs(os.path.join(root, "drummer1", "session1"), exist_ok=True)
    rows = []
    for index in range(1, recording_count + 1):
        bpm = TEMPOS[(index - 1) % len(TEMPOS)]
        hits = build_hits(bpm, index)
        stem = f"fixture_egmd_{index:03d}"
        midi_filename = f"drummer1/session1/{stem}.mid"
        audio_filename = f"drummer1/session1/{stem}.wav"
        write_midi(os.path.join(root, midi_filename), hits, bpm)
        write_wav(os.path.join(root, audio_filename), hits)
        rows.append(
            {
                "drummer": "drummer1",
                "session": "session1",
                "id": stem,
                "style": "fixture/rock",
                "bpm": str(bpm),
                "beat_type": "beat",
                "time_signature": "4-4",
                "midi_filename": midi_filename,
                "audio_filename": audio_filename,
                "duration": f"{DURATION_SECONDS:.3f}",
                "split": "train" if index <= recording_count // 2 else "test",
                "kit_name": "fixture-kit",
            }
        )

    with open(os.path.join(root, "e-gmd-v1.0.0.csv"), "w", encoding="utf-8", newline="") as metadata:
        writer = csv.DictWriter(
            metadata,
            fieldnames=[
                "drummer",
                "session",
                "id",
                "style",
                "bpm",
                "beat_type",
                "time_signature",
                "midi_filename",
                "audio_filename",
                "duration",
                "split",
                "kit_name",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_egmd_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    write_fixture(argv[1])
    print(f"generate_egmd_fixture: wrote {DEFAULT_RECORDING_COUNT} E-GMD-shaped recordings to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
