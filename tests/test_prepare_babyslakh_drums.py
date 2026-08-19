#!/usr/bin/env python3
"""Regression test for the BabySlakh E-GMD-shaped drum fixture adapter."""

from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "prepare_babyslakh_drums.py"
SPEC = importlib.util.spec_from_file_location("prepare_babyslakh_drums", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))
SPEC.loader.exec_module(MODULE)


def midi(note: int) -> bytes:
    track = bytes([0x00, 0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20, 0x00, 0x99, note, 100,
                   0x18, 0x89, note, 0, 0x00, 0xFF, 0x2F, 0x00])
    return b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") + (1).to_bytes(2, "big") + \
        (480).to_bytes(2, "big") + b"MTrk" + len(track).to_bytes(4, "big") + track


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        wrapper = Path(temporary) / "published-wrapper"
        published_root = wrapper / "babyslakh_16k"
        published_root.mkdir(parents=True)
        assert MODULE.resolve_root(wrapper) == published_root

        root = Path(temporary) / "opaque-archive-wrapper"
        track = root / "train" / "Track00001"
        (track / "MIDI").mkdir(parents=True)
        (track / "metadata.yaml").write_text(
            "stems:\n  S00:\n    is_drum: true\n  S01:\n    is_drum: false\n", encoding="utf-8"
        )
        (track / "MIDI" / "S00.mid").write_bytes(midi(36))
        (track / "MIDI" / "S01.mid").write_bytes(midi(60))
        with wave.open(str(track / "mix.wav"), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(16000)
            audio.writeframes(b"\0\0" * 1600)
        output = Path(temporary) / "fixture"
        subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root.parent), "--output", str(output), "--min-recordings", "1"],
            check=True,
        )
        rows = list(csv.DictReader((output / "e-gmd-v1.0.0.csv").open(encoding="utf-8")))
        assert len(rows) == 1, rows
        assert (output / rows[0]["audio_filename"]).is_symlink(), rows
        assert MODULE.parse_drum_midi(output / rows[0]["midi_filename"]) == [(0.0, 36, 100)]
    print("test_prepare_babyslakh_drums: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
