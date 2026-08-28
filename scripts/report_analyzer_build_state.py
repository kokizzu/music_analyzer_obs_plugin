#!/usr/bin/env python3
"""Report active analyzer compilation processes before dependent replays run."""

import subprocess


def main() -> int:
    result = subprocess.run(
        ["ps", "-eo", "pid=,stat=,args="], text=True, capture_output=True, check=False
    )
    for line in result.stdout.splitlines():
        if "src/analyzer.cpp" in line or "build/analyzer_test.o" in line:
            print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
