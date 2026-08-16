#!/usr/bin/env python3
"""Regression checks for the SATB full-mix candidate-capacity audit."""

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_polyphonic_candidate_capacity.py"


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "choir.tsv"
        path.write_text(
            "active_notes\tcandidates\tmissing_pcs\n"
            "1:60,2:64\tC4/vocal:90@800 E4/vocal:70@700\t--\n"
            "1:60,2:64,3:67\t" + " ".join(f"C{i}/amb:50@500" for i in range(24)) + "\tG\n"
            "1:60\tC4/vocal:90@800\t--\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path)], check=True, capture_output=True, text=True
        )
    assert "choir\t3\t2\t1\t1\t1\t24" in result.stdout
    print("inspect_polyphonic_candidate_capacity: ok")


if __name__ == "__main__":
    main()
