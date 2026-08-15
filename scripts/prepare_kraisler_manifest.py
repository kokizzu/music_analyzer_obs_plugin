#!/usr/bin/env python3
"""Import KRAISLER dry piano/violin stems and aligned note truth."""

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "tests"))
from prepare_slakh_musicnet_fixture import parse_midi_notes  # noqa: E402


PIANO_PROGRAM = 0
VIOLIN_PROGRAM = 40


def note_rows(path: Path) -> list[tuple[float, float, int]]:
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            try:
                start = float(row["onset"])
                end = float(row["offset"])
                midi = int(float(row["midi"]))
            except (KeyError, TypeError, ValueError):
                continue
            if end - start >= 0.035 and 21 <= midi <= 108:
                rows.append((start, end, midi))
    return rows


def write_notes(path: Path, rows: list[tuple[float, float, int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("start", "end", "note"))
        writer.writerows(rows)


def find_dir(root: Path, name: str) -> Path:
    matches = sorted(path for path in root.rglob(name) if path.is_dir())
    if len(matches) != 1:
        raise ValueError(f"expected one {name} directory, found {len(matches)}")
    return matches[0]


def prepare(root: Path, output: Path, minimum_tracks: int) -> int:
    wav_root = find_dir(root, "performance_wav")
    midi_root = find_dir(root, "performance_midi")
    annotation_root = find_dir(root, "annotation_csv")
    pieces = []
    staged: list[tuple[str, Path, Path, list[tuple[float, float, int]], list[tuple[float, float, int]]]] = []
    for piano_audio in sorted(wav_root.glob("??_PF_dry.wav")):
        track_id = piano_audio.name[:2]
        violin_audio = wav_root / f"{track_id}_VN_dry.wav"
        piano_midi = midi_root / f"{track_id}_PF.mid"
        violin_notes = annotation_root / f"{track_id}_notes_VN.csv"
        if not violin_audio.is_file() or not piano_midi.is_file() or not violin_notes.is_file():
            continue
        try:
            piano_rows = [(start, end, midi) for start, end, _, midi in parse_midi_notes(piano_midi, PIANO_PROGRAM)]
            violin_rows = note_rows(violin_notes)
        except (OSError, ValueError, csv.Error, UnicodeDecodeError):
            continue
        if piano_rows and violin_rows:
            staged.append((track_id, piano_audio, violin_audio, piano_rows, violin_rows))
    if len(staged) < minimum_tracks:
        raise ValueError(f"expected at least {minimum_tracks} complete dry KRAISLER tracks, found {len(staged)}")
    shutil.rmtree(output, ignore_errors=True)
    notes_root = output / "scores"
    notes_root.mkdir(parents=True)
    for track_id, piano_audio, violin_audio, piano_rows, violin_rows in staged:
        piano_path = notes_root / f"{track_id}_PF.csv"
        violin_path = notes_root / f"{track_id}_VN.csv"
        write_notes(piano_path, piano_rows)
        write_notes(violin_path, violin_rows)
        pieces.append(
            {
                "id": f"kraisler_{track_id}_dry",
                "configuration": "dry",
                "sources": [
                    {"audio": str(piano_audio.resolve()), "notes": str(piano_path.resolve()), "instrument": PIANO_PROGRAM},
                    {"audio": str(violin_audio.resolve()), "notes": str(violin_path.resolve()), "instrument": VIOLIN_PROGRAM},
                ],
            }
        )
    (output / "manifest.json").write_text(json.dumps({"pieces": pieces}, indent=2) + "\n", encoding="utf-8")
    return len(pieces)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-tracks", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        complete = prepare(args.root, args.output, args.minimum_tracks)
    except (OSError, ValueError, csv.Error, UnicodeDecodeError) as exc:
        print(f"prepare_kraisler_manifest: {exc}")
        return 1
    print(f"prepare_kraisler_manifest: complete={complete} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
