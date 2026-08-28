#!/usr/bin/env python3
"""Summarize completed real-note full-mix shard outputs without replaying audio."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = sorted((ROOT / "build").glob("real_note_full_mix_shard_*.out"))
PATTERN = re.compile(r"drum-active-windows\s+(\d+)/(\d+)")


def main() -> None:
    matched = []
    for path in OUTPUTS:
        text = path.read_text(encoding="utf-8", errors="replace")
        result = PATTERN.search(text)
        if result:
            matched.append((path.name, int(result.group(1)), int(result.group(2))))
    active = sum(value for _, value, _ in matched)
    windows = sum(value for _, _, value in matched)
    percent = 100.0 * active / windows if windows else 0.0
    print(f"shards={len(matched)}/32 active={active}/{windows} percent={percent:.2f}")
    for name, value, total in matched:
        if value:
            print(f"{name} {value}/{total}")


if __name__ == "__main__":
    main()
