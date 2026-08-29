#!/usr/bin/env python3
"""Export full-mix vocal fixture attributes for data-driven classifier analysis."""

import os
from pathlib import Path
import subprocess


ROOT = Path("build/InstrumentSamples/build-cache/real_note_samples")
OUTPUT = Path("build/real_note_vocal_attributes.tsv")
BINARY = Path("build/analyzer_real_note_samples")


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"missing external real-note fixture root: {ROOT}")
    if not BINARY.is_file():
        raise SystemExit(f"missing test binary: {BINARY}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.unlink(missing_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(ROOT),
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": "vocals",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(OUTPUT),
        }
    )
    subprocess.run([str(BINARY)], check=True, env=environment)
    print(OUTPUT)


if __name__ == "__main__":
    main()
