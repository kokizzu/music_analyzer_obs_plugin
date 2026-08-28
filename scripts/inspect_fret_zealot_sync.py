#!/usr/bin/env python3
"""Print the Fret Zealot control and LED-update paths with source locations."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
MANAGER = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java"
CONTROLLER = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def print_function(path: Path, signature: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if signature in line)
    depth = 0
    opened = False
    for index in range(start, len(lines)):
        depth += lines[index].count("{")
        opened = opened or "{" in lines[index]
        depth -= lines[index].count("}")
        if opened and depth == 0:
            print(f"## {path.relative_to(ROOT)}:{start + 1}-{index + 1}")
            for line_index in range(start, index + 1):
                print(f"{line_index + 1:6}: {lines[line_index]}")
            return
    raise RuntimeError(f"Unterminated function {signature}")


def main() -> int:
    print_function(MANAGER, "private void refreshOutputs")
    print_function(MANAGER, "private void refreshFretZealotOutput")
    lines = CONTROLLER.read_text(encoding="utf-8").splitlines()
    print(f"## {CONTROLLER.relative_to(ROOT)}")
    for index, line in enumerate(lines):
        print(f"{index + 1:6}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
