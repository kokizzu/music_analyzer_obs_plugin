#!/usr/bin/env python3
"""Tests for measured same-root guitar quality auditing."""

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_same_root_guitar_quality.py"
HEADER = "expected_chords\tguitar_chord\tguitar_pitch_classes\tguitar_analysis_pitch_classes\traw_pitch_class_levels\tchord_hit\n"


def write_rows(path: Path, rows: list[str]) -> None:
    path.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = root / "first.tsv"
        second = root / "second.tsv"
        write_rows(first, ["C\tCpow\tC,G\tC,G\tC3:1.0,E3:0.5,G3:1.0\t0"])
        write_rows(second, ["C\tCpow\tC,G\tC,G\tC3:1.0,E3:0.5,G3:1.0\t0"])
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(first), str(second)],
            check=True,
            capture_output=True,
            text=True,
        )
    assert "first.tsv: candidates=1 gains=1 regressions=0" in result.stdout
    assert "same_root_guitar_quality: best_floor=0.005 supported_corpora=2/2 regressions=0 common_zero_regression=1" in result.stdout
    print("test_audit_same_root_guitar_quality: ok")


if __name__ == "__main__":
    main()
