#!/usr/bin/env python3
import math
import os
import shutil
import struct
import sys
import wave


SAMPLE_RATE = 48000
SECONDS = 4
PIECES = 20
WINDOWS = (
    (0.20, 0.60, 0, False),
    (1.05, 0.60, 5, False),
    (1.90, 0.60, 9, True),
    (2.75, 0.60, 7, False),
)


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def midi_at_or_above(min_midi, pitch_class):
    return min_midi + ((pitch_class - min_midi % 12 + 12) % 12)


def harmonic_sample(midi, amp, index):
    value = 0.0
    for harmonic, scale in ((1, 1.0), (2, 0.42), (3, 0.22), (4, 0.12), (5, 0.06)):
        value += (
            amp
            * scale
            * math.sin(
                2.0
                * math.pi
                * midi_frequency(midi)
                * harmonic
                * index
                / SAMPLE_RATE
            )
        )
    return value


def write_wav(path, channels):
    frames = []
    for index in range(SAMPLE_RATE * SECONDS):
        value = sum(channel[index] for channel in channels)
        value = max(-0.95, min(0.95, value))
        frames.append(struct.pack("<h", int(value * 32767.0)))

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(b"".join(frames))


def write_piece(root, index):
    root_pitch_class = (index * 5) % 12
    instruments = ["vn", "va", "vc"]
    floors = [72, 67, 60]
    piece_name = f"{index:02d}_Fixture_vn_va_vc"
    piece_dir = os.path.join(root, piece_name)
    os.makedirs(piece_dir, exist_ok=True)

    parts = []
    for track_index, (instrument, floor) in enumerate(zip(instruments, floors), start=1):
        channel = [0.0 for _ in range(SAMPLE_RATE * SECONDS)]
        note_rows = []
        for onset, duration, root_offset, minor in WINDOWS:
            intervals = [0, 3 if minor else 4, 7]
            midi = midi_at_or_above(
                floor, (root_pitch_class + root_offset + intervals[track_index - 1]) % 12
            )
            start = int(onset * SAMPLE_RATE)
            end = int((onset + duration) * SAMPLE_RATE)
            for sample_index in range(start, min(end, len(channel))):
                channel[sample_index] += harmonic_sample(midi, 0.13, sample_index)
            note_rows.append((onset, duration, midi))
        parts.append(channel)

        write_wav(
            os.path.join(
                piece_dir,
                f"AuSep_{track_index}_{instrument}_{index:02d}_Fixture.wav",
            ),
            [channel],
        )
        with open(
            os.path.join(
                piece_dir,
                f"Notes_{track_index}_{instrument}_{index:02d}_Fixture.txt",
            ),
            "w",
            encoding="utf-8",
        ) as notes_file:
            for onset, duration, midi in note_rows:
                notes_file.write(f"{onset:.3f} {midi_frequency(midi):.6f} {duration:.3f}\n")

    write_wav(os.path.join(piece_dir, f"AuMix_{index:02d}_Fixture_vn_va_vc.wav"), parts)


def main():
    if len(sys.argv) != 2:
        print("usage: generate_urmp_fixture.py OUTPUT_DIR", file=sys.stderr)
        return 2

    output_dir = sys.argv[1]
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)
    for index in range(1, PIECES + 1):
        write_piece(output_dir, index)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
