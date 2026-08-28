#!/usr/bin/env python3
"""Wait briefly, then report whether the VocalSet replay remains active."""

import subprocess
import time


def main() -> int:
    time.sleep(30)
    result = subprocess.run(
        ["ps", "-eo", "pid=,stat=,args="], text=True, capture_output=True, check=False
    )
    matches = [
        line for line in result.stdout.splitlines()
        if "vocalset" in line.lower() or "VocalSet.zip" in line
    ]
    print("active" if matches else "inactive")
    for line in matches:
        print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
