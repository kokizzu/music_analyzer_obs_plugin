#!/usr/bin/env python3
"""Summarize recorded high-fidelity ride primary misses for targeted analysis."""

from pathlib import Path


def main() -> None:
    for suffix in ("out", "err"):
        path = Path(f"build/hf_drum_kit_samples_shard_ride.{suffix}")
        print(f"== {path} ==")
        if not path.exists():
            print("missing")
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-80:]:
            print(line)


if __name__ == "__main__":
    main()
