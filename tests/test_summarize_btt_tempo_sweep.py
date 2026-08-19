#!/usr/bin/env python3
"""Regression tests for the offline BTT range-sweep summary."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_btt_tempo_sweep.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(SCRIPT), *args], text=True, capture_output=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        log = Path(directory) / "sweep.log"
        log.write_text(
            "BTT range sweep\tid=1\texpected=100.00\traw=100.00\tconfidence=0.800\tmin_tempo=40.00\tmax_tempo=240.00\terror=0.00\n"
            "BTT range sweep\tid=2\texpected=200.00\traw=100.00\tconfidence=0.800\tmin_tempo=40.00\tmax_tempo=240.00\terror=100.00\n"
            "BTT range sweep\tid=1\texpected=100.00\traw=180.00\tconfidence=0.200\tmin_tempo=120.00\tmax_tempo=240.00\terror=80.00\n"
            "BTT range sweep\tid=2\texpected=200.00\traw=200.00\tconfidence=0.600\tmin_tempo=120.00\tmax_tempo=240.00\terror=0.00\n",
            encoding="utf-8",
        )
        result = run(str(log), "--confidence-gates", "0.60")
        assert result.returncode == 0, result.stderr
        assert "min_tempo=40.00\tsubset=all\tgate=raw\tcorrect=1/2 (50.0%)" in result.stdout
        assert "min_tempo=120.00\tsubset=high>=150\tgate=0.60\tcorrect=1/1 (100.0%)" in result.stdout
        empty = Path(directory) / "empty.log"
        empty.write_text("ignored\n", encoding="utf-8")
        result = run(str(empty))
        assert result.returncode != 0
        assert "no rows" in result.stderr
    print("test_summarize_btt_tempo_sweep: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
