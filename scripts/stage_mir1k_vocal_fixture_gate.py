#!/usr/bin/env python3
"""Stage only the MIR-1K full-mix regression fixture and its Make target."""

from __future__ import annotations

import difflib
import subprocess


MAKEFILE = "Makefile"
FIXTURE = "tests/fixtures/mir1k_clean_vocals"
ANCHOR = '''.PHONY: apply-mir1k-vocal-test-fixtures
apply-mir1k-vocal-test-fixtures:
\tpython3 scripts/sync_mir1k_vocal_test_fixtures.py apply
'''
BLOCK = '''
.PHONY: test-mir1k-vocal-full-mix
test-mir1k-vocal-full-mix: $(BUILD_DIR)/analyzer_real_note_samples tests/fixtures/mir1k_clean_vocals/manifest.tsv scripts/run_with_duration.sh
\t$(RUN_WITH_DURATION) analyzer_mir1k_vocal_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=221 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="tests/fixtures/mir1k_clean_vocals" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=221 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=70 $(BUILD_DIR)/analyzer_real_note_samples
'''


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, check=True, text=True, input=input_text, stdout=subprocess.PIPE).stdout


def main() -> int:
    if run("git", "diff", "--cached", "--name-only").strip():
        raise RuntimeError("refusing to modify a non-empty index")
    manifest = f"{FIXTURE}/manifest.tsv"
    tracked = run("git", "ls-files", "--", FIXTURE).splitlines()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", FIXTURE],
                               check=True, text=True, stdout=subprocess.PIPE).stdout.splitlines()
    if manifest in tracked and len(tracked) >= 222:
        fixture_rows: list[str] = []
    elif manifest in untracked and len(untracked) == 222:
        fixture_rows = sorted(untracked)
    else:
        raise RuntimeError(
            f"expected 222 tracked or untracked MIR-1K fixture files, got tracked={len(tracked)} "
            f"untracked={len(untracked)}")

    base = run("git", "show", f"HEAD:{MAKEFILE}")
    if base.count(ANCHOR) != 1 or BLOCK in base:
        raise RuntimeError("unexpected MIR-1K Makefile anchor")
    desired = base.replace(ANCHOR, ANCHOR + BLOCK)
    patch = "".join(difflib.unified_diff(
        base.splitlines(keepends=True), desired.splitlines(keepends=True),
        fromfile=f"a/{MAKEFILE}", tofile=f"b/{MAKEFILE}", n=3,
    ))
    subprocess.run(["git", "apply", "--cached"], check=True, text=True, input=patch)
    if fixture_rows:
        subprocess.run(["git", "add", "--", FIXTURE], check=True)
    staged = run("git", "diff", "--cached", "--name-only").splitlines()
    if staged != [MAKEFILE, *fixture_rows]:
        raise RuntimeError("staged scope differs from the exact MIR-1K fixture gate")
    print(f"staged {len(fixture_rows)} fixture files and the MIR-1K full-mix gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
