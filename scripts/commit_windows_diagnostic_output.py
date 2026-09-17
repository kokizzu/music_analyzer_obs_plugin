#!/usr/bin/env python3
"""Commit only the Windows diagnostic stdout redirection and its test."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src/standalone.cpp"
HARDWARE_SOURCE = "src/windows_hardware_control.cpp"
TEST = "scripts/test_windows_diagnostic_output.py"
COMMIT_SCRIPT = "scripts/commit_windows_diagnostic_output.py"
WINDOWS_MK = "windows.mk"
COMMIT_MESSAGE = "windows: capture hardware enumeration output"


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


def select_patch(path: str, markers: tuple[str, ...]) -> str | None:
    result = run("git", "diff", "--unified=0", "--", path)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr, end="")
        return None
    lines = result.stdout.splitlines(keepends=True)
    header: list[str] = []
    hunks: list[list[str]] = []
    current: list[str] | None = None
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
    selected = [hunk for hunk in hunks if any(marker in "".join(hunk) for marker in markers)]
    if not selected:
        return None
    return "".join(header + [line for hunk in selected for line in hunk])


def plan() -> int:
    print(f"commit: {COMMIT_MESSAGE}")
    print(f"stage: {SOURCE} selected stream-fix hunk only")
    print(f"stage: {HARDWARE_SOURCE} selected diagnostic-output hunks only")
    print(f"stage: {TEST}")
    print(f"stage: {COMMIT_SCRIPT}")
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

    patches = [
        select_patch(SOURCE, ("output_stream", "setvbuf(stdout")),
        select_patch(HARDWARE_SOURCE, ("No Windows MIDI output devices", "No paired LiteJam", "No paired Fret Zealot", "MIDI %u")),
    ]
    if patches[0] is None or patches[1] is None:
        print("refusing to commit: expected diagnostic-output hunks are missing", file=sys.stderr)
        return 1
    for patch in patches[:2]:
        applied = run("git", "apply", "--cached", "--unidiff-zero", input_text=patch)
        if applied.returncode != 0:
            print(applied.stdout, file=sys.stderr, end="")
            return applied.returncode

    added = run("git", "add", "--", TEST, COMMIT_SCRIPT)
    if added.returncode != 0:
        print(added.stdout, file=sys.stderr, end="")
        return added.returncode

    expected = {SOURCE, HARDWARE_SOURCE, TEST, COMMIT_SCRIPT}
    after = run("git", "diff", "--cached", "--name-only")
    actual = {line for line in after.stdout.splitlines() if line}
    if after.returncode != 0 or actual != expected:
        print("refusing to commit: staged path set is not scoped", file=sys.stderr)
        print(after.stdout, file=sys.stderr, end="")
        return 1

    committed = run("git", "commit", "-m", COMMIT_MESSAGE)
    print(committed.stdout, end="")
    return committed.returncode


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        print(f"usage: {sys.argv[0]} plan|apply", file=sys.stderr)
        return 2
    return plan() if sys.argv[1] == "plan" else apply_commit()


if __name__ == "__main__":
    raise SystemExit(main())
