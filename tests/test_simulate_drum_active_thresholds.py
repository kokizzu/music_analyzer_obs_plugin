#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "simulate_drum_active_thresholds.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    rows_text = """sample\texpected\tgot\tenergy_low\tkick_level\tsnare_level\thihat_level\tcrash_level\ttom_level\tride_level\trim_level
kick/a.wav\tkick\tkick\t0.20\t0.80\t0.35\t0\t0\t0.20\t0\t0
kick/b.wav\tkick\tsnare\t0.20\t0.25\t0.70\t0\t0\t0\t0\t0
snare/a.wav\tsnare\tsnare\t0.20\t0.10\t0.90\t0\t0\t0.45\t0\t0
snare/b.wav\tsnare\tkick\t0.20\t0.60\t0.20\t0\t0\t0\t0\t0
tom/a.wav\ttom\ttom\t0.20\t0\t0.20\t0\t0\t0.95\t0\t0
kick/tom_bleed.wav\tkick\tkick\t0.70\t0.98\t0.10\t0\t0\t0.55\t0\t0
tom/unsafe.wav\ttom\tkick\t0.75\t0.99\t0.15\t0\t0\t0.95\t0\t0
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        rows = pathlib.Path(tmpdir) / "rows.tsv"
        rows.write_text(rows_text, encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--threshold",
                "0.30,0.60",
                "--candidate-cap",
                "kick-primary-tom:tom:0.28:got=kick,kick_level>=0.95,energy_low>=0.58,tom_level>0.30",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum active threshold simulation: rows=7 source=")
    require(output, "threshold 0.30")
    require(output, "  kick: recall=2/3 66.67% precision=2/4 50.00% false=2")
    require(output, "  snare: recall=1/2 50.00% precision=1/3 33.33% false=2")
    require(output, "  tom: recall=2/2 100.00% precision=2/4 50.00% false=2")
    require(output, "threshold 0.60")
    require(output, "  kick: recall=2/3 66.67% precision=2/3 66.67% false=1")
    require(output, "  snare: recall=1/2 50.00% precision=1/2 50.00% false=1")
    require(output, "  tom: recall=2/2 100.00% precision=2/2 100.00% false=0")
    require(output, "candidate kick-primary-tom threshold 0.30 target=tom cap=0.28 matched=2")
    require(output, "  predicate: got=kick,kick_level>=0.95,energy_low>=0.58,tom_level>0.30")
    require(output, "  matched expected=kick=1 tom=1 got=kick=2")
    require(output, "  after tom: recall=1/2 50.00% precision=1/2 50.00% false=1")
    require(output, "  false-active removed=1 routes=kick->tom=1 true-active lost=1")
    require(output, "    removed sample=kick/tom_bleed.wav expected=kick got=kick tom_level=0.550->0.280")
    require(output, "    lost sample=tom/unsafe.wav expected=tom got=kick tom_level=0.950->0.280")
    print("test_simulate_drum_active_thresholds: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
