#!/usr/bin/env python3
"""Run the broad analyzer-case suite and retain its complete output."""

from pathlib import Path
from subprocess import run


LOG = Path("build/analyzer_cases.log")


def main() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", encoding="utf-8") as output:
        result = run(["make", "test-analyzer-cases"], stdout=output, stderr=output, text=True)
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-40:]:
        print(line)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
