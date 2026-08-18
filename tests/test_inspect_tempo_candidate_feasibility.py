#!/usr/bin/env python3
"""Regression test for labelled tempo candidate feasibility reporting."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_tempo_candidate_feasibility.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        log = pathlib.Path(temporary) / "tempo.log"
        log.write_text(
            "MAESTRO tempo diag\tid=one\texpected=120\tcandidates="
            "160(s=11,m=0.10,align=10/10/10/10) 120(s=10,m=0.90,align=10/90/10/10)\n"
            "MAESTRO tempo diag\tid=two\texpected=100\tcandidates="
            "160(s=12,m=0.80,align=10/80/10/10) 100(s=8,m=0.20,align=10/20/10/10)\n",
            encoding="utf-8",
        )
        result = subprocess.run([sys.executable, str(SCRIPT), str(log)], check=True, text=True,
                                capture_output=True)
    if "labelled 2/2, score-only 0/2" not in result.stdout:
        raise AssertionError(result.stdout)
    if "meter selector w=0.25:1/2" not in result.stdout:
        raise AssertionError(result.stdout)
    if "bass alignment selector w=0.25:1/2" not in result.stdout:
        raise AssertionError(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
