#!/usr/bin/env python3
"""Print unstaged analyzer-case hunks relevant to extended guitar chords."""

from pathlib import Path
import subprocess


PATH = "tests/analyzer_cases.cpp"
NEEDLES = ("check_extended_chords", "C diminished closed shape", "Cdim", "Eaug")


def main() -> int:
    diff = subprocess.run(
        ["git", "diff", "--unified=5", "--", PATH],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    lines = diff.splitlines()
    start = 0
    printed = 0
    for index, line in enumerate(lines + ["@@ END"]):
        if index and line.startswith("@@"):
            hunk = lines[start:index]
            if any(needle in "\n".join(hunk) for needle in NEEDLES):
                print("\n".join(hunk))
                print()
                printed += 1
            start = index
    print(f"extended-chord hunks: {printed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
