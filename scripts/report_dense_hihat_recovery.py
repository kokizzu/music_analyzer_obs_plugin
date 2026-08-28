#!/usr/bin/env python3
"""Report full-mix rows admitted by the dense hi-hat recovery diagnostic flag."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FLAG = 1 << 30
LOGS = (
    ROOT / "build/mdb_dense_hihat_recovery.out",
    ROOT / "build/mdb_dense_hihat_recovery.log",
    ROOT / "build/mdb_drums_misses.log",
    ROOT / "build/star_drums_misses.log",
)
FLAG_PATTERN = re.compile(r"flags=0x([0-9a-fA-F]+)")


def main() -> None:
    for path in LOGS:
        print(f"## {path.relative_to(ROOT)}")
        if not path.exists():
            print("missing")
            continue
        matched = 0
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            flag = FLAG_PATTERN.search(line)
            if flag is None or int(flag.group(1), 16) & FLAG == 0:
                continue
            matched += 1
            print(line)
        print(f"matched={matched}")


if __name__ == "__main__":
    main()
