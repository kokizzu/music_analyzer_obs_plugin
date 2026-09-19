#!/usr/bin/env python3
"""Show status and diff statistics for the Windows hardware change set."""

import subprocess


FILES = (
    "src/windows_hardware_control.cpp",
    "scripts/deploy_windows_self_signed.py",
    "scripts/report_fret_zealot_sdk.py",
    "scripts/report_windows_hardware_source.py",
    "scripts/report_windows_source_range.py",
    "scripts/report_windows_deploy_source.py",
    "scripts/test_windows_hardware_retry_contract.py",
    "windows.mk",
)


def run_git(*arguments: str) -> None:
    result = subprocess.run(["git", *arguments, "--", *FILES], check=False, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def print_diff(path: str) -> None:
    print(f"=== diff {path} ===")
    result = subprocess.run(["git", "diff", "--", path], check=False, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    print("=== status ===")
    run_git("status", "--short")
    print("=== unstaged stat ===")
    run_git("diff", "--stat")
    print("=== staged stat ===")
    run_git("diff", "--cached", "--stat")
    print_diff("windows.mk")
    print_diff("scripts/deploy_windows_self_signed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
