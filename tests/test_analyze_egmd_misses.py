#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_egmd_misses.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing `{needle}` in:\n{text}")


def test_summarizes_verbose_egmd_logs() -> None:
    sample = "\n".join(
        [
            "E-GMD miss SongA sample 100 expected kick,snare missing snare:  levels BASS DRUM=0.80* SNARE=0.20 TOMS=0.40* BASS DRUM band=10 seg=10 shape=10 trig=2/1 supported=1 level=0.80* | SNARE band=4 seg=4 shape=4 trig=2/1 supported=1 level=0.20 | TOMS band=5 seg=5 shape=5 trig=2/1 supported=1 level=0.40* | rms=0.1 energy=0.8/0.1/0.1 bodyShape=0",
            "E-GMD miss SongB sample 200 expected hihat missing hihat:  levels HIHAT=0.29 CRASH=0.70* HIHAT band=3 seg=3 shape=3 trig=2/1 supported=1 level=0.29 | CRASH band=8 seg=8 shape=8 trig=2/1 supported=1 level=0.70* | rms=0.1 energy=0.2/0.3/0.5 bodyShape=4",
            "E-GMD false-positive SongC sample 300 expected kick: BASS DRUM band=10 seg=10 shape=10 trig=2/1 supported=1 level=0.90* | SNARE band=6 seg=6 shape=6 trig=2/1 supported=1 level=0.60* | RIM band=3 seg=3 shape=3 trig=2/1 supported=1 level=0.40* | CRASH band=4 seg=4 shape=4 trig=2/1 supported=1 level=0.20 | rms=0.1 energy=0.7/0.2/0.1 bodyShape=0",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "egmd.err"
        path.write_text(sample, encoding="utf-8")
        result = subprocess.run([str(SCRIPT), str(path)], check=True, text=True, capture_output=True)

    output = result.stdout
    require(output, "egmd_misses 2")
    require(output, "egmd_false_positive_windows 1")
    require(output, "missing by category snare:1 hihat:1")
    require(output, "false positives by category rim:1 snare:1")
    require(output, "miss snare examples SongA@100 expected kick,snare")
    require(output, "false rim examples SongC@300 expected kick")


if __name__ == "__main__":
    test_summarizes_verbose_egmd_logs()
    print("test_analyze_egmd_misses: ok")
