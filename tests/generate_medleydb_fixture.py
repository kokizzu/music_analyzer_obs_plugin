#!/usr/bin/env python3
import csv
import os
import sys


TRACK_COUNT = 20


def write_empty(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as output:
        output.write(b"")


def write_melody(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as melody_file:
        writer = csv.writer(melody_file)
        writer.writerow(["time", "frequency"])
        writer.writerow(["0.000", "440.0"])
        writer.writerow(["0.050", "440.0"])


def write_track(root, annotations, index):
    track_id = f"Artist_Song{index:02d}"
    track_dir = os.path.join(root, "MedleyDB", track_id)
    write_empty(os.path.join(track_dir, f"{track_id}_MIX.wav"))
    write_empty(os.path.join(track_dir, f"{track_id}_STEM_01.wav"))
    write_empty(os.path.join(track_dir, "stems", f"{track_id}_STEM_02.wav"))
    write_melody(os.path.join(annotations, f"{track_id}_MELODY1.csv"))


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
