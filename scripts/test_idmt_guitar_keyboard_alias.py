#!/usr/bin/env python3
"""Regression test for low guitar E2 incorrectly restored into Keyboard."""

import csv
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path("build/real_instrument_expansion_samples")
BINARY = Path("build/analyzer_real_note_samples")
GUITAR_ID = "idmt_guitar_G53-40100-1111-00001_0001_E2_PK_NO"
GUITAR_G2_ID = "idmt_guitar_G53-43103-1111-00004_0001_G2_PK_NO"


def midi_label(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def low_piano_control() -> tuple[str, str]:
    with (ROOT / "manifest.tsv").open(encoding="utf-8", newline="") as manifest:
        for row in csv.DictReader(manifest, delimiter="\t"):
            midi = int(row["midi"])
            if row["family"] == "piano" and 40 <= midi <= 47:
                return row["id"], midi_label(midi)
    raise RuntimeError("no low-piano control in real instrument expansion manifest")


def debug_output(sample_id: str) -> str:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
        "MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID": sample_id,
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "100",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES": "100",
    })
    completed = subprocess.run([str(BINARY)], env=environment, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed.stdout + completed.stderr


def row_has_note(line: str, row: str, note: str) -> bool:
    matched = re.search(rf"\b{row}=([^\[]*)\[", line)
    return bool(matched and note in matched.group(1).split())


def debug_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.startswith("debug sample=")]


def main() -> int:
    if not BINARY.is_file() or not (ROOT / "manifest.tsv").is_file():
        raise RuntimeError("missing test binary or real instrument expansion fixture root")

    guitar_lines = debug_lines(debug_output(GUITAR_ID))
    if not guitar_lines:
        raise RuntimeError("missing guitar debug output")
    if not any(row_has_note(line, "guitar", "E2") for line in guitar_lines):
        raise RuntimeError("IDMT E2 guitar control is no longer detected in Guitar")
    if any(row_has_note(line, "keys", note) for line in guitar_lines for note in ("E1", "E2", "E3")):
        raise RuntimeError("IDMT E2 guitar is still projected into Keyboard octaves")

    guitar_g2_lines = debug_lines(debug_output(GUITAR_G2_ID))
    if not guitar_g2_lines:
        raise RuntimeError("missing G2 guitar debug output")
    if not any(row_has_note(line, "guitar", "G2") for line in guitar_g2_lines):
        raise RuntimeError("IDMT G2 guitar control is no longer detected in Guitar")
    if any(row_has_note(line, "keys", note) for line in guitar_g2_lines for note in ("G1", "G2", "G3")):
        raise RuntimeError("IDMT G2 guitar is still projected into Keyboard octaves")

    piano_id, piano_note = low_piano_control()
    piano_lines = debug_lines(debug_output(piano_id))
    if not piano_lines:
        raise RuntimeError(f"missing low-piano debug output for {piano_id}")
    if not any(row_has_note(line, "keys", piano_note) for line in piano_lines):
        raise RuntimeError(f"low-piano control {piano_id} no longer reaches Keyboard as {piano_note}")

    print(f"idmt-guitar-keyboard-alias: E2/G2 stay Guitar; {piano_id} retains Keyboard {piano_note}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"idmt-guitar-keyboard-alias: {error}", file=sys.stderr)
        raise SystemExit(1)
