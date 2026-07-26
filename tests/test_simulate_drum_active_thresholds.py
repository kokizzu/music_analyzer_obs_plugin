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
    rows_text = """sample\texpected\tgot\tkick_level\tsnare_level\thihat_level\tcrash_level\ttom_level\tride_level\trim_level
kick/a.wav\tkick\tkick\t0.80\t0.35\t0\t0\t0.20\t0\t0
kick/b.wav\tkick\tsnare\t0.25\t0.70\t0\t0\t0\t0\t0
snare/a.wav\tsnare\tsnare\t0.10\t0.90\t0\t0\t0.45\t0\t0
snare/b.wav\tsnare\tkick\t0.60\t0.20\t0\t0\t0\t0\t0
tom/a.wav\ttom\ttom\t0\t0.20\t0\t0\t0.95\t0\t0
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
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum active threshold simulation: rows=5 source=")
    require(output, "threshold 0.30")
    require(output, "  kick: recall=1/2 50.00% precision=1/2 50.00% false=1")
    require(output, "  snare: recall=1/2 50.00% precision=1/3 33.33% false=2")
    require(output, "  tom: recall=1/1 100.00% precision=1/2 50.00% false=1")
    require(output, "threshold 0.60")
    require(output, "  kick: recall=1/2 50.00% precision=1/1 100.00% false=0")
    require(output, "  snare: recall=1/2 50.00% precision=1/2 50.00% false=1")
    require(output, "  tom: recall=1/1 100.00% precision=1/1 100.00% false=0")
    print("test_simulate_drum_active_thresholds: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
