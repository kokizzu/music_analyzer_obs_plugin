#!/usr/bin/env python3
"""Surgically commit the verified Fret Zealot legacy batch pacing fix."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CONTROLLER = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"
ANDROID_CHECK = "tests/check_android_project.py"


def run(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def staged_is_empty() -> bool:
    return subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0


def one_hunk(diff: str, needle: str) -> str:
    lines = diff.splitlines(keepends=True)
    first_hunk = next((index for index, line in enumerate(lines) if line.startswith("@@")), None)
    if first_hunk is None:
        raise RuntimeError(f"no diff hunk contains {needle!r}")
    header = "".join(lines[:first_hunk])
    start = first_hunk
    for index in range(first_hunk + 1, len(lines) + 1):
        if index == len(lines) or lines[index].startswith("@@"):
            hunk = "".join(lines[start:index])
            if needle in hunk:
                return header + hunk
            start = index
    raise RuntimeError(f"no diff hunk contains {needle!r}")


def main() -> int:
    if not staged_is_empty():
        staged_names = run("git", "diff", "--cached", "--name-only").splitlines()
        if staged_names != [CONTROLLER]:
            raise RuntimeError("refusing to modify a non-empty index")
        run("git", "restore", "--staged", "--", CONTROLLER)

    controller_diff = run("git", "diff", "--", CONTROLLER)
    required = (
        "LEGACY_BATCH_SETTLE_MILLIS = 750L",
        "physically settled so AUTO-root changes coalesce without interleaving",
    )
    if not controller_diff or not all(text in controller_diff for text in required):
        raise RuntimeError("controller diff does not match the verified batch pacing fix")
    controller_source = Path(CONTROLLER).read_text(encoding="utf-8")
    if ("LEGACY_FRAME_SETTLE_MILLIS" in controller_source
            or "LEGACY_BATCH_FALLBACK_MILLIS" in controller_source):
        raise RuntimeError("controller diff still contains an obsolete completion interval")
    run("git", "apply", "--cached", "-", input_text=controller_diff)

    check_diff = run("git", "diff", "--unified=5", "--", ANDROID_CHECK)
    timing_hunk = one_hunk(check_diff, "LEGACY_BATCH_SETTLE_MILLIS = 750L")
    if "LEGACY_FRAME_SETTLE_MILLIS = 250L" not in timing_hunk:
        raise RuntimeError("Android check hunk does not replace the obsolete settle contract")
    run("git", "apply", "--cached", "-", input_text=timing_hunk)

    run("git", "commit", "-m", "Pace Fret Zealot legacy LED batches")
    print("Committed verified Fret Zealot legacy batch pacing fix.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
