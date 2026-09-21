#!/usr/bin/env python3
"""Show the complete local diff for the Windows audio recovery files."""

import subprocess


FILES = ("src/windows_loopback.hpp", "src/windows_input_capture.hpp")


def main() -> int:
    for path in FILES:
        print(f"=== diff {path} ===")
        result = subprocess.run(["git", "diff", "--", path], check=False, text=True)
        if result.returncode != 0:
            return result.returncode
    print("=== untracked input capture source ===")
    result = subprocess.run(["git", "status", "--short", "--", FILES[1]], check=False, text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
