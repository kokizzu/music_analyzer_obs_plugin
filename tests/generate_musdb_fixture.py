#!/usr/bin/env python3
import math
import os
import struct
import sys
import wave


TRACK_COUNT = 20
SAMPLE_RATE = 44100
SECONDS = 1.0
STEMS = ("mixture", "drums", "bass", "other", "vocals")


def write_wav(path, freq):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frame_count = int(SAMPLE_RATE * SECONDS)
    frames = bytearray()
    for index in range(frame_count):
        sample = 0.18 * math.sin(2.0 * math.pi * freq * index / SAMPLE_RATE)
        encoded = struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767.0))
        frames.extend(encoded)
        frames.extend(encoded)
    with wave.open(path, "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(bytes(frames))


def main(argv):
    if len(argv) != 2:
        print("usage: generate_musdb_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    for index in range(1, TRACK_COUNT + 1):
        split = "train" if index <= TRACK_COUNT // 2 else "test"
        track_dir = os.path.join(root, split, f"fixture_track_{index:03d}")
        for stem_index, stem in enumerate(STEMS):
            write_wav(os.path.join(track_dir, f"{stem}.wav"), 110.0 + index * 7.0 + stem_index * 23.0)
    print(f"generate_musdb_fixture: wrote {TRACK_COUNT} MUSDB-shaped tracks to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
