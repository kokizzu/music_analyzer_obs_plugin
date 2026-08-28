#!/usr/bin/env python3
"""Regression checks for the immediate-source BPM diagnostic parser."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_immediate_source_bpm.py"


def test_summary() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "tempo.log"
        path.write_text(
            "MAESTRO tempo diag\tid=a\texpected=120.00\tgot=0.00\timmediate_source=120.00\n"
            "MAESTRO tempo diag\tid=b\texpected=100.00\tgot=0.00\timmediate_source=108.00\n"
            "MAESTRO tempo diag\tid=c\texpected=90.00\tgot=0.00\timmediate_source=0.00\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", f"Fixture={path}"],
            check=True,
            capture_output=True,
            text=True,
        )
    assert result.stdout == (
        "immediate_source_bpm: corpus=Fixture rows=3 available=2/3 accurate=2/3 "
        "accurate_available=2/2 aliases=0 unavailable=1 tolerance=8\n"
    )


if __name__ == "__main__":
    test_summary()
