#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_agpt_guitar_evaluation.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        first = work / "first.out"
        second = work / "second.out"
        output = work / "summary.tsv"
        first.write_text("analyzer: usable 12, bass 0/0, guitar 10/12, piano 0/0\n", encoding="utf-8")
        second.write_text("analyzer: usable 8, bass 0/0, guitar 8/8, piano 0/0\n", encoding="utf-8")
        subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(output), "--minimum-samples", "20", str(first), str(second)],
            check=True,
        )
        assert output.read_text(encoding="utf-8") == (
            "corpus\tmetric\taccurate\ttotal\tremaining\n"
            "AG-PT\texpected exact-MIDI guitar note\t18\t20\t2\n"
        )
    print("test_summarize_agpt_guitar_evaluation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
