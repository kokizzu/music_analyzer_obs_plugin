#!/usr/bin/env python3
import csv
import math
import os
import struct
import sys
import wave


TRACK_COUNT = 20
SAMPLE_RATE = 44100
SEGMENT_SECONDS = 0.42
GAP_SECONDS = 0.08

MELODIES = (
    (60, 64, 67, 72),
    (62, 65, 69, 74),
    (64, 67, 71, 76),
    (59, 62, 67, 71),
)


def midi_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            frames.extend(struct.pack("<h", int(max(-0.95, min(0.95, sample)) * 32767.0)))
        audio.writeframes(bytes(frames))


def tone_track(notes, amplitude, harmonic=False):
    total_seconds = 0.10 + len(notes) * (SEGMENT_SECONDS + GAP_SECONDS) + 0.20
    samples = [0.0] * int(round(total_seconds * SAMPLE_RATE))
    phase = 0.0
    for index, midi in enumerate(notes):
        start = int(round((0.10 + index * (SEGMENT_SECONDS + GAP_SECONDS)) * SAMPLE_RATE))
        end = int(round((0.10 + index * (SEGMENT_SECONDS + GAP_SECONDS) + SEGMENT_SECONDS) * SAMPLE_RATE))
        freq = midi_hz(midi)
        step = 2.0 * math.pi * freq / SAMPLE_RATE
        for frame in range(start, min(end, len(samples))):
            age = frame - start
            remaining = end - frame
            attack = min(1.0, age / float(max(1, int(0.020 * SAMPLE_RATE))))
            release = min(1.0, remaining / float(max(1, int(0.035 * SAMPLE_RATE))))
            envelope = min(attack, release)
            sample = math.sin(phase)
            if harmonic:
                sample += 0.30 * math.sin(phase * 2.0)
            samples[frame] = sample * amplitude * envelope
            phase += step
    return samples


def mix_tracks(tracks):
    frame_count = max(len(track) for track in tracks)
    gain = 1.0 / math.sqrt(len(tracks))
    mixed = []
    for frame in range(frame_count):
        sample = 0.0
        for track in tracks:
            if frame < len(track):
                sample += track[frame]
        mixed.append(sample * gain)
    return mixed


def write_melody(path, notes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as melody_file:
        writer = csv.writer(melody_file)
        writer.writerow(["time", "frequency"])
        for index, midi in enumerate(notes):
            start = 0.10 + index * (SEGMENT_SECONDS + GAP_SECONDS)
            freq = midi_hz(midi)
            frame = 0
            while True:
                time_value = start + frame * 0.05
                if time_value > start + SEGMENT_SECONDS - 0.025:
                    break
                writer.writerow([f"{time_value:.3f}", f"{freq:.6f}"])
                frame += 1


def write_track(root, annotations, index):
    track_id = f"Artist_Song{index:02d}"
    track_dir = os.path.join(root, "MedleyDB", track_id)
    melody = MELODIES[(index - 1) % len(MELODIES)]
    harmony = tuple(note - 12 if note >= 72 else note - 5 for note in melody)
    stem_1 = tone_track(melody, 0.35, harmonic=True)
    stem_2 = tone_track(harmony, 0.18, harmonic=False)
    write_wav(os.path.join(track_dir, f"{track_id}_MIX.wav"), mix_tracks((stem_1, stem_2)))
    write_wav(os.path.join(track_dir, f"{track_id}_STEM_01.wav"), stem_1)
    write_wav(os.path.join(track_dir, "stems", f"{track_id}_STEM_02.wav"), stem_2)
    write_melody(os.path.join(annotations, f"{track_id}_MELODY1.csv"), melody)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_medleydb_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    annotations = os.path.join(root, "Annotations")
    os.makedirs(root, exist_ok=True)
    for index in range(1, TRACK_COUNT + 1):
        write_track(root, annotations, index)
    print(f"generate_medleydb_fixture: wrote {TRACK_COUNT} tracks to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
