#!/usr/bin/env python3
"""Safely stage, commit, and push the real-drum regression improvement."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    "src/analyzer.cpp",
    "tests/analyzer_real_drum_samples.cpp",
    "scripts/report_drum_fixture_candidates.py",
    "scripts/report_idmt_drum_fixture_manifest.py",
    "scripts/inspect_real_note_drum_test_source.py",
    "scripts/inspect_analyzer_test_utils_source.py",
    "scripts/inspect_drum_detector_source.py",
    "scripts/run_real_drum_source_matrix.sh",
    "scripts/run_real_drum_source_report.sh",
    "scripts/test_real_drum_samples.sh",
    "scripts/manage_detection_improvement_commit.py",
    "scripts/manage_real_drum_improvement_commit.py",
    "Makefile",
)
STAGE_PATHS = tuple(path for path in PATHS if path != "Makefile")
MESSAGE = "analyzer: improve real drum display recall"


def run(*args: str, capture: bool = False, stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=capture, input=stdin_text)


def status() -> str:
    return run("git", "status", "--short", "--", *PATHS, capture=True).stdout


def plan() -> None:
    print("real-drum-path-status=")
    print(status(), end="")
    makefile_diff = run("git", "diff", "--", "Makefile", capture=True).stdout
    print("real-drum-makefile-diff=")
    print(makefile_diff, end="")


def stage_real_drum_makefile_hunk() -> None:
    diff = run("git", "diff", "-U0", "--", "Makefile", capture=True).stdout
    if not diff:
        return
    lines = diff.splitlines(keepends=True)
    header_end = next((index for index, line in enumerate(lines) if line.startswith("@@")), len(lines))
    header = lines[:header_end]
    hunks = []
    current = []
    for line in lines[header_end:]:
        if line.startswith("@@") and current:
            hunks.append(current)
            current = []
        current.append(line)
    if current:
        hunks.append(current)
    selected = [hunk for hunk in hunks if any("report-drum-fixture-candidates" in line for line in hunk)]
    if not selected:
        return
    if len(selected) != 1:
        raise SystemExit("expected exactly one real-drum Makefile hunk")
    run("git", "apply", "--cached", "--unidiff-zero", stdin_text="".join(header + selected[0]))


def apply() -> None:
    if not status().strip():
        raise SystemExit("no real-drum changes to stage")
    pre_staged = run("git", "diff", "--cached", "--name-only", capture=True).stdout
    pre_staged_paths = {line for line in pre_staged.splitlines() if line}
    allowed_pre_staged = {"scripts/manage_real_drum_improvement_commit.py"}
    if pre_staged_paths - allowed_pre_staged:
        raise SystemExit("refusing to commit pre-staged changes:\n" + pre_staged)
    run("git", "diff", "--check", "--", *PATHS)
    run("git", "add", "--", *STAGE_PATHS)
    stage_real_drum_makefile_hunk()
    run("git", "commit", "-m", MESSAGE)


def push() -> None:
    upstream = run("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", capture=True).stdout.strip()
    if not upstream:
        raise SystemExit("current branch has no upstream")
    run("git", "fetch")
    try:
        run("git", "merge-base", "--is-ancestor", upstream, "HEAD")
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"{upstream} has commits not present in HEAD; rebase is required") from error
    run("git", "push")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply", "push"}:
        raise SystemExit("usage: manage_real_drum_improvement_commit.py plan|apply|push")
    {"plan": plan, "apply": apply, "push": push}[sys.argv[1]]()


if __name__ == "__main__":
    main()
