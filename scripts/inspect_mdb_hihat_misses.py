#!/usr/bin/env python3
"""Print verbose MDB hi-hat miss rows for feature-level inspection."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    path = Path("build/mdb_drums_misses.log")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    matches = [line for line in lines if "hihat" in line.lower() and "miss" in line.lower()]
    print(f"mdb_hihat_misses={len(matches)}")
    for line in matches[:60]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
