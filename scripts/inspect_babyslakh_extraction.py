#!/usr/bin/env python3
"""Report whether the dedicated BabySlakh extraction service is still active."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.destination.is_dir():
        print("state=extracted")
        return 0
    service = subprocess.run(
        ["systemctl", "--user", "is-active", "--quiet", "music-analyzer-babyslakh-extract.service"],
        check=False,
    )
    print("state=extracting" if service.returncode == 0 else "state=not_started")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
