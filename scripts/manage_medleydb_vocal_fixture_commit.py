#!/usr/bin/env python3
"""Commit MedleyDB Vocal fixture tooling without staging unrelated Makefile work."""

from __future__ import annotations

import argparse
import subprocess
import sys


FILES = (
    "README.md",
    "scripts/probe_medleydb_sample.py",
    "scripts/manage_medleydb_sample_download.py",
    "scripts/inspect_medleydb_sample_archive.py",
    "scripts/inspect_medleydb_vocal_annotations.py",
    "scripts/prepare_medleydb_vocal_mix_fixtures.py",
    "scripts/test_medleydb_vocal_mix.py",
    "scripts/manage_medleydb_vocal_fixture_commit.py",
)
MAKEFILE_BLOCK = '''

.PHONY: probe-medleydb-sample
probe-medleydb-sample: scripts/probe_medleydb_sample.py
	python3 scripts/probe_medleydb_sample.py
.PHONY: start-medleydb-sample-download status-medleydb-sample-download stop-medleydb-sample-download
start-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py start
status-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py status
stop-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py stop
.PHONY: inspect-medleydb-sample-archive
inspect-medleydb-sample-archive: scripts/inspect_medleydb_sample_archive.py
	python3 scripts/inspect_medleydb_sample_archive.py
.PHONY: inspect-medleydb-vocal-annotations
inspect-medleydb-vocal-annotations: scripts/inspect_medleydb_vocal_annotations.py
	python3 scripts/inspect_medleydb_vocal_annotations.py
.PHONY: plan-medleydb-vocal-mix-fixtures apply-medleydb-vocal-mix-fixtures verify-medleydb-vocal-mix-fixtures
plan-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py plan
apply-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py apply
verify-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py verify
.PHONY: report-medleydb-vocal-mix test-medleydb-vocal-mix
report-medleydb-vocal-mix: build/analyzer_real_note_samples build/medleydb_vocal_mix_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py
test-medleydb-vocal-mix: build/analyzer_real_note_samples build/medleydb_vocal_mix_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --verify
.PHONY: plan-medleydb-vocal-fixture-commit commit-medleydb-vocal-fixture push-medleydb-vocal-fixture
plan-medleydb-vocal-fixture-commit: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py plan
commit-medleydb-vocal-fixture: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py commit
push-medleydb-vocal-fixture: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py push
'''
STAGED = ("Makefile",) + FILES


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=True).stdout


def staged_names() -> tuple[str, ...]:
    return tuple(line for line in run("git", "diff", "--cached", "--name-only").splitlines() if line)


def stage() -> None:
    run("git", "add", "--", *FILES)
    makefile = run("git", "show", ":Makefile")
    if "test-medleydb-vocal-mix" in makefile:
        raise RuntimeError("MedleyDB Vocal Makefile targets are already staged")
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
    run("git", "commit", "-m", "test: add annotated MedleyDB vocal mix fixtures")
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
