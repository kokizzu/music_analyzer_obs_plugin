#!/usr/bin/env python3
"""Unit checks for the silent Real A2S sax scale trait probe."""

from __future__ import annotations

import importlib.util
import tempfile
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("probe", ROOT / "scripts" / "inspect_real_a2s_sax_scale.py")
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        kern = root / "scale.krn"
        kern.write_text("**kern\n*Trd-1c-2\n8fL\n8gJ\n8r\n*-\n", encoding="utf-8")
        assert probe.parse_kern_notes(kern) == ["8fL", "8gJ"]

        wav = root / "scale.wav"
        with wave.open(str(wav), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(100)
            output.writeframes(b"\x00\x00" * 10 + b"\x00@" * 10 + b"\x00\x00" * 10 + b"\x00@" * 10)
        rate, duration, levels = probe.rms_windows(wav, seconds=0.1)
        assert rate == 100 and duration == 0.4 and len(levels) == 4
        threshold, onsets = probe.onset_times(levels, window_seconds=0.1)
        assert threshold > 0.0 and len(onsets) == 2
        assert abs(onsets[0] - 0.1) < 1e-9 and abs(onsets[1] - 0.3) < 1e-9
    print("inspect_real_a2s_sax_scale tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
