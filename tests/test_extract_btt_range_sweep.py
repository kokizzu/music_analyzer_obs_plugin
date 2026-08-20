#!/usr/bin/env python3
"""Regression coverage for publishing a selected BTT range-sweep result."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_btt_range_sweep.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "sweep.log"
        output = root / "selected.log"
        source.write_text(
            "BTT range sweep\tid=1\texpected=180.0\traw=180.5\tconfidence=0.4\tmin_tempo=120\tmax_tempo=240\terror=0.5\n"
            "BTT range sweep\tid=1\texpected=180.0\traw=90.0\tconfidence=0.4\tmin_tempo=40\tmax_tempo=240\terror=90.0\n"
            "BTT range sweep\tid=2\texpected=160.0\traw=159.5\tconfidence=0.5\tmin_tempo=120\tmax_tempo=240\terror=0.5\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["python3", str(SCRIPT), "--input", str(source), "--output", str(output), "--min-tempo", "120"],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert output.read_text(encoding="utf-8") == (
            "BTT tempo diag\tid=1\texpected=180.00\traw=180.50\tconfidence=0.400\tmin_tempo=120.00\tmax_tempo=240.00\terror=0.50\n"
            "BTT tempo diag\tid=2\texpected=160.00\traw=159.50\tconfidence=0.500\tmin_tempo=120.00\tmax_tempo=240.00\terror=0.50\n"
        )
        source.write_text(
            "BTT range sweep\tid=2\texpected=160.0\traw=159.5\tconfidence=0.5\tmin_tempo=120\tmax_tempo=240\terror=0.5\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["python3", str(SCRIPT), "--input", str(source), "--output", str(output), "--min-tempo", "120"],
            text=True,
            capture_output=True,
        )
        assert result.returncode != 0 and "not contiguous" in result.stderr
    print("test_extract_btt_range_sweep: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
