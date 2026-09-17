#!/usr/bin/env python3
"""Commit only the bitmap-font glyph change, preserving unrelated worktree edits."""

from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT_MESSAGE = "visualizer: render common source-label punctuation"
TEST_FILES = (
    "scripts/test_visualizer_parentheses.py",
    "scripts/test_visualizer_glyph_coverage.py",
    "scripts/commit_visualizer_glyphs.py",
)
STAGED_PATHS = {
    "src/visualizer_renderer.cpp",
    "windows.mk",
    *TEST_FILES,
}


def run_git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def head_text(path: str) -> str:
    result = run_git("show", f"HEAD:{path}")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"cannot read HEAD:{path}")
    return result.stdout


def visualizer_update(base: str) -> str:
    insertion = (
        "\tcase '(':\n"
        "\t\treturn {\"00100\", \"01000\", \"10000\", \"10000\", \"10000\", \"01000\", \"00100\"};\n"
        "\tcase ')':\n"
        "\t\treturn {\"00100\", \"00010\", \"00001\", \"00001\", \"00001\", \"00010\", \"00100\"};\n"
        "\tcase ',':\n"
        "\t\treturn {\"00000\", \"00000\", \"00000\", \"00000\", \"00000\", \"01100\", \"01000\"};\n"
        "\tcase ';':\n"
        "\t\treturn {\"00000\", \"01100\", \"01100\", \"00000\", \"01100\", \"01000\", \"10000\"};\n"
        "\tcase '\\'':\n"
        "\t\treturn {\"00100\", \"00100\", \"00000\", \"00000\", \"00000\", \"00000\", \"00000\"};\n"
        "\tcase '\"':\n"
        "\t\treturn {\"01010\", \"01010\", \"00000\", \"00000\", \"00000\", \"00000\", \"00000\"};\n"
        "\tcase '[':\n"
        "\t\treturn {\"01110\", \"01000\", \"01000\", \"01000\", \"01000\", \"01000\", \"01110\"};\n"
        "\tcase ']':\n"
        "\t\treturn {\"01110\", \"00010\", \"00010\", \"00010\", \"00010\", \"00010\", \"01110\"};\n"
        "\tcase '{':\n"
        "\t\treturn {\"00110\", \"01000\", \"01000\", \"10000\", \"01000\", \"01000\", \"00110\"};\n"
        "\tcase '}':\n"
        "\t\treturn {\"01100\", \"00010\", \"00010\", \"00001\", \"00010\", \"00010\", \"01100\"};\n"
        "\tcase '_':\n"
        "\t\treturn {\"00000\", \"00000\", \"00000\", \"00000\", \"00000\", \"00000\", \"11111\"};\n"
        "\tcase '=':\n"
        "\t\treturn {\"00000\", \"00000\", \"11111\", \"00000\", \"11111\", \"00000\", \"00000\"};\n"
        "\tcase '*':\n"
        "\t\treturn {\"00000\", \"10101\", \"01110\", \"11111\", \"01110\", \"10101\", \"00000\"};\n"
        "\tcase '&':\n"
        "\t\treturn {\"01100\", \"10010\", \"10100\", \"01000\", \"10101\", \"10010\", \"01101\"};\n"
        "\tcase '@':\n"
        "\t\treturn {\"01110\", \"10001\", \"10111\", \"10101\", \"10111\", \"10000\", \"01110\"};\n"
        "\tcase '$':\n"
        "\t\treturn {\"00100\", \"01111\", \"10100\", \"01110\", \"00101\", \"11110\", \"00100\"};\n"
        "\tcase '^':\n"
        "\t\treturn {\"00100\", \"01010\", \"10001\", \"00000\", \"00000\", \"00000\", \"00000\"};\n"
        "\tcase '`':\n"
        "\t\treturn {\"01000\", \"00100\", \"00000\", \"00000\", \"00000\", \"00000\", \"00000\"};\n"
        "\tcase '\\\\':\n"
        "\t\treturn {\"10000\", \"01000\", \"01000\", \"00100\", \"00010\", \"00010\", \"00001\"};\n"
        "\tcase '|':\n"
        "\t\treturn {\"00100\", \"00100\", \"00100\", \"00100\", \"00100\", \"00100\", \"00100\"};\n"
        "\tcase '<':\n"
        "\t\treturn {\"00010\", \"00100\", \"01000\", \"10000\", \"01000\", \"00100\", \"00010\"};\n"
        "\tcase '>':\n"
        "\t\treturn {\"01000\", \"00100\", \"00010\", \"00001\", \"00010\", \"00100\", \"01000\"};\n"
    )
    anchor = "\tcase '/':\n\t\treturn {\"00001\", \"00010\", \"00010\", \"00100\", \"01000\", \"01000\", \"10000\"};\n"
    if base.count(anchor) != 1:
        raise RuntimeError("visualizer glyph insertion anchor is not unique in HEAD")
    return base.replace(anchor, anchor + insertion, 1)


def makefile_update(base: str) -> str:
    anchor = "inspect-windows-standalone:\n\tpython3 scripts/windows_standalone.py inspect\n"
    insertion = (
        "\n.PHONY: test-visualizer-parentheses\n"
        "test-visualizer-parentheses:\n"
        "\tpython3 scripts/test_visualizer_parentheses.py\n"
        "\n.PHONY: test-visualizer-glyph-coverage\n"
        "test-visualizer-glyph-coverage:\n"
        "\tpython3 scripts/test_visualizer_glyph_coverage.py\n"
    )
    if base.count(anchor) != 1:
        raise RuntimeError("windows.mk test insertion anchor is not unique in HEAD")
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


def planned_patches() -> str:
    return patch_for("src/visualizer_renderer.cpp", visualizer_update(head_text("src/visualizer_renderer.cpp"))) + patch_for(
        "windows.mk", makefile_update(head_text("windows.mk"))
    )


def staged_paths() -> set[str]:
    result = run_git("diff", "--cached", "--name-only")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return {line for line in result.stdout.splitlines() if line}


def plan() -> None:
    if staged_paths():
        raise RuntimeError("refusing to plan with pre-existing staged changes")
    print(f"commit: {COMMIT_MESSAGE}")
    for path in sorted(STAGED_PATHS):
        print(f"stage: {path}")
    print("unrelated worktree changes remain unstaged")


def apply() -> None:
    if staged_paths():
        raise RuntimeError("refusing to apply with pre-existing staged changes")
    patch = planned_patches()
    result = run_git("apply", "--cached", "--whitespace=nowarn", input_text=patch)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git apply --cached failed")
    result = run_git("add", "--", *TEST_FILES)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git add failed")
    actual = staged_paths()
    if actual != STAGED_PATHS:
        raise RuntimeError(f"unexpected staged paths: {sorted(actual)}")
    result = run_git("commit", "-m", COMMIT_MESSAGE)
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
