#!/usr/bin/env python3
"""Convert real DCS SATB recordings and aligned score CSVs to a prepared manifest."""
import argparse
import csv
import json
import shutil
from pathlib import Path

ROLES = ("S", "A", "T", "B")


def score_rows(path):
    rows = []
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.reader(source):
            try:
                start, end, note = float(row[0]), float(row[1]), int(float(row[2]))
            except (IndexError, ValueError):
                continue
            if end > start and 21 <= note <= 108:
                rows.append((start, end, note))
    return rows


def write_notes(path, rows):
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("start", "end", "note"))
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    score_root = args.root / "annotations_csv_scorerepresentation"
    audio_root = args.root / "audio_wav_22050_mono"
    if not score_root.is_dir() or not audio_root.is_dir():
        raise SystemExit("prepare_dagstuhl_choirset_manifest: missing extracted score/audio directories")
    shutil.rmtree(args.output, ignore_errors=True)
    notes_root = args.output / "scores"
    notes_root.mkdir(parents=True)
    pieces = []
    suffix = "_Stereo_STM_S.csv"
    for soprano_score in sorted(score_root.glob(f"*{suffix}")):
        prefix = soprano_score.name[: -len(suffix)]
        sources = []
        for role_index, role in enumerate(ROLES):
            score = score_root / f"{prefix}_Stereo_STM_{role}.csv"
            candidates = sorted(audio_root.glob(f"{prefix}_{role}[0-9]_LRX.wav"))
            rows = score_rows(score) if score.is_file() else []
            if not candidates or not rows:
                sources = []
                break
            note_path = notes_root / f"{prefix}_{role}.csv"
            write_notes(note_path, rows)
            sources.append({"audio": str(candidates[0].resolve()), "notes": str(note_path.resolve()),
                            "instrument": 52 + role_index})
        if len(sources) == 4:
            pieces.append({"id": prefix, "sources": sources})
    (args.output / "manifest.json").write_text(json.dumps({"pieces": pieces}, indent=2) + "\n", encoding="utf-8")
    print(f"prepare_dagstuhl_choirset_manifest: complete={len(pieces)} output={args.output}")
    return 0 if len(pieces) >= 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
