#!/usr/bin/env python3
"""Plan or commit only the verified Fret Zealot AUTO-root stabilization hunks."""

import subprocess
import sys
import re


FILES = (
    "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java",
    "tests/check_android_project.py",
)
MARKERS = (
    "This also applies to the first render after a connection.",
    '"partial scales are worse" in external_devices and',
    "Android AUTO root updates must not bypass stabilization after connection",
)


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(
        args,
        check=True,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout


def selected_hunks() -> tuple[str, str]:
    diff = run("git", "diff", "--no-ext-diff", "--unified=0", "--", *FILES)
    sections = re.split(r"(?=^diff --git )", diff, flags=re.MULTILINE)
    selected: list[str] = []
    for section in sections:
        if not section:
            continue
        header, *hunks = re.split(r"(?=^@@ )", section, flags=re.MULTILINE)
        for hunk in hunks:
            text = hunk
            removes_force_bypass = (
                "if (force) {" in text and "AUTO scale to preserve" in text
            )
            if removes_force_bypass or any(marker in text for marker in MARKERS):
                selected.append(header + hunk)
    if len(selected) != len(MARKERS) + 1:
        raise SystemExit("expected only the AUTO bypass removal and its two regression hunks")
    patch = "".join(selected)
    if "partial scales are worse" not in patch:
        raise SystemExit("dispatcher hunk is not the expected AUTO-root stabilization change")
    if "Android AUTO root updates" not in patch:
        raise SystemExit("regression assertion hunk is missing")
    return patch, diff


def main() -> None:
    apply = len(sys.argv) == 2 and sys.argv[1] == "apply"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not apply):
        raise SystemExit("usage: commit_verified_fret_zealot_auto_stabilization.py [apply]")
    patch, diff = selected_hunks()
    if not apply:
        print("## selected hunks")
        print(patch, end="")
        print("## full candidate diff")
        print(diff, end="")
        return
    if run("git", "diff", "--cached", "--name-only").strip():
        raise SystemExit("refusing to commit with pre-existing staged changes")
    subprocess.run(
        ["git", "apply", "--cached", "--unidiff-zero", "-"],
        check=True,
        input=patch,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Stabilize automatic Fret Zealot scale updates"],
        check=True,
    )


if __name__ == "__main__":
    main()
