#!/usr/bin/env python3
"""Compare the indexed and working Fret Zealot legacy-frame settle setting."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def matching_lines(label: str, content: str) -> None:
    print(label)
    for line_no, line in enumerate(content.splitlines(), 1):
        if "LEGACY_FRAME_SETTLE_MILLIS" in line or "legacy" in line.lower() and "settle" in line.lower():
            print(f"{line_no}: {line}")


def main() -> int:
    indexed = subprocess.run(
        ["git", "show", f":{PATH}"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    working = (ROOT / PATH).read_text(encoding="utf-8")
    matching_lines("index", indexed)
    matching_lines("working tree", working)
    diff = subprocess.run(
        ["git", "diff", "--unified=3", "--", PATH],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    print("diff")
    print(diff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
