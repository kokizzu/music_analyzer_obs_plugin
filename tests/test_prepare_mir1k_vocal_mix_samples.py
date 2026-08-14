#!/usr/bin/env python3
"""Regression checks for stable MIR-1K mixed-vocal clip preparation."""

from __future__ import annotations

import sys
import tempfile
import wave
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_mir1k_vocal_mix_samples as prepare


def write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(b"\0\0" * 16000)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "source"
        dataset = root / "mir1k_yourmt3_16k"
        write_wav(dataset / "Wavfile" / "Singer_1_01.wav")
        (dataset / "PitchLabel").mkdir(parents=True)
        (dataset / "PitchLabel" / "Singer_1_01.pv").write_text("0\n" * 3 + "60.1\n" * 30, encoding="utf-8")
        run = prepare.longest_stable_run([0.0, 60.1, 60.2, 60.0, 0.0], 3)
        assert run == (1, 4, 60)
        output = Path(temporary) / "prepared"
        assert prepare.prepare(root, output, 20, 0.5, 1, 1) == 1
        manifest = (output / "manifest.tsv").read_text(encoding="utf-8")
        assert "mir1k_Singer_1_01_C4" in manifest
        assert (output / "audio" / "mir1k_Singer_1_01_C4.wav").is_file()
    print("test_prepare_mir1k_vocal_mix_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
