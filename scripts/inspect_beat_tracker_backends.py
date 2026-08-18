#!/usr/bin/env python3
"""Report locally available optional beat-tracking development back ends."""

from __future__ import annotations

import shutil
import subprocess


def pkg_config_exists(package: str) -> bool:
    if shutil.which("pkg-config") is None:
        return False
    return subprocess.run(["pkg-config", "--exists", package], check=False).returncode == 0


def main() -> int:
    for package in ("aubio", "essentia"):
        print(f"beat_tracker_backend package={package} available={pkg_config_exists(package)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
