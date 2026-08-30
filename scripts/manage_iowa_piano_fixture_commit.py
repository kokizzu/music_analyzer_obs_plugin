#!/usr/bin/env python3
"""Commit Iowa Piano fixture tooling without staging unrelated Makefile edits."""

from __future__ import annotations

import argparse
import subprocess
import sys


FILES = (
    "README.md",
    "scripts/prepare_iowa_piano_midrange_fixtures.py",
    "scripts/manage_iowa_piano_fixture_download.py",
    "scripts/test_iowa_piano_midrange.py",
    "scripts/report_iowa_piano_attributes.py",
    "scripts/manage_iowa_piano_fixture_commit.py",
)
MAKEFILE_BLOCK = '''

.PHONY: plan-iowa-piano-midrange-fixtures probe-iowa-piano-midrange-fixtures apply-iowa-piano-midrange-fixtures verify-iowa-piano-midrange-fixtures
plan-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py plan
probe-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py probe
apply-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py apply
verify-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py verify
.PHONY: start-iowa-piano-midrange-fixtures status-iowa-piano-midrange-fixtures stop-iowa-piano-midrange-fixtures
start-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py start
status-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py status
stop-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py stop
.PHONY: test-iowa-piano-midrange-samples
test-iowa-piano-midrange-samples: build/analyzer_real_note_samples build/iowa_piano_midrange_samples scripts/test_iowa_piano_midrange.py
	python3 scripts/test_iowa_piano_midrange.py --verify
.PHONY: report-iowa-piano-midrange-samples
report-iowa-piano-midrange-samples: build/analyzer_real_note_samples build/iowa_piano_midrange_samples scripts/test_iowa_piano_midrange.py
	python3 scripts/test_iowa_piano_midrange.py --details --attributes
.PHONY: report-iowa-piano-attributes
report-iowa-piano-attributes: report-iowa-piano-midrange-samples scripts/report_iowa_piano_attributes.py
	python3 scripts/report_iowa_piano_attributes.py
.PHONY: publish-iowa-piano-midrange-partial
publish-iowa-piano-midrange-partial: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py publish-partial
.PHONY: plan-iowa-piano-fixture-commit commit-iowa-piano-fixture push-iowa-piano-fixture
plan-iowa-piano-fixture-commit: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py plan
commit-iowa-piano-fixture: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py commit
push-iowa-piano-fixture: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py push
'''
STAGED = ("Makefile",) + FILES


def run(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(args, text=True, input=input_text, capture_output=True, check=True)
    return result.stdout


def staged_names() -> tuple[str, ...]:
    return tuple(line for line in run("git", "diff", "--cached", "--name-only").splitlines() if line)


def assert_staged() -> None:
    unexpected = set(staged_names()) - set(STAGED)
    if unexpected:
        raise RuntimeError(f"refusing to commit unrelated staged paths: {sorted(unexpected)}")
    missing = set(STAGED) - set(staged_names())
    if missing:
        raise RuntimeError(f"expected staged paths are missing: {sorted(missing)}")


def stage() -> None:
    run("git", "add", "--", *FILES)
    indexed_makefile = run("git", "show", ":Makefile")
    if "plan-iowa-piano-midrange-fixtures" in indexed_makefile:
        raise RuntimeError("Iowa Piano Makefile targets are already staged")
    object_id = run("git", "hash-object", "-w", "--stdin", input_text=indexed_makefile.rstrip("\n") + MAKEFILE_BLOCK).strip()
    run("git", "update-index", "--cacheinfo", f"100644,{object_id},Makefile")
    assert_staged()


def plan() -> None:
    print("worktree-status=")
    print(run("git", "status", "--short"), end="")
    print("cached-paths=")
    print("\n".join(staged_names()))


def commit() -> None:
    stage()
    run("git", "commit", "-m", "test: add Iowa piano real-audio corpus workflow")
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
