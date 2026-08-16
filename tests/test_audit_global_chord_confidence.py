#!/usr/bin/env python3
"""Tests for global chord confidence display auditing."""

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_global_chord_confidence.py"
HEADER = "global_chord\tglobal_chord_confidence\tchord_hit\n"


def write_attributes(path: Path) -> None:
    path.write_text(
        HEADER
        + "C\t0.40\t0\n"
        + "G\t0.80\t1\n"
        + "--\t0.00\t0\n",
        encoding="utf-8",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = root / "first.tsv"
        second = root / "second.tsv"
        write_attributes(first)
        write_attributes(second)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(first), str(second), "--floors", "0", "0.45", "0.95"],
            check=True,
            capture_output=True,
            text=True,
        )
    assert "first\t3\t1\t1\t50.0%" in result.stdout
    assert "0.45\t0\t2\t2\t0\t100.0%\t2/2" in result.stdout
    assert "global_chord_confidence: best_floor=0.45 supported_corpora=2/2 common_zero_regression_floors=1" in result.stdout
    print("test_audit_global_chord_confidence: ok")


if __name__ == "__main__":
    main()
