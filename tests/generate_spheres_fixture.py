#!/usr/bin/env python3
import os
import struct
import sys
import wave


PIECES = ("Mozart_Symphony_No_40", "Tchaikovsky_Romeo_And_Juliet")
FOLDERS = ("Stereo Mix", "Main L")
SOURCES = ("Violin_I", "Cello")


def write_wav(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sample_rate = 8000
    frame_count = sample_rate
    with wave.open(path, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(b"".join(struct.pack("<h", 0) for _ in range(frame_count)))


def main(argv):
    if len(argv) != 2:
        print("usage: generate_spheres_fixture.py OUT_DIR", file=sys.stderr)
        return 2
    root = argv[1]
    os.makedirs(root, exist_ok=True)
    for piece in PIECES:
        for folder in FOLDERS:
            for source in SOURCES:
                write_wav(os.path.join(root, piece, folder, f"{source}.wav"))
    print(f"generate_spheres_fixture: wrote {len(PIECES)} Spheres-shaped pieces to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
