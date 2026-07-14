#!/usr/bin/env python3
import math
import os
import struct
import sys
import wave


PIECE_COUNT = 20
SAMPLE_RATE = 44100
SEGMENT_SECONDS = 0.55
GAP_SECONDS = 0.10
SOURCE_NAMES = ("Violin_1", "Viola", "Clarinet", "Cello")
SOURCE_PROGRAMS = (40, 41, 71, 42)
PROGRESSIONS = (
    ((72, 67, 64, 48), (74, 69, 65, 50), (76, 71, 67, 52), (72, 67, 64, 48)),
    ((69, 64, 60, 45), (71, 67, 62, 47), (72, 69, 64, 48), (69, 64, 60, 45)),
    ((77, 72, 69, 53), (76, 71, 67, 52), (74, 69, 65, 50), (72, 67, 64, 48)),
    ((74, 69, 65, 50), (74, 71, 67, 55), (76, 67, 60, 48), (72, 69, 65, 53)),
)


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


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


def source_samples(piece_index, source_index):
    progression = PROGRESSIONS[piece_index % len(PROGRESSIONS)]
    total_seconds = len(progression) * (SEGMENT_SECONDS + GAP_SECONDS) + 0.25
    frame_count = int(round(total_seconds * SAMPLE_RATE))
    samples = [0.0] * frame_count
    phase = 0.0
    amplitude = 0.21 - source_index * 0.014
    for segment_index, notes in enumerate(progression):
        start = int(round((0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)) * SAMPLE_RATE))
        end = int(round((0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS) + SEGMENT_SECONDS) * SAMPLE_RATE))
        step = 2.0 * math.pi * midi_hz(notes[source_index]) / SAMPLE_RATE
        for frame in range(start, min(end, frame_count)):
            age = frame - start
            remaining = end - frame
            attack = min(1.0, age / float(max(1, int(0.025 * SAMPLE_RATE))))
            release = min(1.0, remaining / float(max(1, int(0.045 * SAMPLE_RATE))))
            samples[frame] = math.sin(phase) * amplitude * min(attack, release)
            phase += step
    return samples


def write_score(path, piece_index):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    progression = PROGRESSIONS[piece_index % len(PROGRESSIONS)]
    with open(path, "w", encoding="utf-8") as score_file:
        score_file.write("start end pitch instrument\n")
        for segment_index, notes in enumerate(progression):
            start = 0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)
            end = start + SEGMENT_SECONDS
            for source_index, note in enumerate(notes):
                score_file.write(f"{start:.3f} {end:.3f} {note} {SOURCE_PROGRAMS[source_index]}\n")


def write_fixture(root):
    data_root = join_path(root, "SynthSOD-data")
    score_root = join_path(root, "SynthSOD-aligned-scores")
    for piece in range(1, PIECE_COUNT + 1):
        piece_id = f"SYNTHSOD_{piece:03d}"
        close_mic = join_path(data_root, piece_id, "Close Mic")
        tree = join_path(data_root, piece_id, "Tree")
        for source_index, source_name in enumerate(SOURCE_NAMES):
            write_wav(join_path(close_mic, f"{source_name}.wav"), source_samples(piece - 1, source_index))
        write_wav(join_path(tree, "mix.wav"), source_samples(piece - 1, 0))
        write_score(join_path(score_root, f"{piece_id}.txt"), piece - 1)


def main(argv):
    if len(argv) != 2:
        print("usage: generate_synthsod_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    write_fixture(argv[1])
    print(f"generate_synthsod_fixture: wrote {PIECE_COUNT} SynthSOD-shaped pieces to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
