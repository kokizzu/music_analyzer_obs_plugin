#!/usr/bin/env python3
"""Commit the signed-bundle runtime check without staging unrelated Windows work."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT_MESSAGE = "windows: verify signed bundle locally"
CHECK_PATH = "scripts/verify_windows_signed_runtime.py"
SCRIPT_PATH = "scripts/commit_signed_runtime_check.py"


def git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_text, text=True, capture_output=True, check=False
    )


def head_text(path: str) -> str:
    result = git("show", f"HEAD:{path}")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"cannot read HEAD:{path}")
    return result.stdout


def makefile_update(base: str) -> str:
    anchor = ".PHONY: verify-windows-share-runtime\nverify-windows-share-runtime:\n\tpython3 scripts/verify_windows_share_runtime.py\n"
    insertion = (
        "\n.PHONY: verify-windows-signed-runtime\n"
        "verify-windows-signed-runtime:\n"
        "\tpython3 scripts/verify_windows_signed_runtime.py\n"
        "\n.PHONY: plan-commit-signed-runtime commit-signed-runtime\n"
        "plan-commit-signed-runtime:\n"
        "\tpython3 scripts/commit_signed_runtime_check.py plan\n\n"
        "commit-signed-runtime:\n"
        "\tpython3 scripts/commit_signed_runtime_check.py apply\n"
    )
    if base.count(anchor) != 1:
        raise RuntimeError("signed runtime target anchor is not unique in HEAD")
    return base.replace(anchor, anchor + insertion, 1)


def patch_for(path: str, updated: str) -> str:
    base = head_text(path)
    diff = "".join(
        difflib.unified_diff(
            base.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
    )
    return f"diff --git a/{path} b/{path}\n" + diff


def staged_paths() -> set[str]:
    result = git("diff", "--cached", "--name-only")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return {line for line in result.stdout.splitlines() if line}


def plan() -> None:
    if staged_paths():
        raise RuntimeError("refusing to plan with pre-existing staged changes")
    print(f"commit: {COMMIT_MESSAGE}")
    print(f"stage: {CHECK_PATH}")
    print(f"stage: {SCRIPT_PATH}")
    print("stage only the scoped windows.mk target hunks")
    print("unrelated worktree changes remain unstaged")


def apply() -> None:
    if staged_paths():
        raise RuntimeError("refusing to apply with pre-existing staged changes")
    patch = patch_for("windows.mk", makefile_update(head_text("windows.mk")))
    result = git("apply", "--cached", "--whitespace=nowarn", input_text=patch)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git apply --cached failed")
    result = git("add", "--", CHECK_PATH, SCRIPT_PATH)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git add failed")
    expected = {"windows.mk", CHECK_PATH, SCRIPT_PATH}
    if staged_paths() != expected:
        raise RuntimeError(f"unexpected staged paths: {sorted(staged_paths())}")
    result = git("commit", "-m", COMMIT_MESSAGE)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git commit failed")
    print(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    options = parser.parse_args()
    try:
        {"plan": plan, "apply": apply}[options.mode]()
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
