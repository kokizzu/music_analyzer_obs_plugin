#!/usr/bin/env python3
"""Commit only the Windows GATT interface GUID fix and regression test."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HEADER = "src/windows_bluetooth_gatt.hpp"
CONTROL = "src/windows_hardware_control.cpp"
TEST = "scripts/test_windows_gatt_interface.py"
COMMIT_SCRIPT = "scripts/commit_windows_gatt_interface.py"
WINDOWS_MK = "windows.mk"
COMMIT_MESSAGE = "windows: enumerate the GATT service interface"


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
    print(f"stage: {HEADER} selected interface-GUID hunks only")
    print(f"stage: {CONTROL} selected interface-use hunks only")
    print(f"stage: {TEST}")
    print(f"stage: {COMMIT_SCRIPT}")
    print(f"stage: {WINDOWS_MK} selected GATT-test target hunk only")
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
        select_patch(HEADER, ("kBluetoothGattServiceInterface",)),
        select_patch(CONTROL, ("kBluetoothGattServiceInterface",)),
        select_patch(WINDOWS_MK, ("test-windows-gatt-interface",)),
    ]
    if any(patch is None for patch in patches):
        print("refusing to commit: expected GATT interface hunks are missing", file=sys.stderr)
        return 1
    for patch in patches:
        applied = run("git", "apply", "--cached", "--unidiff-zero", input_text=patch)
        if applied.returncode != 0:
            print(applied.stdout, file=sys.stderr, end="")
            return applied.returncode

    added = run("git", "add", "--", TEST, COMMIT_SCRIPT)
    if added.returncode != 0:
        print(added.stdout, file=sys.stderr, end="")
        return added.returncode

    expected = {HEADER, CONTROL, TEST, COMMIT_SCRIPT, WINDOWS_MK}
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
