#!/usr/bin/env python3
import json
import math
import os
import struct
import sys
import wave


DEFAULT_EXCERPT_COUNT = 20
SAMPLE_RATE = 44100
DURATION_SECONDS = 2.0
STANDARD_TUNING = [40, 45, 50, 55, 59, 64]
CHORD_WINDOWS = [
    (0.25, "C:maj", [0, 3, 2, 0, 1, 0]),
    (0.75, "G:maj", [3, 2, 0, 0, 0, 3]),
    (1.25, "A:min", [0, 0, 2, 2, 1, 0]),
    (1.65, "F:maj", [1, 3, 3, 2, 1, 1]),
]


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(samples, channel, midi, center_seconds, duration_seconds, amplitude):
    start = max(0, int((center_seconds - duration_seconds / 2.0) * SAMPLE_RATE))
    end = min(len(samples), int((center_seconds + duration_seconds / 2.0) * SAMPLE_RATE))
    freq = midi_frequency(midi)
    for i in range(start, end):
        rel = (i - start) / max(1, end - start)
        envelope = min(1.0, rel * 10.0, (1.0 - rel) * 10.0)
        samples[i][channel] += amplitude * envelope * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)


def write_hex_wav(path, transpose):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frame_count = int(DURATION_SECONDS * SAMPLE_RATE)
    samples = [[0.0 for _ in STANDARD_TUNING] for _ in range(frame_count)]
    for center, _chord, frets in CHORD_WINDOWS:
        for string_index, fret in enumerate(frets):
            midi = STANDARD_TUNING[string_index] + fret + (transpose % 3)
            add_tone(samples, string_index, midi, center, 0.32, 0.38)

    with wave.open(path, "wb") as wav:
        wav.setnchannels(len(STANDARD_TUNING))
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for frame in samples:
            for sample in frame:
                clipped = max(-1.0, min(1.0, sample))
                frames.extend(struct.pack("<h", int(clipped * 32767.0)))
        wav.writeframes(bytes(frames))


def write_mic_wav(path, transpose):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frame_count = int(DURATION_SECONDS * SAMPLE_RATE)
    samples = [0.0 for _ in range(frame_count)]
    for center, _chord, frets in CHORD_WINDOWS:
        for string_index, fret in enumerate(frets):
            midi = STANDARD_TUNING[string_index] + fret + (transpose % 3)
            start = max(0, int((center - 0.16) * SAMPLE_RATE))
            end = min(frame_count, int((center + 0.16) * SAMPLE_RATE))
            freq = midi_frequency(midi)
            for i in range(start, end):
                rel = (i - start) / max(1, end - start)
                envelope = min(1.0, rel * 10.0, (1.0 - rel) * 10.0)
                samples[i] += 0.08 * envelope * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            clipped = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", int(clipped * 32767.0)))
        wav.writeframes(bytes(frames))


def note_annotation_for_string(string_index, transpose):
    data = []
    for center, _chord, frets in CHORD_WINDOWS:
        midi = STANDARD_TUNING[string_index] + frets[string_index] + (transpose % 3)
        data.append(
            {
                "time": round(center - 0.16, 4),
                "duration": 0.32,
                "value": {
                    "midi_note": midi,
                    "string": string_index,
                    "fret": frets[string_index],
                },
                "confidence": 1.0,
            }
        )
    return {
        "namespace": "note_midi",
        "annotation_metadata": {"data_source": f"string_{string_index + 1}"},
        "data": data,
    }


def chord_annotation(transpose, performed):
    data = []
    for center, chord, _frets in CHORD_WINDOWS:
        data.append(
            {
                "time": round(center - 0.2, 4),
                "duration": 0.4,
                "value": chord,
                "confidence": 0.95 if performed else 1.0,
            }
        )
    return {
        "namespace": "chord",
        "annotation_metadata": {"data_source": "performed" if performed else "lead_sheet"},
        "data": data,
    }


def pitch_annotation_for_string(string_index, transpose):
    data = []
    for center, _chord, frets in CHORD_WINDOWS:
        midi = STANDARD_TUNING[string_index] + frets[string_index] + (transpose % 3)
        data.append(
            {
                "time": round(center, 4),
                "duration": 0.1,
                "value": midi_frequency(midi),
                "confidence": 0.9,
            }
        )
    return {
        "namespace": "pitch_contour",
        "annotation_metadata": {"data_source": f"string_{string_index + 1}"},
        "data": data,
    }


def write_jams(path, excerpt_id, transpose):
    annotations = []
    for string_index in range(len(STANDARD_TUNING)):
        annotations.append(note_annotation_for_string(string_index, transpose))
    for string_index in range(len(STANDARD_TUNING)):
        annotations.append(pitch_annotation_for_string(string_index, transpose))
    annotations.append(chord_annotation(transpose, performed=False))
    annotations.append(chord_annotation(transpose, performed=True))
    annotations.append({"namespace": "tempo", "data": [{"time": 0.0, "duration": DURATION_SECONDS, "value": 120.0}]})
    annotations.append({"namespace": "beat_position", "data": []})

    payload = {
        "file_metadata": {
            "title": excerpt_id,
            "duration": DURATION_SECONDS,
        },
        "annotations": annotations,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as jams_file:
        json.dump(payload, jams_file, sort_keys=True)
        jams_file.write("\n")


def write_excerpt(root, index, write_audio_files):
    excerpt_id = f"fixture{index:03d}_comp"
    transpose = index % 12
    write_jams(os.path.join(root, "annotation", excerpt_id + ".jams"), excerpt_id, transpose)
    if write_audio_files:
        write_hex_wav(os.path.join(root, "audio_hex-pickup_debleeded", excerpt_id + "_hex_cln.wav"), transpose)
        write_mic_wav(os.path.join(root, "audio_mono-mic", excerpt_id + "_mic.wav"), transpose)


def write_fixture(root, excerpt_count=DEFAULT_EXCERPT_COUNT, write_audio=True):
    os.makedirs(root, exist_ok=True)
    for index in range(1, excerpt_count + 1):
        write_excerpt(root, index, write_audio)


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: generate_guitarset_fixture.py OUT_DIR [--no-audio]", file=sys.stderr)
        return 2
    write_audio_files = True
    if len(argv) == 3:
        if argv[2] != "--no-audio":
            print("usage: generate_guitarset_fixture.py OUT_DIR [--no-audio]", file=sys.stderr)
            return 2
        write_audio_files = False
    write_fixture(argv[1], write_audio=write_audio_files)
    suffix = "" if write_audio_files else " without audio"
    print(f"generate_guitarset_fixture: wrote {DEFAULT_EXCERPT_COUNT} GuitarSet-shaped excerpts{suffix} to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
