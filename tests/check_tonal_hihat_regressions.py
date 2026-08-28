#!/usr/bin/env python3
"""Ensure tonal real-note fixtures do not enter the visible hi-hat lane."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = (
    "brass_acoustic_016-082-100",
    "brass_acoustic_016-069-100",
)
PATTERN = re.compile(r"drum-active-windows (\d+)/(\d+)")


def main() -> None:
    for sample_id in SAMPLES:
        result = subprocess.run(
            ["sh", "scripts/run_real_note_sample_debug.sh", sample_id],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        match = PATTERN.search(result.stdout)
        if not match:
            raise SystemExit(f"missing drum-active summary for {sample_id}\n{result.stdout}")
        active, total = (int(value) for value in match.groups())
        if active:
            raise SystemExit(f"tonal hi-hat regression for {sample_id}: {active}/{total}\n{result.stdout}")
    print("check_tonal_hihat_regressions: ok")


if __name__ == "__main__":
    main()
