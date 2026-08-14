#!/usr/bin/env python3
"""Regression checks for stable SCMS mixed-vocal clip preparation."""

from __future__ import annotations

import sys
import tempfile
import wave
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_scms_vocal_mix_samples as prepare


def write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(44100)
        output.writeframes(b"\0\0" * 44100)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "source" / "SCMS"
        write_wav(root / "audio" / "Artist_01.wav")
        pitch = root / "pitch" / "Artist_01.csv"
        pitch.parent.mkdir(parents=True)
        pitch.write_text("0.000,0\n" + "0.029,440\n" * 12, encoding="utf-8")
        points = prepare.pitch_points(pitch)
        assert prepare.longest_stable_run(points, 8) == (1, 13, 69)
        output = Path(temporary) / "prepared"
        assert prepare.prepare(root.parent, output, 8, 0.5, 1, 1) == 1
        manifest = (output / "manifest.tsv").read_text(encoding="utf-8")
        assert "scms_Artist_01_A4" in manifest
        assert (output / "audio" / "scms_Artist_01_A4.wav").is_file()
    print("test_prepare_scms_vocal_mix_samples: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
