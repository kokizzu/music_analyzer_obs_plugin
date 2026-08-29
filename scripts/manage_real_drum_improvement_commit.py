#!/usr/bin/env python3
"""Safely stage, commit, and push the real-drum regression improvement."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    "src/analyzer.cpp",
    "tests/analyzer_real_drum_samples.cpp",
    "tests/analyzer_internal.cpp",
    "scripts/report_drum_fixture_candidates.py",
    "scripts/report_idmt_drum_fixture_manifest.py",
    "scripts/inspect_real_note_drum_test_source.py",
    "scripts/inspect_analyzer_test_utils_source.py",
    "scripts/inspect_drum_detector_source.py",
    "scripts/run_real_drum_source_matrix.sh",
    "scripts/run_real_drum_source_report.sh",
    "scripts/test_real_drum_samples.sh",
    "scripts/manage_detection_improvement_commit.py",
    "scripts/manage_real_drum_improvement_commit.py",
    "scripts/inspect_chord_temporal_tests.py",
    "scripts/report_urmp_chord_cases.py",
    "scripts/report_urmp_other_recovery_profile.py",
    "scripts/report_urmp_chord_routes.py",
    "scripts/manage_urmp_profile_replay.py",
    "scripts/manage_analyzer_internal_test.py",
    "Makefile",
)
STAGE_PATHS = tuple(path for path in PATHS if path != "Makefile")
MESSAGE = "analyzer: recover dense low guitar bodies"


def run(*args: str, capture: bool = False, stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=capture, input=stdin_text)


def status() -> str:
    return run("git", "status", "--short", "--", *PATHS, capture=True).stdout


def plan() -> None:
    print("real-drum-path-status=")
    print(status(), end="")
    makefile_diff = run("git", "diff", "--", "Makefile", capture=True).stdout
    print("real-drum-makefile-diff=")
    print(makefile_diff, end="")


def stage_chord_temporal_makefile_target() -> None:
    block = (
        ".PHONY: inspect-chord-temporal-tests\n"
        "inspect-chord-temporal-tests: scripts/inspect_chord_temporal_tests.py\n"
        "\tpython3 scripts/inspect_chord_temporal_tests.py\n"
        "\n"
        ".PHONY: commit-chord-stability\n"
        "commit-chord-stability: scripts/manage_real_drum_improvement_commit.py\n"
        "\tpython3 scripts/manage_real_drum_improvement_commit.py apply\n"
        "\n"
        ".PHONY: push-chord-stability\n"
        "push-chord-stability: scripts/manage_real_drum_improvement_commit.py\n"
        "\tpython3 scripts/manage_real_drum_improvement_commit.py push\n"
    )
    anchor = (
        ".PHONY: inspect-chord-timing-source\n"
        "inspect-chord-timing-source: scripts/inspect_analyzer_section.py\n"
        "\tpython3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic \"kChordHoldSeconds\"\n"
    )
    worktree = (ROOT / "Makefile").read_text(encoding="utf-8")
    if block not in worktree:
        raise SystemExit("missing inspect-chord-temporal-tests target in Makefile")
    indexed = run("git", "show", ":Makefile", capture=True).stdout
    if block in indexed:
        return
    if anchor not in indexed:
        raise SystemExit("missing chord timing target in indexed Makefile")
    updated = indexed.replace(anchor, anchor + "\n" + block, 1)
    object_id = run("git", "hash-object", "-w", "--stdin", capture=True, stdin_text=updated).stdout.strip()
    run("git", "update-index", "--add", "--cacheinfo", f"100644,{object_id},Makefile")


def stage_temporal_tools_makefile_targets() -> None:
    block = (
        ".PHONY: report-urmp-chord-routes-cached start-analyzer-internal-test "
        "status-analyzer-internal-test start-urmp-profile-replay status-urmp-profile-replay\n"
        "report-urmp-chord-routes-cached: scripts/report_urmp_chord_routes.py\n"
        "\tpython3 scripts/report_urmp_chord_routes.py\n"
        "\n"
        "start-analyzer-internal-test: scripts/manage_analyzer_internal_test.py\n"
        "\tpython3 scripts/manage_analyzer_internal_test.py start\n"
        "\n"
        "status-analyzer-internal-test: scripts/manage_analyzer_internal_test.py\n"
        "\tpython3 scripts/manage_analyzer_internal_test.py status\n"
        "\n"
        "start-urmp-profile-replay: scripts/manage_urmp_profile_replay.py\n"
        "\tpython3 scripts/manage_urmp_profile_replay.py start\n"
        "\n"
        "status-urmp-profile-replay: scripts/manage_urmp_profile_replay.py\n"
        "\tpython3 scripts/manage_urmp_profile_replay.py status\n"
    )
    anchor = (
        ".PHONY: push-chord-stability\n"
        "push-chord-stability: scripts/manage_real_drum_improvement_commit.py\n"
        "\tpython3 scripts/manage_real_drum_improvement_commit.py push\n"
    )
    worktree = (ROOT / "Makefile").read_text(encoding="utf-8")
    if block not in worktree:
        raise SystemExit("missing temporal replay targets in Makefile")
    indexed = run("git", "show", ":Makefile", capture=True).stdout
    if block in indexed:
        return
    if anchor not in indexed:
        raise SystemExit("missing chord stability targets in indexed Makefile")
    updated = indexed.replace(anchor, anchor + "\n" + block, 1)
    object_id = run("git", "hash-object", "-w", "--stdin", capture=True, stdin_text=updated).stdout.strip()
    run("git", "update-index", "--add", "--cacheinfo", f"100644,{object_id},Makefile")


def apply() -> None:
    if not status().strip():
        raise SystemExit("no real-drum changes to stage")
    pre_staged = run("git", "diff", "--cached", "--name-only", capture=True).stdout
    pre_staged_paths = {line for line in pre_staged.splitlines() if line}
    allowed_pre_staged = {"scripts/manage_real_drum_improvement_commit.py"}
    if pre_staged_paths - allowed_pre_staged:
        raise SystemExit("refusing to commit pre-staged changes:\n" + pre_staged)
    run("git", "diff", "--check", "--", *PATHS)
    run("git", "add", "--", *STAGE_PATHS)
    stage_chord_temporal_makefile_target()
    stage_temporal_tools_makefile_targets()
    run("git", "commit", "-m", MESSAGE)


def push() -> None:
    upstream = run("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", capture=True).stdout.strip()
    if not upstream:
        raise SystemExit("current branch has no upstream")
    run("git", "fetch")
    try:
        run("git", "merge-base", "--is-ancestor", upstream, "HEAD")
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"{upstream} has commits not present in HEAD; rebase is required") from error
    run("git", "push")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply", "push"}:
        raise SystemExit("usage: manage_real_drum_improvement_commit.py plan|apply|push")
    {"plan": plan, "apply": apply, "push": push}[sys.argv[1]]()


if __name__ == "__main__":
    main()
