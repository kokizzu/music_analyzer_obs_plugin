#!/usr/bin/env python3
"""Run the Windows compiler/toolchain smoke checks used by CI."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    script = Path(__file__).with_name("test_windows_toolchains.py")
    result = subprocess.run([sys.executable, str(script)], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
