#!/usr/bin/env python3
"""Regression test for the BabySlakh cross-corpus decision record."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_babyslakh_drum_calibration.py"
SUMMARY = (
    "analyzer_egmd: drum hits {hits}/{events}, drum precision {precision}% x "
    "recall by category kick:1/1-0/snare:1/1-0/hihat:1/1-0/crash:{crash}/36-0/"
    "tom:{tom}/15-0/ride:{ride}/25-0/rim:0/0-0\n"
)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        paths = []
        for name, values in (("mdb", (139, 192, "69.8", 1, 1, 1)), ("star", (39, 56, "100.0", 1, 1, 1)),
                             ("baby", (140, 259, "77.3", 0, 2, 0))):
            path = root / f"{name}.log"
            path.write_text(SUMMARY.format(hits=values[0], events=values[1], precision=values[2], crash=values[3], tom=values[4], ride=values[5]), encoding="utf-8")
            paths.append(path)
        output = root / "audit.txt"
        subprocess.run([sys.executable, str(SCRIPT), "--mdb", str(paths[0]), "--star", str(paths[1]),
                        "--babyslakh", str(paths[2]), "--output", str(output)], check=True)
        assert "decision=retain_current_detector" in output.read_text(encoding="utf-8")
    print("test_audit_babyslakh_drum_calibration: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
