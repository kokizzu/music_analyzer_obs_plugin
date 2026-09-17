#!/usr/bin/env python3
"""Commit only the Windows share connectivity diagnostic changes."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = "check-windows-share-connectivity"
DIAGNOSTIC = "scripts/check_windows_share_connectivity.py"
COMMIT_HELPER = "scripts/commit_windows_share_connectivity.py"
MAKEFILE = "windows.mk"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def selected_patch() -> str:
    diff = run("diff", "--no-ext-diff", "--unified=0", "--", MAKEFILE).stdout
    lines = diff.splitlines(keepends=True)
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

    selected = [hunk for hunk in hunks if TARGET in "".join(hunk)]
    if not selected:
        raise RuntimeError(f"could not find the {TARGET} diff in {MAKEFILE}")
    return "".join(header + [line for hunk in selected for line in hunk])


def main() -> int:
    cached = run("diff", "--cached", "--name-only").stdout.splitlines()
    allowed = {DIAGNOSTIC, COMMIT_HELPER, MAKEFILE}
    unexpected = sorted(set(cached) - allowed)
    if unexpected:
        raise RuntimeError(
            "refusing to mix with pre-existing staged paths: " + ", ".join(unexpected)
        )

    if MAKEFILE in cached:
        run("restore", "--staged", "--", MAKEFILE)

    patch = selected_patch()
    with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False) as handle:
        handle.write(patch)
        patch_path = Path(handle.name)
    try:
        run("apply", "--cached", "--check", str(patch_path))
        run("apply", "--cached", str(patch_path))
    finally:
        patch_path.unlink(missing_ok=True)

    run("add", "--", DIAGNOSTIC, COMMIT_HELPER)
    staged = run("diff", "--cached", "--name-only").stdout.splitlines()
    expected = sorted([DIAGNOSTIC, COMMIT_HELPER, MAKEFILE])
    if sorted(staged) != expected:
        raise RuntimeError(
            "unexpected staged paths: " + ", ".join(staged) +
            f" (expected {', '.join(expected)})"
        )

    run("diff", "--cached", "--check")
    commit = run(
        "commit",
        "-m",
        "Add Windows share connectivity diagnostic",
    )
    sys.stdout.write(commit.stdout)
    sys.stderr.write(commit.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout, end="", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, end="", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
