#!/usr/bin/env python3
"""Wait for the current analyzer-cases process without starting another suite."""

from pathlib import Path
from time import monotonic, sleep


def is_running() -> bool:
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            )
        except OSError:
            continue
        if "build/analyzer_cases" in command:
            return True
    return False


def main() -> None:
    deadline = monotonic() + 180.0
    while monotonic() < deadline:
        if not is_running():
            print("Analyzer-case process completed.")
            return
        print("Waiting for analyzer-case process.")
        sleep(10)
    raise SystemExit("Timed out waiting for analyzer-case process after 180 seconds.")


if __name__ == "__main__":
    main()
