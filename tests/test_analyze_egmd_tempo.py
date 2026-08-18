#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_egmd_tempo.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing `{needle}` in:\n{text}")


def test_reports_phase_energy_alignment_without_changing_tempo_summary() -> None:
    sample = "\n".join(
        [
            "MAESTRO tempo diag\tid=A\texpected=120.00\tgot=0.00\traw=160.00\tconfidence=0.30\terror=120.00\tstatus=no-estimate\tcandidates=160(s=1.00,align=20/10/30/40) 120(s=0.90,align=20/80/30/40)",
            "MAESTRO tempo diag\tid=B\texpected=110.00\tgot=0.00\traw=110.00\tconfidence=0.30\terror=110.00\tstatus=no-estimate\tcandidates=110(s=1.00,align=20/55/30/40) 160(s=0.90,align=20/10/30/40)",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tempo.err"
        path.write_text(sample, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--prefix", "MAESTRO tempo diag", str(path)],
            check=True,
            text=True,
            capture_output=True,
        )

    require(result.stdout, "tempo diagnostics: rows 2")
    require(result.stdout, "tempo phase-energy alignment: candidate diagnostics 2/2, expected candidate available 2/2")
    require(result.stdout, "bass expected>selected 1/2, equal 1/2, lower 0/2")


if __name__ == "__main__":
    test_reports_phase_energy_alignment_without_changing_tempo_summary()
    print("test_analyze_egmd_tempo: ok")
