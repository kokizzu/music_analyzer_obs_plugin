#!/usr/bin/env python3
"""Regression checks for the SATB relative-chroma selector audit."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_satb_relative_chroma_selector.py"


def write_tsv(path: pathlib.Path, rows: list[str]) -> None:
    path.write_text("missing_pcs\textra_pcs\traw_chroma\n" + "\n".join(rows) + "\n")


def test_requires_zero_extras_in_every_corpus() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = pathlib.Path(temporary)
        safe = root / "safe.tsv"
        unsafe = root / "unsafe.tsv"
        write_tsv(safe, ["C\t\tC:100 G:20"])
        write_tsv(unsafe, ["D\tA\tD:100 A:90"])
        output = subprocess.check_output(
            [sys.executable, str(SCRIPT), "--input", f"safe={safe}", "--input", f"unsafe={unsafe}"],
            text=True,
        )
    assert "threshold=0.90 missing=2 extra=1 safe=0" in output
    assert "common_zero_extra_thresholds=0/9 corpora=2" in output


if __name__ == "__main__":
    test_requires_zero_extras_in_every_corpus()
    print("test_audit_satb_relative_chroma_selector: ok")
