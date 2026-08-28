#!/usr/bin/env python3
"""Plan, stage, and commit the repository's source-only baseline safely."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "build" / "code_baseline_commit_plan.json"
MAX_FILE_SIZE = 2 * 1024 * 1024
ALLOWED_ROOTS = ("android/", "docs/", "scripts/", "src/", "tests/", "third_party/")
ALLOWED_FILES = {"Makefile", "README.md"}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def eligible(path: str) -> tuple[bool, str]:
    if path in ALLOWED_FILES or path.startswith(ALLOWED_ROOTS):
        full_path = ROOT / path
        if not full_path.is_file():
            return False, "not-a-regular-file"
        if full_path.stat().st_size > MAX_FILE_SIZE:
            return False, "over-2MiB-limit"
        return True, "source-file"
    return False, "outside-source-scope"


def create_plan() -> dict[str, object]:
    modified = git("diff", "--name-only").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    candidates = sorted(set(modified + untracked))
    included: list[str] = []
    excluded: list[dict[str, str]] = []
    for path in candidates:
        accepted, reason = eligible(path)
        if accepted:
            included.append(path)
        else:
            excluded.append({"path": path, "reason": reason})
    return {
        "max_file_size": MAX_FILE_SIZE,
        "included": included,
        "excluded": excluded,
    }


def write_plan(plan: dict[str, object]) -> None:
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")


def print_plan(plan: dict[str, object]) -> None:
    included = plan["included"]
    excluded = plan["excluded"]
    print(f"included={len(included)} source/config/doc/test files")
    for path in included:
        print(f"+ {path}")
    print(f"excluded={len(excluded)}")
    for item in excluded:
        print(f"- {item['path']} ({item['reason']})")


def stage(plan: dict[str, object]) -> None:
    included = plan["included"]
    if not included:
        raise RuntimeError("no eligible source files to stage")
    git("add", "--", *included)


def verify(plan: dict[str, object]) -> None:
    print(f"head={git('log', '-1', '--format=%h %s').strip()}")
    staged = git("diff", "--cached", "--name-only").splitlines()
    print(f"staged={len(staged)}")
    print(f"eligible_uncommitted={len(plan['included'])}")
    print(f"excluded_uncommitted={len(plan['excluded'])}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "stage", "commit", "verify", "push"))
    parser.add_argument(
        "--message", default="chore: checkpoint current analyzer implementation"
    )
    args = parser.parse_args()
    plan = create_plan()
    write_plan(plan)
    print_plan(plan)
    if args.mode == "plan":
        return 0
    if args.mode == "verify":
        verify(plan)
        return 0
    if args.mode == "push":
        if git("diff", "--cached", "--name-only").strip():
            raise RuntimeError("refusing to push with staged but uncommitted changes")
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
        return 0
    stage(plan)
    print("staged eligible source-only baseline")
    if args.mode == "commit":
        subprocess.run(["git", "commit", "-m", args.message], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"baseline commit error: {error}", file=sys.stderr)
        raise SystemExit(1)
