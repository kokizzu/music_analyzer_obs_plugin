#!/usr/bin/env python3
import math
import os
import struct
import sys
import wave


TRACK_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
WINDOWS = [
    (0.30, [60, 64, 67, 72]),
    (0.70, [62, 65, 69, 74]),
    (1.10, [55, 59, 62, 67]),
    (1.50, [57, 60, 64, 69]),
]
STEMS = (
    ("S00", "Piano"),
    ("S01", "Bass"),
    ("S02", "Guitar"),
    ("S03", "Drums"),
)


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


def write_midi(path, notes, program):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    division = 480
    ticks_per_second = 960
    events = [(0, b"\xff\x51\x03\x07\xa1\x20"), (0, bytes([0xC0, program]))]
    for start_seconds, end_seconds, midi in notes:
        start_tick = int(round(start_seconds * ticks_per_second))
        end_tick = int(round(end_seconds * ticks_per_second))
        events.append((start_tick, bytes([0x90, midi, 96])))
        events.append((end_tick, bytes([0x80, midi, 0])))
    events.sort(key=lambda item: (item[0], item[1][0] == 0x80))

    track = bytearray()
    previous_tick = 0
    for tick, payload in events:
        track.extend(encode_var_len(max(0, tick - previous_tick)))
        track.extend(payload)
        previous_tick = tick
    track.extend(b"\x00\xff\x2f\x00")

    data = b"MThd" + struct.pack(">IHHH", 6, 1, 1, division) + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)
    with open(path, "wb") as midi:
        midi.write(data)


def write_metadata(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["stems:\n"]
    for stem_name, instrument_class in STEMS:
        lines.extend(
            [
                f"  {stem_name}:\n",
                "    audio_rendered: true\n",
                f"    inst_class: {instrument_class}\n",
                f"    is_drum: {'true' if instrument_class == 'Drums' else 'false'}\n",
            ]
        )
    with open(path, "w", encoding="utf-8") as metadata:
        metadata.writelines(lines)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_slakh_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    for index in range(1, TRACK_COUNT + 1):
        split = "train" if index <= TRACK_COUNT // 2 else "validation"
        track_dir = os.path.join(root, split, f"Track{index:05d}")
        mix_samples = [0.0 for _ in range(int(DURATION_SECONDS * SAMPLE_RATE))]
        stem_samples = [[0.0 for _ in mix_samples] for _ in STEMS]
        stem_notes = [[] for _ in STEMS]
        all_notes = []
        transpose = index % 12
        for center, chord in WINDOWS:
            for stem_index, midi in enumerate(chord):
                shifted = midi + transpose
                start = center - 0.17
                end = center + 0.17
                add_tone(stem_samples[stem_index], shifted, center, 0.34, 0.20)
                add_tone(mix_samples, shifted, center, 0.34, 0.18)
                stem_notes[stem_index].append((start, end, shifted))
                all_notes.append((start, end, shifted))

        write_metadata(os.path.join(track_dir, "metadata.yaml"))
        write_wav(os.path.join(track_dir, "mix.wav"), mix_samples)
        write_midi(os.path.join(track_dir, "all_src.mid"), all_notes, 0)
        for stem_index, (stem_name, _) in enumerate(STEMS):
            write_wav(os.path.join(track_dir, "stems", f"{stem_name}.wav"), stem_samples[stem_index])
            write_midi(os.path.join(track_dir, "MIDI", f"{stem_name}.mid"), stem_notes[stem_index], stem_index)
    print(f"generate_slakh_fixture: wrote {TRACK_COUNT} Slakh-shaped tracks to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
