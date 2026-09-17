#!/usr/bin/env python3
"""Commit the share-runtime log-capture fix without staging unrelated work."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT_MESSAGE = "windows: include diagnostic log in share runtime checks"
SCRIPT_PATH = "scripts/commit_share_runtime_verifier.py"
VERIFIER_PATH = "scripts/verify_windows_share_runtime.py"


def git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_text, text=True, capture_output=True, check=False
    )


def head_text(path: str) -> str:
    result = git("show", f"HEAD:{path}")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"cannot read HEAD:{path}")
    return result.stdout


def verifier_update(base: str) -> str:
    run_anchor = "    result = subprocess.run(\n"
    log_setup = (
        "    diagnostic_log = executable.with_suffix(\".log\")\n"
        "    try:\n"
        "        log_start = diagnostic_log.stat().st_size\n"
        "    except OSError:\n"
        "        log_start = 0\n"
    )
    if base.count(run_anchor) != 1:
        raise RuntimeError("share verifier subprocess anchor is not unique in HEAD")
    updated = base.replace(run_anchor, log_setup + run_anchor, 1)
    result_close = "        timeout=30,\n    )\n"
    log_read = (
        "    diagnostic_output = \"\"\n"
        "    try:\n"
        "        with diagnostic_log.open(\"r\", encoding=\"utf-8\", errors=\"replace\") as stream:\n"
        "            stream.seek(log_start)\n"
        "            diagnostic_output = stream.read()\n"
        "    except OSError:\n"
        "        pass\n"
    )
    if updated.count(result_close) != 1:
        raise RuntimeError("share verifier subprocess close anchor is not unique in HEAD")
    updated = updated.replace(result_close, result_close + log_read, 1)
    old_error = (
        "        raise SystemExit(\n"
        "            f\"{executable.name} {' '.join(arguments)} failed with {result.returncode}:\\n{result.stdout}\"\n"
        "        )\n"
        "    return result.stdout\n"
    )
    new_error = (
        "        raise SystemExit(\n"
        "            f\"{executable.name} {' '.join(arguments)} failed with {result.returncode}:\\n\"\n"
        "            f\"{result.stdout}{diagnostic_output}\"\n"
        "        )\n"
        "    return result.stdout + diagnostic_output\n"
    )
    if old_error not in updated:
        raise RuntimeError("share verifier output block is missing in HEAD")
    return updated.replace(old_error, new_error, 1)


def patch_text() -> str:
    base = head_text(VERIFIER_PATH)
    updated = verifier_update(base)
    diff = "".join(
        difflib.unified_diff(
            base.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{VERIFIER_PATH}",
            tofile=f"b/{VERIFIER_PATH}",
        )
    )
    return f"diff --git a/{VERIFIER_PATH} b/{VERIFIER_PATH}\n" + diff


def staged_paths() -> set[str]:
    result = git("diff", "--cached", "--name-only")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return {line for line in result.stdout.splitlines() if line}


def plan() -> None:
    if staged_paths():
        raise RuntimeError("refusing to plan with pre-existing staged changes")
    print(f"commit: {COMMIT_MESSAGE}")
    print(f"stage: {VERIFIER_PATH}")
    print(f"stage: {SCRIPT_PATH}")
    print("unrelated worktree changes remain unstaged")


def apply() -> None:
    if staged_paths():
        raise RuntimeError("refusing to apply with pre-existing staged changes")
    result = git("apply", "--cached", "--whitespace=nowarn", input_text=patch_text())
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git apply --cached failed")
    result = git("add", "--", SCRIPT_PATH)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git add failed")
    expected = {VERIFIER_PATH, SCRIPT_PATH}
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
