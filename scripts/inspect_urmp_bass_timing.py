#!/usr/bin/env python3
"""Audit whether URMP double-bass stems include metrical timing truth.

URMP's Notes files are aligned to the recorded stems, whereas Sco MIDI files
are the original score.  A score is not an audio-aligned beat reference, so a
stem qualifies for a tempo benchmark only when the official piece directory
also provides an explicit beat/downbeat/bar annotation.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


TIMING_NAME = re.compile(r"(?:beat|downbeat|bar|tempo)", re.IGNORECASE)


def timing_annotations(piece: Path) -> list[Path]:
    return [path for path in piece.iterdir() if path.is_file() and TIMING_NAME.search(path.name)]


def rows(root: Path) -> list[dict[str, str]]:
    dataset = root / "Dataset"
    if not dataset.is_dir():
        raise ValueError(f"missing URMP Dataset root: {dataset}")
    result: list[dict[str, str]] = []
    for piece in sorted(path for path in dataset.iterdir() if path.is_dir()):
        score = any(piece.glob("Sco_*.mid"))
        timing = timing_annotations(piece)
        for notes in sorted(piece.glob("Notes_*_db_*.txt")):
            audio = notes.with_name(notes.name.replace("Notes_", "AuSep_").replace(".txt", ".wav"))
            audio_and_notes = audio.is_file() and notes.is_file()
            explicit_grid = bool(timing)
            result.append(
                {
                    "piece": piece.name,
                    "notes": notes.name,
                    "audio_aligned_notes": str(int(audio_and_notes)),
                    "score_midi": str(int(score)),
                    "explicit_beat_grid": str(int(explicit_grid)),
                    "qualifies_as_tempo_truth": str(int(audio_and_notes and explicit_grid)),
                    "timing_files": ",".join(path.name for path in timing),
                }
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    found = rows(args.root)
    if not found:
        raise SystemExit("URMP contains no double-bass Notes_*_db_*.txt stems")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(found[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(found)
    pairs = sum(row["audio_aligned_notes"] == "1" for row in found)
    scores = sum(row["score_midi"] == "1" for row in found)
    grids = sum(row["explicit_beat_grid"] == "1" for row in found)
    qualified = sum(row["qualifies_as_tempo_truth"] == "1" for row in found)
    print(
        "urmp_bass_timing: "
        f"stems={len(found)} audio_note_pairs={pairs}/{len(found)} score_midi={scores}/{len(found)} "
        f"explicit_beat_grid={grids}/{len(found)} qualified={qualified}/{len(found)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
