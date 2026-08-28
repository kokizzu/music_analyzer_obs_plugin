#!/usr/bin/env python3
"""Wait for all detached real-world sample regression workers to complete."""

from pathlib import Path
import os
import time


MATCHES = (
    "analyzer_real_note_samples",
    "analyzer_drum_samples",
    "analyzer_hf_drum",
    "analyzer_gaps_guitar",
    "analyzer_guitar",
    "analyzer_instrument_samples",
)


def active_workers() -> list[str]:
    workers: list[str] = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit() or process.name == str(os.getpid()):
            continue
        try:
            command = (process / "cmdline").read_bytes().replace(b"\0", b" ").decode()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue
        if any(marker in command for marker in MATCHES):
            workers.append(process.name)
    return workers


def main() -> None:
    print("Waiting for real-world sample workers.", flush=True)
    while True:
        workers = active_workers()
        if not workers:
            print("Real-world sample workers completed.", flush=True)
            return
        print(f"Real-world sample workers active={len(workers)}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
"""Wait for the parallel real-world sample gate to complete."""

from pathlib import Path
import time


NEEDLE = "real_world_samples_parallel"


def running() -> bool:
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if NEEDLE in (entry / "cmdline").read_bytes().decode("utf-8", "replace"):
                return True
        except OSError:
            continue
    return False


def main() -> int:
    print("Waiting for real-world sample gate.")
    while running():
        time.sleep(2)
    print("Real-world sample gate completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
