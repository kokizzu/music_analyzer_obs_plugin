#!/usr/bin/env python3
"""Commit only the reproducible vocadito fixture workflow, never its audio cache."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
FILES = (
    "scripts/manage_vocadito_fixtures.py",
    "scripts/prepare_vocadito_midrange_fixtures.py",
    "scripts/test_vocadito_midrange.py",
    "scripts/manage_vocadito_fixture_commit.py",
)
MESSAGE = "tests: add annotated vocal midrange corpus"
MAKEFILE_BLOCK = """
.PHONY: inspect-vocadito-fixtures plan-vocadito-fixtures apply-vocadito-fixtures
inspect-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py inspect

plan-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py plan

apply-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py apply

.PHONY: plan-vocadito-midrange-fixtures apply-vocadito-midrange-fixtures
plan-vocadito-midrange-fixtures: scripts/prepare_vocadito_midrange_fixtures.py
	python3 scripts/prepare_vocadito_midrange_fixtures.py plan

apply-vocadito-midrange-fixtures: scripts/prepare_vocadito_midrange_fixtures.py
	python3 scripts/prepare_vocadito_midrange_fixtures.py apply

.PHONY: report-vocadito-midrange-samples test-vocadito-midrange-samples
report-vocadito-midrange-samples: build/analyzer_real_note_samples apply-vocadito-midrange-fixtures scripts/test_vocadito_midrange.py
	python3 scripts/test_vocadito_midrange.py

test-vocadito-midrange-samples: build/analyzer_real_note_samples apply-vocadito-midrange-fixtures scripts/test_vocadito_midrange.py
	python3 scripts/test_vocadito_midrange.py --verify

.PHONY: plan-vocadito-fixture-commit commit-vocadito-fixture-commit push-vocadito-fixture-commit
plan-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py plan

commit-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py commit

push-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py push
""".lstrip()


def git(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, input=input_text, capture_output=True
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def stage_makefile_block() -> None:
    working = MAKEFILE.read_text(encoding="utf-8")
    if MAKEFILE_BLOCK not in working:
        raise RuntimeError("the complete vocadito Makefile block is missing from the working tree")
    head = git("show", "HEAD:Makefile").stdout
    index = git("show", ":Makefile").stdout
    if index != head:
        raise RuntimeError("Makefile already has staged changes; preserve them and retry")
    if MAKEFILE_BLOCK in head:
        return
    staged = head.rstrip() + "\n\n" + MAKEFILE_BLOCK
    object_id = git("hash-object", "-w", "--stdin", input_text=staged).stdout.strip()
    git("update-index", "--add", "--cacheinfo", f"100644,{object_id},Makefile")


def stage() -> None:
    stage_makefile_block()
    git("add", "--", *FILES)
    git("diff", "--cached", "--check")


def plan() -> int:
    print("vocadito-commit-files=")
    for path in ("Makefile", *FILES):
        status = git("status", "--short", "--", path).stdout.rstrip()
        print(status or f"  {path}: unchanged")
    print("external-audio=excluded (build/vocadito_midrange_samples is a symlink)")
    return 0


def commit() -> int:
    stage()
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("vocadito fixture workflow already committed")
        return 0
    result = git("commit", "-m", MESSAGE)
    print(result.stdout.rstrip())
    return 0


def push() -> int:
    result = git("push")
    print(result.stdout.rstrip())
    if result.stderr.strip():
        print(result.stderr.rstrip())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "commit", "push"))
    command = parser.parse_args().command
    if command == "plan":
        return plan()
    if command == "commit":
        return commit()
    return push()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
