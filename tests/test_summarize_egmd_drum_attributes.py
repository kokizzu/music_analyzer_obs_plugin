#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_egmd_drum_attributes.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing `{needle}` in:\n{text}")


def test_summarizes_drum_attribute_distributions() -> None:
    sample = "\n".join(
        [
            "E-GMD miss SongA sample 100 expected kick,snare missing snare: levels BASS DRUM=0.80* SNARE=0.20 TOMS=0.40* BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=2.00/1.00 supported=1 level=0.80* | SNARE band=4.00 seg=3.00 shape=2.00 trig=0.50/1.00 supported=1 level=0.20 | TOMS band=5.00 seg=4.00 shape=3.00 trig=1.50/1.00 supported=1 level=0.40* | rms=0.1000 energy=0.80/0.10/0.10 transient=1.30 onset=0.40 body=0.60/0.50/0.30 crack=0.20 upperTom=0.10 bodyShape=0",
            "E-GMD false-positive SongB sample 200 expected snare: BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=2.00/1.00 supported=1 level=0.90* | SNARE band=6.00 seg=5.00 shape=4.00 trig=2.00/1.00 supported=1 level=0.60* | HIHAT band=3.00 seg=2.00 shape=1.00 trig=1.20/1.00 supported=1 level=0.40* | CRASH band=4.00 seg=3.00 shape=2.00 trig=0.20/1.00 supported=1 level=0.20 | rms=0.2000 energy=0.70/0.20/0.10 transient=1.50 onset=0.50 body=0.70/0.30/0.20 crack=0.10 upperTom=0.05 bodyShape=4",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "egmd.err"
        path.write_text(sample, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--top", "4", "--examples", "2"],
            check=True,
            text=True,
            capture_output=True,
        )

    output = result.stdout
    require(output, "summarize_egmd_drum_attributes: events 2 rows 3")
    require(output, "miss:snare=1")
    require(output, "false_positive:hihat=1")
    require(output, "false_positive:kick=1")
    require(output, "trigger_ratio=min0.50")
    require(output, "example SongA@100 expected=kick,snare level=0.20 trigger=0.50")


if __name__ == "__main__":
    test_summarizes_drum_attribute_distributions()
    print("test_summarize_egmd_drum_attributes: ok")
