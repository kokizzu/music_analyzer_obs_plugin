#!/usr/bin/env python3
"""Report current analyzer-cases runner processes."""

from pathlib import Path
from time import clock_gettime, CLOCK_BOOTTIME


def main() -> None:
    found = False
    for proc in sorted(Path("/proc").iterdir(), key=lambda item: item.name):
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            ).strip()
        except OSError:
            continue
        if "analyzer_cases" not in command:
            continue
        found = True
        stat = (proc / "stat").read_text(encoding="utf-8", errors="replace").split()
        state = stat[2]
        ticks = int(stat[13]) + int(stat[14])
        elapsed = max(0.0, clock_gettime(CLOCK_BOOTTIME) - int(stat[21]) / 100.0)
        print(f"{proc.name}: state={state} cpu_ticks={ticks} elapsed={elapsed:.1f}s {command}")
    if not found:
        print("No analyzer-case process is running.")


if __name__ == "__main__":
    main()
