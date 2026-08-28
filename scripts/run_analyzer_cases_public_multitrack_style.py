#!/usr/bin/env python3
"""Run the synthetic multitrack-style analyzer regression group."""

import os
import subprocess


def main() -> int:
    subprocess.run(["make", "build/analyzer_cases"], check=True)
    environment = os.environ.copy()
    environment["MUSIC_ANALYZER_CASE_GROUP"] = "public-multitrack-style"
    return subprocess.run(["build/analyzer_cases"], env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
