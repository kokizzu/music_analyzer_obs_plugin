#!/usr/bin/env python3
"""Stage only the self-contained MIR-1K vocal regression fixture increment."""

from __future__ import annotations

import difflib
import subprocess


PATHS = (
    "scripts/plan_mir1k_vocal_fixtures.py",
    "scripts/import_mir1k_vocal_archive.py",
    "scripts/status_mir1k_vocal_import.py",
    "scripts/inspect_mir1k_vocal_layout.py",
    "scripts/inspect_mir1k_vocal_pitch_labels.py",
    "scripts/prepare_mir1k_vocal_fixtures.py",
    "scripts/sync_mir1k_vocal_test_fixtures.py",
    "scripts/clean_mir1k_vocal_test_fixture_stale.py",
    "scripts/run_mir1k_vocal_fixture_test.py",
    "scripts/stage_mir1k_vocal_fixture_commit.py",
    "tests/fixtures/mir1k_clean_vocals",
)

MAKEFILE_BLOCK = """
# Self-contained MIR-1K clean-vocal regression fixtures.
.PHONY: plan-mir1k-vocal-fixtures
plan-mir1k-vocal-fixtures:
	python3 scripts/plan_mir1k_vocal_fixtures.py

.PHONY: import-mir1k-vocal-archive
import-mir1k-vocal-archive:
	python3 scripts/import_mir1k_vocal_archive.py

.PHONY: status-mir1k-vocal-import
status-mir1k-vocal-import:
	python3 scripts/status_mir1k_vocal_import.py

.PHONY: inspect-mir1k-vocal-layout
inspect-mir1k-vocal-layout:
	python3 scripts/inspect_mir1k_vocal_layout.py

.PHONY: inspect-mir1k-vocal-pitch-labels
inspect-mir1k-vocal-pitch-labels:
	python3 scripts/inspect_mir1k_vocal_pitch_labels.py

.PHONY: prepare-mir1k-vocal-fixtures
prepare-mir1k-vocal-fixtures:
	python3 scripts/prepare_mir1k_vocal_fixtures.py

.PHONY: plan-mir1k-vocal-test-fixtures
plan-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py plan

.PHONY: apply-mir1k-vocal-test-fixtures
apply-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py apply

.PHONY: plan-clean-mir1k-vocal-test-fixture-stale
plan-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py plan

.PHONY: apply-clean-mir1k-vocal-test-fixture-stale
apply-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py apply

.PHONY: test-mir1k-clean-vocal-fixtures
test-mir1k-clean-vocal-fixtures: build/analyzer_real_note_samples
	python3 scripts/run_mir1k_vocal_fixture_test.py

.PHONY: test-mir1k-clean-vocal-fixtures-full-mix
test-mir1k-clean-vocal-fixtures-full-mix: build/analyzer_real_note_samples
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix
"""


def run(arguments: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, check=True, text=True, **kwargs)


def main() -> int:
    staged = run(["git", "diff", "--cached", "--name-only"], capture_output=True).stdout.strip()
    if staged:
        raise SystemExit("refusing to mix this increment with already staged paths:\n" + staged)
    run(["git", "add", "--", *PATHS])
    indexed = run(["git", "show", ":Makefile"], capture_output=True).stdout
    if "test-mir1k-clean-vocal-fixtures:" not in indexed:
        updated = indexed.rstrip("\n") + "\n" + MAKEFILE_BLOCK
        patch = "".join(difflib.unified_diff(
            indexed.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile="a/Makefile", tofile="b/Makefile"))
        run(["git", "apply", "--cached", "--whitespace=nowarn", "-"], input=patch)
    summary = run(["git", "diff", "--cached", "--stat"], capture_output=True).stdout
    print(summary.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
