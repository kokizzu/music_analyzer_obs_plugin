#!/usr/bin/env python3
"""Regression controls for low bass fundamentals leaking into the keyboard grid."""

from __future__ import annotations

import csv
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "build" / "real_instrument_expansion_samples"
BINARY = ROOT / "build" / "analyzer_real_note_samples"
BASS_ID = "idmt_bass_lines_004_006_E1_FS_NO"
PIANO_ID = "Piano.mf.B0"


def attributes(sample_id: str) -> list[dict[str, str]]:
    with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as handle:
        path = Path(handle.name)
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": "0",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(SAMPLES),
            "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": sample_id,
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(path),
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "1000000",
            "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        }
    )
    try:
        completed = subprocess.run(
            (str(BINARY),), cwd=ROOT, env=environment, text=True, capture_output=True, check=False
        )
        if completed.returncode:
            raise RuntimeError(completed.stdout + completed.stderr)
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle, delimiter="\t"))
    finally:
        path.unlink(missing_ok=True)


def main() -> int:
    if not BINARY.is_file() or not (SAMPLES / "manifest.tsv").is_file():
        raise SystemExit("missing analyzer binary or real-instrument fixture manifest")
    bass = attributes(BASS_ID)
    piano = attributes(PIANO_ID)
    if not bass or "E1" not in bass[0]["bass_notes"]:
        raise SystemExit("IDMT E1 bass control did not reach the bass grid")
    if "E1" in bass[0]["piano_notes"]:
        raise SystemExit("IDMT E1 bass fundamental leaked into the piano grid")
    if not piano or piano[0]["piano_notes"] == "--":
        raise SystemExit("low Iowa piano control lost its keyboard grid")
    print("idmt-bass-keyboard-routing: bass fundamental isolated; low piano retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
