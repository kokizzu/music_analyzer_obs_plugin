#!/usr/bin/env python3
"""Smoke-test the Windows signing command without touching release files."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    env = dict(os.environ)
    for name in (
        "WINDOWS_SIGN_PFX",
        "WINDOWS_SIGN_CERT",
        "WINDOWS_SIGN_PASSWORD",
        "WINDOWS_SIGN_TIMESTAMP_URL",
        "WINDOWS_SIGN_TOOL",
    ):
        env.pop(name, None)
    result = subprocess.run(
        ["python3", "scripts/sign_windows_standalone.py", "plan"],
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    required = (
        "executables:",
        "certificate: (unset; no files will be changed)",
        "timestamp URL: (unset)",
    )
    missing = [marker for marker in required if marker not in result.stdout]
    if missing:
        raise SystemExit("missing signing plan markers: " + ", ".join(missing))
    print("Windows signing plan: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
