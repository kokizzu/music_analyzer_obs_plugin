#!/usr/bin/env python3
"""Report active VocalSet replay/download processes for safe test polling."""

import subprocess


def main() -> int:
    result = subprocess.run(
        ["ps", "-eo", "pid=,stat=,args="], text=True, capture_output=True, check=False
    )
    for line in result.stdout.splitlines():
        if "vocalset" in line.lower() or "VocalSet.zip" in line:
            print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
