#!/usr/bin/env python3
"""Wait for running IDMT analyzer shards, without starting or stopping them."""

from pathlib import Path
from time import monotonic, sleep


TIMEOUT_SECONDS = 300.0


def running() -> list[tuple[int, str]]:
    matches = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            ).strip()
        except OSError:
            continue
        lowered = command.lower()
        if "analyzer_drum_samples" in lowered and "idmt_drums_samples" in lowered:
            matches.append((int(proc.name), command))
    return matches


def main() -> None:
    deadline = monotonic() + TIMEOUT_SECONDS
    while monotonic() < deadline:
        matches = running()
        if not matches:
            print("IDMT drum analyzer shards completed.")
            return
        print(f"Waiting for {len(matches)} IDMT drum analyzer shard process(es).")
        sleep(10)
    raise SystemExit("Timed out waiting for IDMT drum analyzer shards after 300 seconds.")


if __name__ == "__main__":
    main()
