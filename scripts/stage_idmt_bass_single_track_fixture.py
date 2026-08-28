#!/usr/bin/env python3
"""Stage only the compact IDMT bass fixture pipeline and its Makefile API."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    "scripts/import_idmt_bass_single_track_archive.py",
    "scripts/inspect_idmt_bass_single_track_layout.py",
    "scripts/diagnose_idmt_bass_single_track_archive.py",
    "scripts/summarize_idmt_bass_single_track_annotations.py",
    "scripts/prepare_idmt_bass_single_track_fixture.py",
    "scripts/run_idmt_bass_single_track_measurement.py",
    "scripts/summarize_idmt_bass_single_track_measurement.py",
    "tests/test_prepare_idmt_bass_single_track_fixture.py",
)
RULES = {
    "import-idmt-bass-single-track-archive": """.PHONY: import-idmt-bass-single-track-archive
import-idmt-bass-single-track-archive:
\t@python3 scripts/import_idmt_bass_single_track_archive.py
""",
    "inspect-idmt-bass-single-track-layout": """.PHONY: inspect-idmt-bass-single-track-layout
inspect-idmt-bass-single-track-layout:
\t@python3 scripts/inspect_idmt_bass_single_track_layout.py
""",
    "diagnose-idmt-bass-single-track-archive": """.PHONY: diagnose-idmt-bass-single-track-archive
diagnose-idmt-bass-single-track-archive:
\t@python3 scripts/diagnose_idmt_bass_single_track_archive.py
""",
    "summarize-idmt-bass-single-track-annotations": """.PHONY: summarize-idmt-bass-single-track-annotations
summarize-idmt-bass-single-track-annotations:
\t@python3 scripts/summarize_idmt_bass_single_track_annotations.py
""",
    "prepare-idmt-bass-single-track-fixture": """.PHONY: prepare-idmt-bass-single-track-fixture test-prepare-idmt-bass-single-track-fixture measure-idmt-bass-single-track test-idmt-bass-single-track
prepare-idmt-bass-single-track-fixture: import-idmt-bass-single-track-archive
\t@python3 scripts/prepare_idmt_bass_single_track_fixture.py

test-prepare-idmt-bass-single-track-fixture: prepare-idmt-bass-single-track-fixture
\t@python3 tests/test_prepare_idmt_bass_single_track_fixture.py

measure-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
\t@python3 scripts/run_idmt_bass_single_track_measurement.py

test-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
\t@python3 scripts/run_idmt_bass_single_track_measurement.py --min-recall 95
""",
    "summarize-idmt-bass-single-track-measurement": """.PHONY: summarize-idmt-bass-single-track-measurement
summarize-idmt-bass-single-track-measurement:
\t@python3 scripts/summarize_idmt_bass_single_track_measurement.py
""",
}


def run(arguments: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=ROOT, input=input_text, text=True,
                          capture_output=True, check=True)


def main() -> int:
    missing = [path for path in PATHS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("missing fixture paths: " + ", ".join(missing))
    staged = run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines()
    if staged:
        raise SystemExit("refusing to stage into a nonempty index: " + ", ".join(staged))
    makefile = run(["git", "show", ":Makefile"]).stdout
    additions = [rule for target, rule in RULES.items() if f"{target}:" not in makefile]
    if additions:
        makefile = makefile.rstrip() + "\n\n" + "\n".join(additions)
    run(["git", "add", "--", *PATHS])
    make_hash = run(["git", "hash-object", "-w", "--stdin"], input_text=makefile).stdout.strip()
    run(["git", "update-index", "--add", "--cacheinfo", f"100644,{make_hash},Makefile"])
    staged = run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines()
    expected = set(PATHS) | {"Makefile"}
    unexpected = set(staged) - expected
    if unexpected:
        raise SystemExit("unexpected staged paths: " + ", ".join(sorted(unexpected)))
    print("staged compact IDMT bass fixture paths:")
    for path in staged:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        sys.stderr.write(error.stderr)
        raise SystemExit(error.returncode)
