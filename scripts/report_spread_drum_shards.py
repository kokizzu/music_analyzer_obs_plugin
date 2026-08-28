#!/usr/bin/env python3
"""Report the most recent spread drum shard summaries."""

from pathlib import Path


def main() -> None:
    for category in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim"):
        path = Path(f"build/drum_samples_spread_test_shard_{category}.out")
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
        summary = next((line for line in reversed(lines) if "analyzer_drum_samples:" in line), "pending")
        print(f"{category}: {summary}")


if __name__ == "__main__":
    main()
