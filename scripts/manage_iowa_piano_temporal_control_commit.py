#!/usr/bin/env python3
"""Commit only Iowa piano temporal Vocal precision controls."""

from __future__ import annotations

import difflib
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "README.md",
    "scripts/inspect_iowa_piano_continuous_candidates.py",
    "scripts/prepare_iowa_piano_temporal_controls.py",
    "scripts/test_iowa_piano_temporal_controls.py",
)
SELF = Path(__file__).relative_to(REPO_ROOT).as_posix()
MAKE_BLOCK = """.PHONY: plan-iowa-piano-temporal-control-commit commit-iowa-piano-temporal-control push-iowa-piano-temporal-control
plan-iowa-piano-temporal-control-commit: scripts/manage_iowa_piano_temporal_control_commit.py
\t$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py plan
commit-iowa-piano-temporal-control: scripts/manage_iowa_piano_temporal_control_commit.py
\t$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py commit
push-iowa-piano-temporal-control: scripts/manage_iowa_piano_temporal_control_commit.py
\t$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py push

.PHONY: inspect-iowa-piano-continuous-candidates
inspect-iowa-piano-continuous-candidates: scripts/inspect_iowa_piano_continuous_candidates.py
\t$(PYTHON) scripts/inspect_iowa_piano_continuous_candidates.py

.PHONY: apply-iowa-piano-temporal-controls verify-iowa-piano-temporal-controls test-iowa-piano-temporal-controls
apply-iowa-piano-temporal-controls: scripts/prepare_iowa_piano_temporal_controls.py
\t$(PYTHON) scripts/prepare_iowa_piano_temporal_controls.py apply
verify-iowa-piano-temporal-controls: scripts/prepare_iowa_piano_temporal_controls.py
\t$(PYTHON) scripts/prepare_iowa_piano_temporal_controls.py verify
test-iowa-piano-temporal-controls: $(BUILD_DIR)/basic_pitch_medleydb_context apply-iowa-piano-temporal-controls $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/test_iowa_piano_temporal_controls.py
\t$(PYTHON) scripts/test_iowa_piano_temporal_controls.py

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
    git("commit", "-m", "test: add Iowa piano temporal vocal controls", capture=False)
    return 0


def push() -> int:
    git("push", capture=False)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "commit", "push"}:
        raise SystemExit("usage: manage_iowa_piano_temporal_control_commit.py plan|commit|push")
    try:
        raise SystemExit({"plan": plan, "commit": commit, "push": push}[sys.argv[1]]())
    except RuntimeError as error:
        print(f"manage_iowa_piano_temporal_control_commit: {error}", file=sys.stderr)
        raise SystemExit(1)
