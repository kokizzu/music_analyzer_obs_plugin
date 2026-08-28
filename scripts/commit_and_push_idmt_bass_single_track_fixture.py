#!/usr/bin/env python3
"""Commit and push the already-reviewed compact IDMT bass fixture increment."""

from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "Makefile",
    "scripts/import_idmt_bass_single_track_archive.py",
    "scripts/inspect_idmt_bass_single_track_layout.py",
    "scripts/diagnose_idmt_bass_single_track_archive.py",
    "scripts/summarize_idmt_bass_single_track_annotations.py",
    "scripts/prepare_idmt_bass_single_track_fixture.py",
    "scripts/run_idmt_bass_single_track_measurement.py",
    "scripts/summarize_idmt_bass_single_track_measurement.py",
    "tests/test_prepare_idmt_bass_single_track_fixture.py",
}


def run(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=ROOT, text=True, capture_output=True, check=True)


def main() -> int:
    staged = set(run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines())
    if staged != EXPECTED:
        raise SystemExit("staged scope does not match compact IDMT fixture increment")
    commit = run(["git", "commit", "-m", "Add annotated real bass regression fixture"])
    print(commit.stdout, end="")
    pushed = run(["git", "push"])
    print(pushed.stdout, end="")
    print(pushed.stderr, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
