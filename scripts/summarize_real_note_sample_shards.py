#!/usr/bin/env python3
"""Summarize the latest persisted real-note sample shard results."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in sorted((ROOT / "build").glob("real_note_*_shard_*.out")):
        prefix, _, _ = path.name.rpartition("_shard_")
        grouped[prefix].append(path)

    for prefix, paths in grouped.items():
        latest = max(paths, key=lambda path: path.stat().st_mtime)
        lines = latest.read_text(encoding="utf-8", errors="replace").splitlines()
        nonempty = [line for line in lines if line.strip()]
        checks = 0
        usable = 0
        for path in paths:
            content = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r": (\d+) checks passed \(usable (\d+),", content)
            if match:
                checks += int(match.group(1))
                usable += int(match.group(2))
        if checks:
            print(f"{prefix}: {checks} checks passed; usable {usable}")
            continue
        tail = nonempty[-1] if nonempty else "(empty)"
        print(f"{prefix}: {len(paths)} shards; latest {latest.name}: {tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
