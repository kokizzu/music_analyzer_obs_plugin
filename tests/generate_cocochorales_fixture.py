#!/usr/bin/env python3
import json
import math
import os
import struct
import sys
import wave


PIECE_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
PARTS = (
    ("soprano_violin", 40, 0),
    ("alto_viola", 41, 1),
    ("tenor_cello", 42, 2),
    ("bass_bassoon", 70, 3),
)
WINDOWS = (
    (0.30, (72, 64, 55, 48)),
    (0.70, (74, 65, 57, 50)),
    (1.10, (79, 67, 59, 43)),
    (1.50, (81, 69, 60, 45)),
)


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(samples, midi, center_seconds, duration_seconds, amplitude, harmonic):
    start = max(0, int((center_seconds - duration_seconds / 2.0) * SAMPLE_RATE))
    end = min(len(samples), int((center_seconds + duration_seconds / 2.0) * SAMPLE_RATE))
    freq = midi_frequency(midi)
    for index in range(start, end):
        rel = (index - start) / max(1, end - start)
        envelope = min(1.0, rel * 12.0, (1.0 - rel) * 12.0)
        phase = 2.0 * math.pi * freq * index / SAMPLE_RATE
        sample = math.sin(phase)
        if harmonic:
            sample += 0.22 * math.sin(phase * 2.0)
        samples[index] += amplitude * envelope * sample


def mix_stems(stems):
    mixed = [0.0 for _ in range(max(len(stem) for stem in stems))]
    gain = 1.0 / math.sqrt(len(stems))
    for index in range(len(mixed)):
        sample = 0.0
        for stem in stems:
            if index < len(stem):
                sample += stem[index]
        mixed[index] = sample * gain
    return mixed


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frames = bytearray()
    for sample in samples:
        frames.extend(struct.pack("<h", int(max(-0.95, min(0.95, sample)) * 32767.0)))
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(bytes(frames))


def encode_var_len(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.insert(0, 0x80 | (value & 0x7F))
        value >>= 7
    return bytes(bytes_out)


def write_track(events):
    track = bytearray()
    previous_tick = 0
    for tick, payload in sorted(events, key=lambda item: (item[0], item[1][0] == 0x80)):
        track.extend(encode_var_len(max(0, tick - previous_tick)))
        track.extend(payload)
        previous_tick = tick
    track.extend(b"\x00\xff\x2f\x00")
    return b"MTrk" + struct.pack(">I", len(track)) + bytes(track)


def write_score_midi(path, part_notes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    division = 480
    ticks_per_second = 960
    tempo_track = write_track([(0, b"\xff\x51\x03\x07\xa1\x20")])
    tracks = [tempo_track]
    for part_index, notes in enumerate(part_notes):
        channel = part_index % 16
        program = PARTS[part_index][1]
        events = [(0, bytes([0xC0 | channel, program]))]
        for start_seconds, end_seconds, midi in notes:
            start_tick = int(round(start_seconds * ticks_per_second))
            end_tick = int(round(end_seconds * ticks_per_second))
            events.append((start_tick, bytes([0x90 | channel, midi, 96])))
            events.append((end_tick, bytes([0x80 | channel, midi, 0])))
        tracks.append(write_track(events))

    data = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), division) + b"".join(tracks)
    with open(path, "wb") as midi:
        midi.write(data)


def write_metadata(piece_dir, index):
    with open(os.path.join(piece_dir, "metadata.json"), "w", encoding="utf-8") as metadata:
        json.dump(
            {
                "fixture": True,
                "dataset": "CocoChorales",
                "ensemble": "random",
                "piece_id": f"fixture_{index:05d}",
                "parts": [part[0] for part in PARTS],
            },
            metadata,
            sort_keys=True,
        )


def main(argv):
    if len(argv) != 2:
        print("usage: generate_cocochorales_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = argv[1]
    for index in range(1, PIECE_COUNT + 1):
        piece_id = f"cocochorales_fixture_{index:05d}"
        piece_dir = os.path.join(root, "train", piece_id)
        stems_dir = os.path.join(piece_dir, "stems")
        os.makedirs(stems_dir, exist_ok=True)

        transpose = index % 6
        stems = [[0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))] for _ in PARTS]
        part_notes = [[] for _ in PARTS]
        for center, chord in WINDOWS:
            for part_index, midi in enumerate(chord):
                shifted = midi + transpose
                start = center - 0.17
                end = center + 0.17
                add_tone(stems[part_index], shifted, center, 0.34, 0.20, part_index != 3)
                part_notes[part_index].append((start, end, shifted))

        write_metadata(piece_dir, index)
        write_score_midi(os.path.join(piece_dir, "score.mid"), part_notes)
        for part_index, (part_name, _, _) in enumerate(PARTS):
            write_wav(os.path.join(stems_dir, f"{part_name}.wav"), stems[part_index])
        write_wav(os.path.join(piece_dir, "mixture.wav"), mix_stems(stems))

    print(f"generate_cocochorales_fixture: wrote {PIECE_COUNT} CocoChorales-shaped pieces to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
