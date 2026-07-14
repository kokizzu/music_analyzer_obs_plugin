#!/usr/bin/env python3
import csv
import json
import math
import os
import struct
import sys
import wave


PIECE_COUNT = 20
SAMPLE_RATE = 44100
SEGMENT_SECONDS = 0.55
GAP_SECONDS = 0.10
SOURCE_NAMES = ("violin", "clarinet", "bassoon", "cello")
PROGRESSIONS = (
    ((72, 67, 60, 48), (72, 65, 60, 53), (71, 67, 62, 55), (72, 64, 60, 48)),
    ((72, 69, 64, 57), (74, 69, 62, 50), (74, 67, 62, 55), (72, 67, 64, 48)),
    ((77, 69, 65, 53), (77, 70, 65, 58), (76, 70, 64, 48), (77, 69, 65, 53)),
    ((74, 67, 62, 55), (76, 67, 64, 52), (76, 67, 60, 48), (78, 66, 62, 50)),
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
    amplitude = 0.22 - source_index * 0.018
    for segment_index, notes in enumerate(progression):
        start = int(round((0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)) * SAMPLE_RATE))
        end = int(round((0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS) + SEGMENT_SECONDS) * SAMPLE_RATE))
        step = 2.0 * math.pi * midi_hz(notes[source_index]) / SAMPLE_RATE
        for frame in range(start, min(end, frame_count)):
            age = frame - start
            remaining = end - frame
            attack = min(1.0, age / float(max(1, int(0.025 * SAMPLE_RATE))))
            release = min(1.0, remaining / float(max(1, int(0.040 * SAMPLE_RATE))))
            samples[frame] = math.sin(phase) * amplitude * min(attack, release)
            phase += step
    return samples


def write_notes_csv(path, piece_index, source_index, instrument):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    progression = PROGRESSIONS[piece_index % len(PROGRESSIONS)]
    with open(path, "w", newline="", encoding="utf-8") as note_file:
        writer = csv.DictWriter(note_file, fieldnames=("start", "end", "instrument", "note"))
        writer.writeheader()
        for segment_index, notes in enumerate(progression):
            start = 0.10 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)
            end = start + SEGMENT_SECONDS
            writer.writerow(
                {
                    "start": f"{start:.3f}",
                    "end": f"{end:.3f}",
                    "instrument": instrument,
                    "note": notes[source_index],
                }
            )


def write_fixture(root):
    os.makedirs(root, exist_ok=True)
    pieces = []
    for piece in range(1, PIECE_COUNT + 1):
        piece_id = f"PMT{piece:03d}"
        sources = []
        for source_index, source_name in enumerate(SOURCE_NAMES):
            audio_path = join_path("audio", piece_id, f"{source_name}.wav")
            notes_path = join_path("annotations", piece_id, f"{source_name}.csv")
            instrument = 40 + source_index
            write_wav(join_path(root, audio_path), source_samples(piece - 1, source_index))
            write_notes_csv(join_path(root, notes_path), piece - 1, source_index, instrument)
            sources.append(
                {
                    "name": source_name,
                    "audio": audio_path,
                    "notes": notes_path,
                    "instrument": instrument,
                }
            )
        pieces.append({"id": piece_id, "sources": sources})

    with open(join_path(root, "manifest.json"), "w", encoding="utf-8") as manifest_file:
        json.dump({"version": 1, "pieces": pieces}, manifest_file, indent=2, sort_keys=True)
        manifest_file.write("\n")


def main(argv):
    if len(argv) != 2:
        print("usage: generate_prepared_multitrack_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    write_fixture(argv[1])
    print(f"generate_prepared_multitrack_fixture: wrote {PIECE_COUNT} prepared multitrack pieces to {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
