#!/usr/bin/env python3
"""Summarize completed real-drum shard outputs without starting another test run."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
PATTERNS = (
    "hf_drum_kit_samples_shard_*.out",
    "idmt_drums_samples_shard_*.out",
    "mdb_drums_samples_shard_*.out",
    "star_drums_samples_shard_*.out",
    "drum_samples_test_shard_*.out",
    "drum_samples_spread_test_shard_*.out",
)


def main() -> None:
    for pattern in PATTERNS:
        files = sorted(BUILD.glob(pattern))
        if not files:
            print(f"{pattern}: pending")
            continue
        summaries = []
        for path in files:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            summary = next((line for line in reversed(lines) if "checks" in line or "recall" in line), "running")
            summaries.append(f"{path.name}: {summary}")
        print(f"{pattern}: {len(files)} shard(s)")
        for summary in summaries:
            print(f"  {summary}")


if __name__ == "__main__":
    main()
