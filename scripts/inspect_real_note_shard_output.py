#!/usr/bin/env python3
"""Print one persisted shard output to document its result format."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    candidates = sorted((ROOT / "build").glob("real_note_isolated_shard_*.out"))
    if not candidates:
        print("no isolated real-note shard output found")
        return 1
    path = candidates[0]
    print(path.relative_to(ROOT))
    print(path.read_text(encoding="utf-8", errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
