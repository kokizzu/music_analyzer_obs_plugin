#!/usr/bin/env python3
"""Commit the runtime-status log-capture regression fix without other worktree edits."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT_MESSAGE = "windows: read diagnostic log in hardware status test"
TEST_PATH = "scripts/test_windows_hardware_status_runtime.py"
SCRIPT_PATH = "scripts/commit_windows_runtime_test.py"


def git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_text, text=True, capture_output=True, check=False
    )


def head_text(path: str) -> str:
    result = git("show", f"HEAD:{path}")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"cannot read HEAD:{path}")
    return result.stdout


def test_update(base: str) -> str:
    loop_anchor = '    for name in ("MusicAnalyzer", "HalfMusicAnalyzer"):\n'
    setup = (
        "        executable = PORTABLE / f\"{name}.exe\"\n"
        "        diagnostic_log = executable.with_suffix(\".log\")\n"
        "        try:\n"
        "            log_start = diagnostic_log.stat().st_size\n"
        "        except OSError:\n"
        "            log_start = 0\n"
    )
    if base.count(loop_anchor) != 1:
        raise RuntimeError("hardware status loop anchor is not unique in HEAD")
    updated = base.replace(loop_anchor, loop_anchor + setup, 1)
    old_executable = '                str(PORTABLE / f"{name}.exe"),\n'
    if updated.count(old_executable) != 1:
        raise RuntimeError("hardware status executable expression is not unique in HEAD")
    updated = updated.replace(old_executable, '                str(executable),\n', 1)
    result_close = "            timeout=30,\n        )\n"
    log_read = (
        "        diagnostic_output = \"\"\n"
        "        try:\n"
        "            with diagnostic_log.open(\"r\", encoding=\"utf-8\", errors=\"replace\") as stream:\n"
        "                stream.seek(log_start)\n"
        "                diagnostic_output = stream.read()\n"
        "        except OSError:\n"
        "            pass\n"
        "        output = result.stdout + diagnostic_output\n"
    )
    if updated.count(result_close) != 1:
        raise RuntimeError("hardware status subprocess close anchor is not unique in HEAD")
    updated = updated.replace(result_close, result_close + log_read, 1)
    return updated.replace("{result.stdout}", "{output}")


def makefile_update(base: str) -> str:
    anchor = "test-visualizer-glyph-coverage:\n\tpython3 scripts/test_visualizer_glyph_coverage.py\n"
    insertion = (
        "\n.PHONY: plan-commit-share-runtime-verifier commit-share-runtime-verifier\n"
        "plan-commit-share-runtime-verifier:\n"
        "\tpython3 scripts/commit_share_runtime_verifier.py plan\n\n"
        "commit-share-runtime-verifier:\n"
        "\tpython3 scripts/commit_share_runtime_verifier.py apply\n"
        "\n.PHONY: plan-commit-windows-runtime-test commit-windows-runtime-test\n"
        "plan-commit-windows-runtime-test:\n"
        "\tpython3 scripts/commit_windows_runtime_test.py plan\n\n"
        "commit-windows-runtime-test:\n"
        "\tpython3 scripts/commit_windows_runtime_test.py apply\n"
    )
    if base.count(anchor) != 1:
        raise RuntimeError("windows.mk runtime-test insertion anchor is not unique in HEAD")
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
    print(f"stage: {TEST_PATH}")
    print(f"stage: {SCRIPT_PATH}")
    print("stage only the scoped windows.mk target hunks")
    print("unrelated worktree changes remain unstaged")


def apply() -> None:
    if staged_paths():
        raise RuntimeError("refusing to apply with pre-existing staged changes")
    patch = patch_for(TEST_PATH, test_update(head_text(TEST_PATH))) + patch_for(
        "windows.mk", makefile_update(head_text("windows.mk"))
    )
    result = git("apply", "--cached", "--whitespace=nowarn", input_text=patch)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git apply --cached failed")
    result = git("add", "--", SCRIPT_PATH)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git add failed")
    expected = {TEST_PATH, SCRIPT_PATH, "windows.mk"}
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
