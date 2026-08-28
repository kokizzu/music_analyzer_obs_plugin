#!/usr/bin/env python3
"""Show the exact analyzer diff hunks containing verified drum recoveries."""

import subprocess


ANCHORS = (
    "final_real_mix_no_hihat_band_false_positive",
    "final_one_shot_measured_ride_band_hihat_primary_recovery",
)


def main() -> None:
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "-U3", "--", "src/analyzer.cpp"],
        check=True,
        text=True,
        capture_output=True,
    )
    hunks = []
    current = []
    for line in result.stdout.splitlines(keepends=True):
        if line.startswith("@@ "):
            if current:
                hunks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        hunks.append(current)

    selected = [hunk for hunk in hunks if any(anchor in "".join(hunk) for anchor in ANCHORS)]
    if not selected:
        raise SystemExit("no verified drum hunk found")
    for hunk in selected:
        print("".join(hunk), end="")


if __name__ == "__main__":
    main()
