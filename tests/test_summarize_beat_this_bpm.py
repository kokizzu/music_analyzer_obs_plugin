#!/usr/bin/env python3
"""Regression tests for the offline Beat This! summary."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_beat_this_bpm.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        log = Path(directory) / "diagnostic.log"
        log.write_text(
            "Beat This tempo diag\tid=1\texpected=100.00\traw=100.00\tintervals=30\terror=0.00\n"
            "Beat This tempo diag\tid=2\texpected=200.00\traw=100.00\tintervals=30\terror=100.00\n"
            "Beat This tempo diag\tid=3\texpected=180.00\traw=180.00\tintervals=0\terror=0.00\n",
            encoding="utf-8",
        )
        result = subprocess.run(["python3", str(SCRIPT), str(log)], text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert "subset=all\thits=2/3 (66.7%)\tno_beats=1\thalf_or_double=1\ttotal=3" in result.stdout
        assert "subset=high>=150\thits=1/2 (50.0%)" in result.stdout
    print("test_summarize_beat_this_bpm: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
