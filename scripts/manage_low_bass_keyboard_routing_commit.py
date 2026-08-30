#!/usr/bin/env python3
"""Commit the low-bass keyboard-routing fix without staging unrelated worktree changes."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = ("src/analyzer.cpp", "scripts/test_idmt_bass_keyboard_routing.py", "scripts/manage_low_bass_keyboard_routing_commit.py")
MAKE_BLOCK = """\n.PHONY: plan-low-bass-keyboard-routing-commit commit-low-bass-keyboard-routing push-low-bass-keyboard-routing
plan-low-bass-keyboard-routing-commit: scripts/manage_low_bass_keyboard_routing_commit.py
\t$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py plan
commit-low-bass-keyboard-routing: scripts/manage_low_bass_keyboard_routing_commit.py
\t$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py commit
push-low-bass-keyboard-routing: scripts/manage_low_bass_keyboard_routing_commit.py
\t$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py push
"""
ALLOWED = set(PATHS) | {"Makefile"}


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE if capture else None)
    return result.stdout if capture else ""


def staged() -> set[str]:
    return set(filter(None, run("git", "diff", "--cached", "--name-only", capture=True).splitlines()))


def stage_makefile() -> None:
    head = run("git", "show", "HEAD:Makefile", capture=True)
    patch = "".join(difflib.unified_diff(head.splitlines(True), (head + MAKE_BLOCK).splitlines(True), "a/Makefile", "b/Makefile"))
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        run("git", "apply", "--cached", str(patch_path))
    finally:
        patch_path.unlink(missing_ok=True)


def main() -> int:
    action = argparse.ArgumentParser()
    action.add_argument("action", choices=("plan", "commit", "push"))
    mode = action.parse_args().action
    if mode == "plan":
        print("planned paths:\n" + "\n".join(sorted(ALLOWED)))
        return 0
    if mode == "push":
        run("git", "push")
        return 0
    if staged():
        raise SystemExit("refusing mixed staged changes")
    run("git", "add", "--", *PATHS)
    stage_makefile()
    if staged() != ALLOWED:
        raise SystemExit("unexpected staged scope")
    run("git", "commit", "-m", "fix: prevent bass fundamentals leaking into keyboard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
