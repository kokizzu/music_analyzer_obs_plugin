#!/usr/bin/env python3
"""Regression coverage for offline phase/BTT/Beat-This consensus auditing."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_three_tempo_tracker_consensus.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        phase = root / "phase.log"
        btt = root / "btt.log"
        beat = root / "beat.log"
        phase.write_text(
            "MAESTRO tempo diag\tid=1\texpected=120.00\tgot=0.00\tphase_raw=121.00\tphase_confidence=0.40\n"
            "MAESTRO tempo diag\tid=2\texpected=90.00\tgot=0.00\tphase_raw=180.00\tphase_confidence=0.40\n",
            encoding="utf-8",
        )
        btt.write_text(
            "BTT tempo diag\tid=1\texpected=120.00\traw=120.00\tconfidence=0.40\n"
            "BTT tempo diag\tid=2\texpected=90.00\traw=90.00\tconfidence=0.90\n",
            encoding="utf-8",
        )
        beat.write_text(
            "Beat This tempo diag\tid=1\texpected=120.00\traw=120.00\n"
            "Beat This tempo diag\tid=2\texpected=90.00\traw=90.00\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                "python3", str(SCRIPT), "--corpus", "test", str(phase), str(btt), str(beat),
                "--btt-gates", "0", "--agreement-gates", "4",
            ],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert "correct=1/1 (100.0%)" in result.stdout
        assert "newly_revealed=1" in result.stdout
        phase.write_text(
            "MAESTRO tempo diag\tid=1\texpected=120.00\tgot=0.00\tphase_raw=129.00\tphase_confidence=0.40\n",
            encoding="utf-8",
        )
        btt.write_text(
            "BTT tempo diag\tid=1\texpected=120.00\traw=120.00\tconfidence=0.40\n",
            encoding="utf-8",
        )
        beat.write_text(
            "Beat This tempo diag\tid=1\texpected=120.00\traw=120.00\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                "python3", str(SCRIPT), "--corpus", "test", str(phase), str(btt), str(beat),
                "--btt-gates", "0", "--agreement-gates", "12",
            ],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert "viable: none" in result.stdout
        beat.write_text("Beat This tempo diag\tid=2\texpected=90.00\traw=90.00\n", encoding="utf-8")
        result = subprocess.run(
            ["python3", str(SCRIPT), "--corpus", "test", str(phase), str(btt), str(beat)],
            text=True,
            capture_output=True,
        )
        assert result.returncode != 0 and "ids differ" in result.stderr
    print("test_inspect_three_tempo_tracker_consensus: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
