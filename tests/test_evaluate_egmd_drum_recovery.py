#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_egmd_drum_recovery.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing `{needle}` in:\n{text}")


def test_scores_candidate_recovery_rules() -> None:
    sample = "\n".join(
        [
            "E-GMD miss SongA sample 100 expected kick,snare missing snare: levels BASS DRUM=0.90* SNARE=0.20 HIHAT=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.12/0.08 transient=1.80 onset=8.00 body=0.60/10.00/0.30 crack=1.00 upperTom=0.10 bodyShape=0",
            "E-GMD false-positive SongB sample 200 expected kick: BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.12/0.08 transient=1.80 onset=8.00 body=0.60/10.00/0.30 crack=1.00 upperTom=0.10 bodyShape=0",
            "E-GMD miss SongC sample 300 expected kick,ride missing ride: levels BASS DRUM=0.90* RIDE=0.00 HIHAT=0.00 CRASH=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | CRASH band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | RIDE band=3.00 seg=3.00 shape=3.00 trig=6.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.75/0.15/0.10 transient=2.00 onset=5.00 body=1.00/1.00/1.00 crack=0.10 upperTom=0.10 bodyShape=0",
            "E-GMD miss SongD sample 400 expected hihat,snare missing snare: levels SNARE=0.20 HIHAT=0.60* SNARE band=2.00 seg=1.00 shape=1.00 trig=0.80/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=0.80 shape=0.80 trig=3.00/1.00 supported=1 level=0.60* | rms=0.0050 energy=0.35/0.42/0.23 transient=1.50 onset=2.00 body=0.50/0.70/1.20 crack=0.06 upperTom=0.70 bodyShape=4",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "egmd.err"
        path.write_text(sample, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--examples", "2"],
            check=True,
            text=True,
            capture_output=True,
        )

    output = result.stdout
    require(output, "evaluate_egmd_drum_recovery: events=4")
    require(output, "rule=supported-low-snare category=snare")
    require(output, "tp_gain=1 fp_gain=0 net=1")
    require(output, "rule=kick-backed-snare category=snare")
    require(output, "tp_gain=1 fp_gain=1 net=0")
    require(output, "rule=embedded-ride category=ride")
    require(output, "tp_gain=1 fp_gain=0 net=1")


if __name__ == "__main__":
    test_scores_candidate_recovery_rules()
    print("test_evaluate_egmd_drum_recovery: ok")
