#!/usr/bin/env python3
import math
import os
import struct
import sys
import wave


TRACK_COUNT = 20
SAMPLE_RATE = 44100
SECONDS = 1.0
STEMS = (
    ("S00", "Piano"),
    ("S01", "Bass"),
    ("S02", "Guitar"),
    ("S03", "Drums"),
)


def write_wav(path, freq):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frame_count = int(SAMPLE_RATE * SECONDS)
    frames = bytearray()
    for index in range(frame_count):
        sample = 0.16 * math.sin(2.0 * math.pi * freq * index / SAMPLE_RATE)
        encoded = struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767.0))
        frames.extend(encoded)
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(bytes(frames))


def write_minimal_midi(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (
        b"MThd"
        + struct.pack(">IHHH", 6, 1, 1, 480)
        + b"MTrk"
        + struct.pack(">I", 4)
        + b"\x00\xff\x2f\x00"
    )
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
        write_metadata(os.path.join(track_dir, "metadata.yaml"))
        write_wav(os.path.join(track_dir, "mix.wav"), 220.0 + index)
        write_minimal_midi(os.path.join(track_dir, "all_src.mid"))
        for stem_index, (stem_name, _) in enumerate(STEMS):
            write_wav(os.path.join(track_dir, "stems", f"{stem_name}.wav"), 110.0 + index * 5.0 + stem_index * 37.0)
            write_minimal_midi(os.path.join(track_dir, "MIDI", f"{stem_name}.mid"))
    print(f"generate_slakh_fixture: wrote {TRACK_COUNT} Slakh-shaped tracks to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
