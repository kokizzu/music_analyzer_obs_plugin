#!/usr/bin/env python3
"""Commit Windows GATT protocol changes without staging unrelated work."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "src/windows_bluetooth_gatt.hpp",
    "scripts/test_windows_gatt_abi.py",
    "windows.mk",
    "scripts/commit_windows_protocol.py",
)


def run(arguments: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=REPO_ROOT, check=check, text=True)


def plan() -> None:
    run(["git", "status", "--short", "--", *FILES])
    run(["git", "diff", "--stat", "--", *FILES])
    print("scoped Windows protocol paths:")
    for path in FILES:
        print(f"  {path}")


def apply() -> None:
    run(["git", "add", "--", *FILES])
    run(["git", "commit", "-m", "windows: align GATT ABI declarations"])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        raise SystemExit("usage: commit_windows_protocol.py plan|apply")
    {"plan": plan, "apply": apply}[sys.argv[1]]()
