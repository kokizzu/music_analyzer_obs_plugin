#!/usr/bin/env python3
"""Commit the bounded Other-owned BasicPitch vocal recovery without mixed worktree churn."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    "src/basic_pitch_vocal_fusion.hpp",
    "tests/basic_pitch_vocal_fusion.cpp",
    "scripts/test_basic_pitch_medleydb_context.py",
    "scripts/manage_basic_pitch_other_vocal_recovery_commit.py",
)
MAKE_BLOCK = """.PHONY: plan-basic-pitch-other-vocal-recovery-commit commit-basic-pitch-other-vocal-recovery push-basic-pitch-other-vocal-recovery
plan-basic-pitch-other-vocal-recovery-commit: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py plan

commit-basic-pitch-other-vocal-recovery: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py commit

push-basic-pitch-other-vocal-recovery: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py push

"""
ALLOWED = set(PATHS) | {"Makefile"}


def run(*args: str, capture: bool = False) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return completed.stdout if capture else ""


def staged_paths() -> set[str]:
    return {line for line in run("git", "diff", "--cached", "--name-only", capture=True).splitlines() if line}


def validate_worktree() -> None:
    changed = set(run("git", "diff", "--name-only", "--", *PATHS, capture=True).splitlines())
    missing = set(PATHS) - changed - {"scripts/manage_basic_pitch_other_vocal_recovery_commit.py"}
    if missing:
        raise SystemExit(f"expected recovery changes missing: {', '.join(sorted(missing))}")


def stage_makefile_block() -> None:
    head = run("git", "show", "HEAD:Makefile", capture=True)
    if head.startswith(MAKE_BLOCK):
        return
    patch = "".join(
        difflib.unified_diff(
            head.splitlines(keepends=True),
            (MAKE_BLOCK + head).splitlines(keepends=True),
            fromfile="a/Makefile",
            tofile="b/Makefile",
        )
    )
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        run("git", "apply", "--cached", str(patch_path))
    finally:
        patch_path.unlink(missing_ok=True)


def stage() -> None:
    existing = staged_paths()
    if existing:
        raise SystemExit(f"refusing mixed staged changes: {', '.join(sorted(existing))}")
    validate_worktree()
    run("git", "add", "--", *PATHS)
    stage_makefile_block()
    staged = staged_paths()
    if staged != ALLOWED:
        raise SystemExit(f"unexpected staged scope: {', '.join(sorted(staged))}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("plan", "commit", "push"))
    action = parser.parse_args().action

    if action == "plan":
        validate_worktree()
        print("planned paths:")
        for path in sorted(ALLOWED):
            print(path)
        return 0
    if action == "commit":
        stage()
        run("git", "commit", "-m", "fix: recover high-confidence Other-owned vocal notes")
        return 0
    run("git", "push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
