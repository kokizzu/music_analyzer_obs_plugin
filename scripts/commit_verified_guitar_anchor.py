#!/usr/bin/env python3
"""Plan, stage, and commit only the verified GuitarSet root-anchor change."""

from __future__ import annotations

import subprocess
import sys


PATH = "src/analyzer.cpp"
BASE = "\tif (anchor < 0.08f)\n"
FIXED = "\tif (anchor < 0.02f)\n"
MESSAGE = "Improve weak-root guitar chord primary selection"


def git(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ("git", *args),
        check=True,
        text=True,
        input=input_text,
        capture_output=True,
    )
    return result.stdout


def anchor_patch() -> str:
    base_lines = git("show", f"HEAD:{PATH}").splitlines(keepends=True)
    source_lines = open(PATH, encoding="utf-8").read().splitlines(keepends=True)
    if base_lines.count(BASE) != 1:
        raise RuntimeError("HEAD does not contain exactly one expected guitar anchor")
    if source_lines.count(FIXED) != 1:
        raise RuntimeError("working tree does not contain exactly one verified guitar anchor")
    line_number = base_lines.index(BASE) + 1
    return (
        f"diff --git a/{PATH} b/{PATH}\n"
        f"--- a/{PATH}\n"
        f"+++ b/{PATH}\n"
        f"@@ -{line_number},1 +{line_number},1 @@\n"
        f"-{BASE}"
        f"+{FIXED}"
    )


def assert_only_anchor_staged() -> None:
    names = [name for name in git("diff", "--cached", "--name-only").splitlines() if name]
    if names != [PATH]:
        raise RuntimeError(f"refusing commit: staged paths are {names!r}")
    cached = git("diff", "--cached", "--unified=0", "--", PATH)
    changed_lines = [
        line
        for line in cached.splitlines(keepends=True)
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    if changed_lines != [f"-{BASE}", f"+{FIXED}"]:
        raise RuntimeError("refusing commit: staged source diff is not the verified anchor patch")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "stage", "commit", "inspect"}:
        raise SystemExit("usage: commit_verified_guitar_anchor.py {plan|stage|commit|inspect}")
    mode = sys.argv[1]
    patch = anchor_patch()
    if mode == "plan":
        print(patch, end="")
        return
    if mode == "inspect":
        cached = git("diff", "--cached", "--unified=0", "--", PATH)
        cached = "".join(line for line in cached.splitlines(keepends=True) if not line.startswith("index "))
        print(repr(cached))
        print(repr(patch))
        return
    if mode == "stage":
        if git("diff", "--cached", "--name-only").strip():
            raise RuntimeError("refusing stage: index is not empty")
        git("apply", "--cached", "--unidiff-zero", input_text=patch)
        assert_only_anchor_staged()
        print("staged verified guitar anchor")
        return
    assert_only_anchor_staged()
    git("commit", "-m", MESSAGE)
    print("committed verified guitar anchor")


if __name__ == "__main__":
    main()
