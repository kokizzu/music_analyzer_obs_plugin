#!/usr/bin/env python3
"""Commit visible-recall reporting without staging unrelated Makefile work."""

from __future__ import annotations

import argparse
import subprocess
import sys


FILES = (
    "scripts/report_guitar_profile_search.py",
    "scripts/report_real_note_visible_recall.py",
    "scripts/manage_visible_recall_reporting_commit.py",
)
MAKEFILE_BLOCK = '''

.PHONY: report-guitar-profile-search-details
report-guitar-profile-search-details: scripts/report_guitar_profile_search.py
	python3 scripts/report_guitar_profile_search.py --details
.PHONY: report-vocal-profile-search-details
report-vocal-profile-search-details: scripts/report_guitar_profile_search.py
	python3 scripts/report_guitar_profile_search.py --family vocals --details
.PHONY: report-real-note-visible-recall
report-real-note-visible-recall: scripts/report_real_note_visible_recall.py
	python3 scripts/report_real_note_visible_recall.py
.PHONY: report-real-note-visible-recall-details
report-real-note-visible-recall-details: scripts/report_real_note_visible_recall.py
	python3 scripts/report_real_note_visible_recall.py --details
.PHONY: plan-visible-recall-reporting-commit commit-visible-recall-reporting push-visible-recall-reporting
plan-visible-recall-reporting-commit: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py plan
commit-visible-recall-reporting: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py commit
push-visible-recall-reporting: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py push
'''
STAGED = ("Makefile",) + FILES


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=True).stdout


def staged_names() -> tuple[str, ...]:
    return tuple(line for line in run("git", "diff", "--cached", "--name-only").splitlines() if line)


def stage() -> None:
    run("git", "add", "--", *FILES)
    makefile = run("git", "show", ":Makefile")
    if "report-real-note-visible-recall" in makefile:
        raise RuntimeError("visible recall Makefile targets are already staged")
    object_id = run("git", "hash-object", "-w", "--stdin", input_text=makefile.rstrip("\n") + MAKEFILE_BLOCK).strip()
    run("git", "update-index", "--cacheinfo", f"100644,{object_id},Makefile")
    names = set(staged_names())
    if names != set(STAGED):
        raise RuntimeError(f"refusing unexpected staged paths: {sorted(names)}")


def plan() -> None:
    print("worktree-status=")
    print(run("git", "status", "--short"), end="")
    print("cached-paths=")
    print("\n".join(staged_names()))


def commit() -> None:
    stage()
    run("git", "commit", "-m", "test: measure visible full-mix row recall")
    print(run("git", "show", "--stat", "--oneline", "HEAD"), end="")


def push() -> None:
    print(run("git", "push"), end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "commit", "push"))
    args = parser.parse_args()
    try:
        if args.command == "plan":
            plan()
        elif args.command == "commit":
            commit()
        else:
            push()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error={error}", file=sys.stderr)
        raise SystemExit(1)
