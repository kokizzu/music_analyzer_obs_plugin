#!/usr/bin/env python3
"""Commit only the label-glyph regression test and its Makefile entries."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
WINDOWS_MK = "windows.mk"
TEST_SCRIPT = "scripts/test_visualizer_label_glyphs.py"
COMMIT_SCRIPT = "scripts/commit_visualizer_label_glyphs.py"
COMMIT_MESSAGE = "tests: cover all visualizer label glyphs"


def run(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def print_plan() -> int:
    print(f"commit: {COMMIT_MESSAGE}")
    print(f"stage: {TEST_SCRIPT}")
    print(f"stage: {COMMIT_SCRIPT}")
    print(f"stage: {WINDOWS_MK} label-glyph and scoped-commit hunks only")
    print("unrelated worktree changes remain unstaged")
    return 0


def apply_commit() -> int:
    staged = run("git", "diff", "--cached", "--name-only")
    if staged.returncode != 0:
        print(staged.stdout, file=sys.stderr, end="")
        return staged.returncode
    if staged.stdout.strip():
        print("refusing to commit: the index already contains staged paths", file=sys.stderr)
        print(staged.stdout, file=sys.stderr, end="")
        return 1

    diff = run("git", "diff", "--unified=0", "--", WINDOWS_MK)
    if diff.returncode != 0:
        print(diff.stdout, file=sys.stderr, end="")
        return diff.returncode

    lines = diff.stdout.splitlines(keepends=True)
    header = []
    hunks = []
    current = None
    for line in lines:
        if line.startswith("@@"):
            if current is not None:
                hunks.append(current)
            current = [line]
        elif current is None:
            header.append(line)
        else:
            current.append(line)
    if current is not None:
        hunks.append(current)

    selected = [hunk for hunk in hunks if any("visualizer-label-glyphs" in line for line in hunk)]
    selected_text = "".join(line for hunk in selected for line in hunk)
    if (
        "test-visualizer-label-glyphs" not in selected_text
        or "commit-visualizer-label-glyphs" not in selected_text
    ):
        print("refusing to commit: expected both label-test and scoped-commit Makefile hunks", file=sys.stderr)
        return 1
    selected_patch = "".join(header + [line for hunk in selected for line in hunk])
    cached = run("git", "apply", "--cached", "--unidiff-zero", input_text=selected_patch)
    if cached.returncode != 0:
        print(cached.stdout, file=sys.stderr, end="")
        return cached.returncode

    added = run("git", "add", "--", TEST_SCRIPT, COMMIT_SCRIPT)
    if added.returncode != 0:
        print(added.stdout, file=sys.stderr, end="")
        return added.returncode

    staged_after = run("git", "diff", "--cached", "--name-only")
    expected = {WINDOWS_MK, TEST_SCRIPT, COMMIT_SCRIPT}
    actual = {line for line in staged_after.stdout.splitlines() if line}
    if staged_after.returncode != 0 or actual != expected:
        print("refusing to commit: staged path set is not scoped", file=sys.stderr)
        print(staged_after.stdout, file=sys.stderr, end="")
        return 1

    committed = run("git", "commit", "-m", COMMIT_MESSAGE)
    print(committed.stdout, end="")
    return committed.returncode


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        print(f"usage: {sys.argv[0]} plan|apply", file=sys.stderr)
        return 2
    return print_plan() if sys.argv[1] == "plan" else apply_commit()


if __name__ == "__main__":
    raise SystemExit(main())
