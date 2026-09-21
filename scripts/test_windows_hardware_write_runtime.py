#!/usr/bin/env python3
"""Test stale hardware writes with a fake revision-changing backend."""

from pathlib import Path
import subprocess
import tempfile


def main() -> int:
    source = Path("tests/windows_hardware_write_runtime.cpp")
    with tempfile.TemporaryDirectory(prefix="mao-write-test-") as directory:
        binary = Path(directory) / "write-test"
        subprocess.run(
            ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I.", str(source), "-o", str(binary)],
            check=True,
        )
        subprocess.run([str(binary)], check=True)
    print("Windows hardware write runtime: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
