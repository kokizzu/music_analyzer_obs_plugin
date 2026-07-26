#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_drum_active_false_rows.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    rows_text = """sample\texpected\tgot\tkick_level\tkick_trigger\tkick_threshold\tkick_seg\tkick_shape\tsnare_level\tsnare_trigger\tsnare_threshold\tsnare_seg\tsnare_shape\thihat_level\thihat_trigger\thihat_threshold\thihat_seg\thihat_shape\tcrash_level\tcrash_trigger\tcrash_threshold\tcrash_seg\tcrash_shape\ttom_level\ttom_trigger\ttom_threshold\ttom_seg\ttom_shape\tride_level\tride_trigger\tride_threshold\tride_seg\tride_shape\trim_level\trim_trigger\trim_threshold\trim_seg\trim_shape
kick/a.wav\tkick\tkick\t0.80\t2.0\t1.0\t10\t1\t0.35\t1.5\t1.0\t6\t1\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0.20\t0.5\t1.0\t3\t0\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0
kick/b.wav\tkick\tsnare\t0.25\t0.8\t1.0\t4\t0\t0.70\t2.5\t1.0\t8\t1\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0
snare/a.wav\tsnare\tsnare\t0.10\t0.4\t1.0\t1\t0\t0.90\t3.0\t1.0\t9\t1\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0.45\t2.0\t1.0\t7\t1\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0
tom/a.wav\ttom\ttom\t0\t0\t1\t0\t0\t0.20\t0.8\t1.0\t2\t0\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0\t0.95\t3.5\t1.0\t11\t1\t0\t0\t1\t0\t0\t0\t0\t1\t0\t0
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        rows = pathlib.Path(tmpdir) / "rows.tsv"
        rows.write_text(rows_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(rows), "--threshold", "0.30", "--examples", "1"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum active false rows: rows=4 threshold=0.30 source=")
    require(output, "kick: recall=1/2 50.00% precision=1/1 100.00% false=0")
    require(output, "snare: recall=1/1 100.00% precision=1/3 33.33% false=2")
    require(output, "  false level_med=0.525 trigger_med=2.000 seg_med=7.000 shape_med=1.000 expected=kick=2")
    require(output, "    false kick->snare sample=kick/a.wav level=0.350 trigger=1.500/1.000 seg=6.000 shape=1 got=kick")
    require(output, "tom: recall=1/1 100.00% precision=1/2 50.00% false=1")
    print("test_summarize_drum_active_false_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
