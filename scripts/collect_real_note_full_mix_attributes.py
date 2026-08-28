#!/usr/bin/env python3
"""Export full-mix ownership evidence for the existing real-note corpus."""

from __future__ import annotations

import os
import pathlib
import subprocess


ROOT = pathlib.Path("build/real_note_samples")
OUTPUT = pathlib.Path("build/real_note_full_mix_attributes.tsv")


def binary() -> pathlib.Path:
    candidates = sorted(path for path in pathlib.Path("build").rglob("analyzer_real_note_samples")
                        if path.is_file() and os.access(path, os.X_OK))
    if not candidates:
        raise SystemExit("analyzer_real_note_samples is not built")
    return candidates[0]


def main() -> int:
    if not (ROOT / "manifest.tsv").is_file():
        raise SystemExit("real-note fixture manifest is missing")
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(OUTPUT),
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "100000",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
    })
    print(f"fixture root: {ROOT}")
    print(f"attribute TSV: {OUTPUT}")
    return subprocess.run([str(binary())], env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
