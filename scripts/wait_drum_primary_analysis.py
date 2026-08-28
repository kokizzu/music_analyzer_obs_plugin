#!/usr/bin/env python3
"""Wait for the bounded drum primary-analysis workers to finish."""

from __future__ import annotations

from pathlib import Path
import time


TIMEOUT_SECONDS = 180.0


def active_workers() -> int:
    count = 0
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "analyzer_drum_samples" in command:
            count += 1
    return count


def main() -> int:
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while True:
        workers = active_workers()
        print(f"active_drum_primary_workers={workers}", flush=True)
        if workers == 0:
            return 0
        if time.monotonic() >= deadline:
            print("timeout waiting for drum primary analysis", flush=True)
            return 1
        time.sleep(1.0)


if __name__ == "__main__":
    raise SystemExit(main())
