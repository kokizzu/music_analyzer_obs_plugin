#!/usr/bin/env python3
"""Run the retry state against a fake clock without Windows hardware."""

from pathlib import Path
import subprocess
import tempfile


def main() -> int:
    source = Path("tests/windows_hardware_retry_runtime.cpp")
    with tempfile.TemporaryDirectory(prefix="mao-retry-test-") as directory:
        binary = Path(directory) / "retry-test"
        subprocess.run(
            ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I.", str(source), "-o", str(binary)],
            check=True,
        )
        subprocess.run([str(binary)], check=True)
    print("Windows hardware retry runtime: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
