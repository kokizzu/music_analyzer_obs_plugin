#!/usr/bin/env python3
"""Show the leading diagnostic rows from each MDB drum analyzer shard."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    for shard in range(4):
        path = Path(f"build/mdb_drums_samples_shard_{shard}.out")
        print(f"[{path}]")
        if not path.exists():
            print("missing")
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:35]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
