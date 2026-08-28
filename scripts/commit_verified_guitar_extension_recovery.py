#!/usr/bin/env python3
"""Surgically commit the verified extended-guitar chord display recovery."""

from __future__ import annotations

import subprocess
import sys


SOURCE = "src/analyzer.cpp"
NEEDLES = (
    "bool chord_labels_share_exact_component",
    "const bool corroborated_extended_guitar_chord",
)


def run(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def select_hunks(diff: str) -> str:
    lines = diff.splitlines(keepends=True)
    first_hunk = next((index for index, line in enumerate(lines) if line.startswith("@@")), None)
    if first_hunk is None:
        raise RuntimeError("analyzer source has no unstaged hunks")
    header = "".join(lines[:first_hunk])
    selected = []
    start = first_hunk
    for index in range(first_hunk + 1, len(lines) + 1):
        if index == len(lines) or lines[index].startswith("@@"):
            hunk = "".join(lines[start:index])
            if any(needle in hunk for needle in NEEDLES):
                selected.append(hunk)
            start = index
    if len(selected) != len(NEEDLES):
        raise RuntimeError("could not isolate both verified guitar-extension hunks")
    return header + "".join(selected)


def main() -> int:
    if subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
        raise RuntimeError("refusing to modify a non-empty index")
    diff = run("git", "diff", "--unified=5", "--", SOURCE)
    patch = select_hunks(diff)
    if "!corroborated_extended_guitar_chord" not in patch:
        raise RuntimeError("the residue-cleanup guard is absent from the selected patch")
    run("git", "apply", "--cached", "-", input_text=patch)
    run("git", "commit", "-m", "Preserve corroborated extended guitar chords")
    print("Committed verified extended guitar chord recovery.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
