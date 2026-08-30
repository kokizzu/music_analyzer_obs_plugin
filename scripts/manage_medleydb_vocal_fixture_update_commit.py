#!/usr/bin/env python3
"""Commit MedleyDB stem-versus-mix diagnostics without staging unrelated work."""

from __future__ import annotations

import argparse
import subprocess
import sys


FILES = (
    "README.md",
    "scripts/inspect_medleydb_sample_archive.py",
    "scripts/prepare_medleydb_vocal_mix_fixtures.py",
    "scripts/test_medleydb_vocal_mix.py",
    "scripts/report_medleydb_vocal_mix_attributes.py",
    "scripts/manage_medleydb_vocal_fixture_update_commit.py",
)
MAKEFILE_BLOCK = '''

.PHONY: report-medleydb-vocal-mix-attributes
report-medleydb-vocal-mix-attributes: report-medleydb-vocal-mix scripts/report_medleydb_vocal_mix_attributes.py
	python3 scripts/report_medleydb_vocal_mix_attributes.py
.PHONY: report-medleydb-vocal-stem test-medleydb-vocal-stem
report-medleydb-vocal-stem: build/analyzer_real_note_samples build/medleydb_vocal_stem_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --stem
test-medleydb-vocal-stem: build/analyzer_real_note_samples build/medleydb_vocal_stem_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --stem --verify
.PHONY: report-medleydb-vocal-stem-attributes
report-medleydb-vocal-stem-attributes: report-medleydb-vocal-stem scripts/report_medleydb_vocal_mix_attributes.py
	python3 scripts/report_medleydb_vocal_mix_attributes.py --stem
.PHONY: plan-medleydb-vocal-fixture-update-commit commit-medleydb-vocal-fixture-update push-medleydb-vocal-fixture-update
plan-medleydb-vocal-fixture-update-commit: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py plan
commit-medleydb-vocal-fixture-update: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py commit
push-medleydb-vocal-fixture-update: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py push
'''
STAGED = ("Makefile",) + FILES


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=True).stdout


def staged_names() -> tuple[str, ...]:
    return tuple(line for line in run("git", "diff", "--cached", "--name-only").splitlines() if line)


def stage() -> None:
    run("git", "add", "--", *FILES)
    makefile = run("git", "show", ":Makefile")
    if "test-medleydb-vocal-stem" not in makefile:
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
    run("git", "commit", "-m", "test: compare MedleyDB vocal stem and mix recall")
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
