#!/usr/bin/env python3
"""Commit only the continuous temporal MedleyDB test improvement."""

from __future__ import annotations

import difflib
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "scripts/test_basic_pitch_medleydb_context.py",
    "tests/basic_pitch_medleydb_context.cpp",
)
SELF = Path(__file__).relative_to(REPO_ROOT).as_posix()
MAKE_BLOCK = """.PHONY: plan-basic-pitch-medleydb-temporal-commit commit-basic-pitch-medleydb-temporal push-basic-pitch-medleydb-temporal
plan-basic-pitch-medleydb-temporal-commit: scripts/manage_basic_pitch_medleydb_temporal_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py plan
commit-basic-pitch-medleydb-temporal: scripts/manage_basic_pitch_medleydb_temporal_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py commit
push-basic-pitch-medleydb-temporal: scripts/manage_basic_pitch_medleydb_temporal_commit.py
\t$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py push

"""
ANCHOR = ".PHONY: plan-medleydb-vocal-fixture-update-commit"


def git(*args: str, capture: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def stage_makefile_block() -> None:
    if git("diff", "--cached", "--name-only", "--", "Makefile").strip():
        raise RuntimeError("refusing to alter an already staged Makefile")
    head = git("show", "HEAD:Makefile")
    if MAKE_BLOCK in head:
        return
    if ANCHOR not in head:
        raise RuntimeError("Makefile anchor not found in HEAD")
    updated = head.replace(ANCHOR, MAKE_BLOCK + ANCHOR, 1)
    patch = "".join(difflib.unified_diff(
        head.splitlines(keepends=True), updated.splitlines(keepends=True),
        fromfile="a/Makefile", tofile="b/Makefile",
    ))
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temporary:
        temporary.write(patch)
        patch_path = Path(temporary.name)
    try:
        git("apply", "--cached", "--whitespace=nowarn", str(patch_path))
    finally:
        patch_path.unlink(missing_ok=True)


def plan() -> int:
    print("worktree-status=")
    print(git("status", "--short"), end="")
    print("commit-paths=")
    for path in (*FILES, "Makefile", SELF):
        print(path)
    return 0


def commit() -> int:
    stage_makefile_block()
    git("add", "--", *FILES, SELF, capture=False)
    allowed = set((*FILES, "Makefile", SELF))
    staged = {path for path in git("diff", "--cached", "--name-only").splitlines() if path}
    unexpected = sorted(staged - allowed)
    if unexpected:
        raise RuntimeError(f"refusing unexpected staged paths: {', '.join(unexpected)}")
    missing = sorted(allowed - staged)
    if missing:
        raise RuntimeError(f"expected staged paths are missing: {', '.join(missing)}")
    git("commit", "-m", "test: exercise temporal MedleyDB vocal evidence", capture=False)
    return 0


def push() -> int:
    git("push", capture=False)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "commit", "push"}:
        raise SystemExit("usage: manage_basic_pitch_medleydb_temporal_commit.py plan|commit|push")
    try:
        raise SystemExit({"plan": plan, "commit": commit, "push": push}[sys.argv[1]]())
    except RuntimeError as error:
        print(f"manage_basic_pitch_medleydb_temporal_commit: {error}", file=sys.stderr)
        raise SystemExit(1)
