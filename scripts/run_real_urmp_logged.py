#!/usr/bin/env python3
"""Run the URMP real-audio gate and retain its complete output."""

from pathlib import Path
import subprocess
import sys


LOG = Path("build/test_analyzer_urmp.log")


def main() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", encoding="utf-8") as output:
        result = subprocess.run(
            ["make", "test-analyzer-urmp"],
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
        )
    print(f"test-analyzer-urmp exit={result.returncode} log={LOG}")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
