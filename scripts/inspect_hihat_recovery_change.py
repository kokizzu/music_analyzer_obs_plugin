#!/usr/bin/env python3
"""Print only diff hunks that touch the generic hi-hat recovery safeguards."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FILES = ("src/analyzer.cpp", "tests/check_hihat_early_recovery_guard.py")
MARKERS = (
    "generic_early_onset_hihat_evidence",
    "generic_tonal_short_onset_hihat_bleed",
    "final_real_mix_early_hihat_recovery",
    "final_real_mix_quiet_ride_hihat_recovery",
)


def main() -> None:
    result = subprocess.run(
        ["git", "diff", "--unified=8", "--", *FILES],
        cwd=ROOT,
        text=True,
        check=True,
        capture_output=True,
    )
    hunks = result.stdout.split("@@ ")
    if not hunks:
        return
    print(hunks[0], end="")
    matched = 0
    for hunk in hunks[1:]:
        if any(marker in hunk for marker in MARKERS):
            print("@@ " + hunk, end="")
            matched += 1
    if not matched:
        print("No matching hi-hat recovery diff hunks.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.stderr.write(error.stderr)
        raise SystemExit(error.returncode)
