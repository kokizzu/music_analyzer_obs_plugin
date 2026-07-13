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
VOICES = (
    ("CANTUS", 0, 0),
    ("ALTUS", 1, 24),
    ("TENOR", 2, 32),
    ("BASSUS", 3, 40),
)
WINDOWS = [
    (0.30, [72, 64, 55, 48]),
    (0.70, [74, 65, 57, 50]),
    (1.10, [79, 67, 59, 43]),
    (1.50, [81, 69, 60, 45]),
]


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(samples, midi, center_seconds, duration_seconds, amplitude):
    start = max(0, int((center_seconds - duration_seconds / 2.0) * SAMPLE_RATE))
    end = min(len(samples), int((center_seconds + duration_seconds / 2.0) * SAMPLE_RATE))
    freq = midi_frequency(midi)
    for index in range(start, end):
        rel = (index - start) / max(1, end - start)
        envelope = min(1.0, rel * 12.0, (1.0 - rel) * 12.0)
        samples[index] += amplitude * envelope * math.sin(2.0 * math.pi * freq * index / SAMPLE_RATE)


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frames = bytearray()
    for sample in samples:
        encoded = struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767.0))
        frames.extend(encoded)
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


def write_score_midi(path, voice_notes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    division = 480
    ticks_per_second = 960
    tempo_track = write_track([(0, b"\xff\x51\x03\x07\xa1\x20")])
    tracks = [tempo_track]
    for voice_index, notes in enumerate(voice_notes):
        channel = voice_index % 16
        program = VOICES[voice_index][2]
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


def write_metadata(piece_dir, piece_name):
    with open(os.path.join(piece_dir, "score.musicxml"), "w", encoding="utf-8") as score:
        score.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<score-partwise version=\"3.1\"/>\n")
    with open(os.path.join(piece_dir, "beat_times.json"), "w", encoding="utf-8") as beat_times:
        json.dump([0.0, 0.5, 1.0, 1.5, 2.0], beat_times)
    with open(os.path.join(piece_dir, "config.json"), "w", encoding="utf-8") as config:
        json.dump({"fixture": True, "voices": [voice[0] for voice in VOICES]}, config, sort_keys=True)
    with open(os.path.join(piece_dir, "info.json"), "w", encoding="utf-8") as info:
        json.dump(
            {
                "name": piece_name,
                "composer": "fixture",
                "language": "none",
                "voices": [voice[0] for voice in VOICES],
            },
            info,
            sort_keys=True,
        )


def main(argv):
    if len(argv) != 2:
        print("usage: generate_choralsynth_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    for index in range(1, PIECE_COUNT + 1):
        piece_name = f"{index:02d}_Fixture_Chorale"
        piece_dir = os.path.join(root, piece_name)
        os.makedirs(os.path.join(piece_dir, "voices"), exist_ok=True)
        voice_samples = [[0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))] for _ in VOICES]
        voice_notes = [[] for _ in VOICES]
        transpose = index % 6

        for center, chord in WINDOWS:
            for voice_index, midi in enumerate(chord):
                shifted = midi + transpose
                start = center - 0.17
                end = center + 0.17
                add_tone(voice_samples[voice_index], shifted, center, 0.34, 0.22)
                voice_notes[voice_index].append((start, end, shifted))

        write_metadata(piece_dir, piece_name)
        write_score_midi(os.path.join(piece_dir, "score.midi"), voice_notes)
        for voice_index, (voice_name, _, _) in enumerate(VOICES):
            write_wav(os.path.join(piece_dir, "voices", f"{voice_name}.wav"), voice_samples[voice_index])

    print(f"generate_choralsynth_fixture: wrote {PIECE_COUNT} ChoralSynth-shaped pieces to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
