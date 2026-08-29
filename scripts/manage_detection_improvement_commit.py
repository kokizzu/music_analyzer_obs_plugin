#!/usr/bin/env python3
"""Plan, stage, commit, and push only the real-audio detection work."""

from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAKEFILE = ROOT / "Makefile"
MESSAGE = "analyzer: improve real mix instrument recall"
PATHS = (
    "src/analyzer.cpp",
    "tests/analyzer_real_note_samples.cpp",
    "scripts/debug_urmp_mixture_case.py",
    "scripts/inspect_chord_detector_source.py",
    "scripts/inspect_analysis_snapshot_source.py",
    "scripts/inspect_full_mix_debug_write_source.py",
    "scripts/inspect_full_mix_display_flow_source.py",
    "scripts/inspect_full_mix_other_predicates_source.py",
    "scripts/inspect_full_mix_owner_source.py",
    "scripts/inspect_mixed_other_display_source.py",
    "scripts/inspect_mixed_owner_source.py",
    "scripts/inspect_real_instrument_expansion_preparer_source.py",
    "scripts/inspect_real_instrument_expansion_test_source.py",
    "scripts/inspect_real_instrument_reporter_source.py",
    "scripts/inspect_real_note_attribute_source.py",
    "scripts/inspect_real_note_test_source.py",
    "scripts/plan_urmp_mixture_cases.py",
    "scripts/prepare_real_instrument_expansion.py",
    "scripts/prepare_nsynth_test_fixtures.sh",
    "scripts/prepare_urmp_analyzer_cases.py",
    "scripts/prepare_urmp_multitrack_fixtures.py",
    "scripts/report_full_mix_bass_attributes.py",
    "scripts/report_full_mix_bass_attributes_script.py",
    "scripts/report_full_mix_display_mirror_source.py",
    "scripts/report_full_mix_ownership_signatures.py",
    "scripts/report_full_mix_vocal_guitar_collisions.py",
    "scripts/report_guitar_profile_search.py",
    "scripts/report_full_mix_vocal_failures.py",
    "scripts/inspect_vocal_display_source.py",
    "scripts/report_real_instrument_expansion_bass_attributes.py",
    "scripts/report_real_note_fixture_inventory.py",
    "scripts/report_real_note_full_mix_attributes.py",
    "scripts/report_timbre_classifier.py",
    "scripts/report_tinysol_fixture_categories.py",
    "scripts/report_urmp_analyzer_cases.py",
    "scripts/report_urmp_chord_cases.py",
    "scripts/report_urmp_chord_opportunities.py",
    "scripts/report_urmp_mixture_ownership_attributes.py",
    "scripts/report_urmp_multitrack_inventory.py",
    "scripts/report_urmp_other_recovery_profile.py",
    "scripts/test_real_instrument_expansion.py",
    "scripts/check_nsynth_test_fixtures.py",
    "scripts/manage_detection_improvement_commit.py",
)
MAKEFILE_BLOCK_START = ".PHONY: report-full-mix-bass-attributes"
MAKEFILE_BLOCK_END = "report-full-mix-other-attributes: build/analyzer_real_note_samples"


def git(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, input=input_text,
                          capture_output=True, check=False)


def require(result: subprocess.CompletedProcess[str], action: str) -> None:
    if result.returncode == 0:
        return
    sys.stderr.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise SystemExit(f"{action} failed")


def makefile_patch() -> str:
    base = git("show", "HEAD:Makefile")
    require(base, "read HEAD Makefile")
    current_text = MAKEFILE.read_text(encoding="utf-8")
    start = current_text.find(MAKEFILE_BLOCK_START)
    end = current_text.find(MAKEFILE_BLOCK_END, start)
    if start < 0 or end < 0:
        raise SystemExit("detection Makefile block was not found")
    block = current_text[start:end]
    base_text = base.stdout
    base_start = base_text.find(MAKEFILE_BLOCK_START)
    if base_start >= 0:
        base_end = base_text.find(MAKEFILE_BLOCK_END, base_start)
        if base_end < 0:
            raise SystemExit("HEAD detection Makefile block end was not found")
        desired = base_text[:base_start] + block + base_text[base_end:]
    else:
        anchor = base_text.find(MAKEFILE_BLOCK_END)
        if anchor < 0:
            raise SystemExit("HEAD Makefile anchor was not found")
        desired = base_text[:anchor] + block + base_text[anchor:]
    return "".join(difflib.unified_diff(
        base_text.splitlines(keepends=True), desired.splitlines(keepends=True),
        fromfile="a/Makefile", tofile="b/Makefile"))


def require_clean_index() -> None:
    result = git("diff", "--cached", "--quiet")
    if result.returncode == 0:
        return
    if result.returncode == 1:
        raise SystemExit("refusing to mix this commit with existing staged changes")
    require(result, "inspect staged changes")


def plan() -> None:
    missing = [path for path in PATHS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("missing planned paths:\n" + "\n".join(missing))
    patch = makefile_patch()
    if not patch:
        raise SystemExit("detection Makefile block has no staged difference")
    print("paths-to-stage=")
    for path in PATHS:
        print(f"+ {path}")
    print("+ Makefile (detection targets only)")
    print(f"makefile-patch-lines={len(patch.splitlines())}")


def apply() -> None:
    require_clean_index()
    plan()
    require(git("add", "--", *PATHS), "stage detection paths")
    require(git("apply", "--cached", "--whitespace=nowarn", input_text=makefile_patch()),
            "stage detection Makefile targets")
    require(git("diff", "--cached", "--check"), "validate staged diff")
    staged = git("diff", "--cached", "--name-only")
    require(staged, "list staged paths")
    allowed = set(PATHS) | {"Makefile"}
    unexpected = sorted(set(staged.stdout.splitlines()) - allowed)
    if unexpected:
        raise SystemExit("unexpected staged paths:\n" + "\n".join(unexpected))
    print("staged-detection-paths=")
    print(staged.stdout, end="")


def commit() -> None:
    staged = git("diff", "--cached", "--name-only")
    require(staged, "list staged paths")
    if not staged.stdout.strip():
        raise SystemExit("no staged detection changes; run apply first")
    allowed = set(PATHS) | {"Makefile"}
    unexpected = sorted(set(staged.stdout.splitlines()) - allowed)
    if unexpected:
        raise SystemExit("refusing commit with unexpected staged paths:\n" + "\n".join(unexpected))
    require(git("commit", "-m", MESSAGE), "commit detection improvement")


def push() -> None:
    require(git("push"), "push detection improvement")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply", "commit", "push"}:
        raise SystemExit("usage: manage_detection_improvement_commit.py plan|apply|commit|push")
    {"plan": plan, "apply": apply, "commit": commit, "push": push}[sys.argv[1]]()


if __name__ == "__main__":
    main()
