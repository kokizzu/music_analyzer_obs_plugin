#!/usr/bin/env python3
"""Show MDB frames that enter the strong-transient crash recovery path."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "mdb_drums_windows.log"
FLAG = 1 << 28
FLAGS = re.compile(r"flags=(0x[0-9a-fA-F]+)")


def main() -> int:
    matches = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        flag = FLAGS.search(line)
        if flag is not None and int(flag.group(1), 0) & FLAG:
            matches.append(line)
    print(f"strong_transient_crash_recovery_frames={len(matches)}")
    for line in matches:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
