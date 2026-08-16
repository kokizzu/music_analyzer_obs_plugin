#!/usr/bin/env python3
"""Fixture checks for the harmonic-product octave audit."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_harmonic_product_octave_evidence.py"


def candidate(midi: int, ratio: float) -> str:
    # Candidate evidence has 29 fields; only MIDI and field 28 matter here.
    fields = [str(midi), "vocal"] + ["0"] * 26 + [f"{ratio:.2f}"]
    return ",".join(fields)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "attributes.tsv"
        path.write_text(
            "active_notes\tcandidate_evidence\n"
            f"52:60\t{candidate(72, 2.25)}\n"
            f"52:64\t{candidate(64, 0.80)}\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", f"fixture={path}"],
            check=True,
            capture_output=True,
            text=True,
        )
    assert "fixture: active_notes=2" in result.stdout
    assert "threshold=1.00 recoveries=1 protected=0 zero_regression=1" in result.stdout
    assert "threshold=3.00 recoveries=0 protected=0 zero_regression=0" in result.stdout
    assert "common_zero_regression_thresholds=4/6 corpora=1" in result.stdout
    print("test_inspect_harmonic_product_octave_evidence: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
