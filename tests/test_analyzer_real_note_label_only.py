#!/usr/bin/env python3
"""Exercise label-only routing export without treating a predicted pitch as ground truth."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import wave


ROOT = Path(__file__).resolve().parents[1]


def write_tone(path: Path, *, frequency: float = 440.0, seconds: float = 1.5) -> None:
    sample_rate = 44_100
    frames = bytearray()
    for index in range(int(sample_rate * seconds)):
        value = int(0.55 * 32767 * math.sin(2.0 * math.pi * frequency * index / sample_rate))
        frames.extend(value.to_bytes(2, "little", signed=True))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(frames)


def main() -> int:
    binary = ROOT / "build" / "analyzer_real_note_samples"
    if not binary.is_file():
        raise SystemExit(f"missing {binary}; run the Make target that builds it first")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_tone(root / "tone.wav")
        (root / "manifest.tsv").write_text(
            "sample_id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\n"
            "labelled-tone\tpiano\tirmas\tirmas/piano\t60\tC4\ttone.wav\n",
            encoding="utf-8",
        )
        attributes = root / "attributes.tsv"
        environment = os.environ | {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(root),
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_LABEL_ONLY": "1",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(attributes),
        }
        completed = subprocess.run([str(binary)], cwd=ROOT, env=environment, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        with attributes.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source, delimiter="\t"))
        assert rows, "label-only mode must export the runtime candidates it evaluates"
        assert all(row["family"] == "piano" for row in rows)
        assert all(row["source"] == "irmas/piano" for row in rows)
        assert all(row["status"] == "hit" for row in rows)
        assert all(row["expected_midi"] != "60" for row in rows), (
            "label-only rows must retain each runtime candidate pitch instead of the manifest placeholder"
        )
    print("analyzer_real_note_label_only: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
