#!/usr/bin/env python3
"""Commit and push only the pre-staged MIR-1K vocal fixture increment."""

from __future__ import annotations

import subprocess


ALLOWED = (
    "Makefile",
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
    "tests/fixtures/mir1k_clean_vocals/",
)


def run(arguments: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, check=True, text=True, **kwargs)


def main() -> int:
    paths = run(["git", "diff", "--cached", "--name-only"], capture_output=True).stdout.splitlines()
    if not paths:
        raise SystemExit("no staged MIR-1K fixture paths")
    unexpected = [path for path in paths if path not in ALLOWED and not path.startswith(ALLOWED[-1])]
    if unexpected:
        raise SystemExit("refusing to commit unexpected staged paths:\n" + "\n".join(unexpected))
    run(["git", "commit", "-m", "Add labelled MIR-1K vocal regression fixtures"])
    run(["git", "push"])
    print(run(["git", "log", "-1", "--oneline"], capture_output=True).stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
