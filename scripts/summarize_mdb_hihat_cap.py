#!/usr/bin/env python3
"""Summarize MDB verbose frames marked by the final weak-hi-hat cap."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "mdb_drums_windows.log"
WEAK_HIHAT_CAP = 1 << 27
FLAGS = re.compile(r"(?:flags|rule_flags)=((?:0x)?[0-9a-fA-F]+)")


def parse_flags(line: str) -> int:
    match = FLAGS.search(line)
    if match is None:
        return 0
    return int(match.group(1), 0)


def main() -> int:
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    marked = [line for line in lines if parse_flags(line) & WEAK_HIHAT_CAP]
    hihat = [line for line in marked if "HiHat" in line or "hihat" in line.lower()]
    print(f"weak_hihat_cap_frames={len(marked)}")
    print(f"weak_hihat_cap_hihat_named_frames={len(hihat)}")
    if not marked:
        print("== log format sample ==")
        for line in lines[:20]:
            print(line)
    for line in marked[:80]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
