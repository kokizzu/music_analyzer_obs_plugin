#!/usr/bin/env python3
"""Report Fret Zealot scale-refresh code paths for regression diagnosis."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java",
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
)
METHODS = (
    "refreshFretZealotOutput",
    "sendStableFretZealotPacket",
    "retryFretZealotAutoReconciliation",
    "sendPacket",
    "queueOrStartScaleFrame",
    "startScaleFrame",
    "flushNextScaleFrameBatch",
    "onScaleFrameFlushed",
    "finishScaleFrameBatch",
    "scheduleScaleFrameBatchFallback",
    "finishScaleFrame",
    "scheduleScaleFrameSettle",
    "completeScaleFrame",
    "clearScaleFrames",
    "queueOrStartScaleFrame",
    "disconnect",
    "close",
    "onDisconnected",
)


def print_method(path: Path, method: str) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    declaration = re.compile(
        r"^\s*(?:(?:public|private|protected)\s+)?(?:static\s+)?[\w<>\[\]]+\s+"
        + re.escape(method)
        + r"\s*\("
    )
    start = next((index for index, line in enumerate(lines) if declaration.search(line)), None)
    if start is None:
        return False
    depth = 0
    opened = False
    end = start
    for end in range(start, len(lines)):
        depth += lines[end].count("{")
        if "{" in lines[end]:
            opened = True
        depth -= lines[end].count("}")
        if opened and depth == 0:
            break
    print(f"\n--- {path.relative_to(ROOT)}:{start + 1} {method}")
    for index in range(start, end + 1):
        print(f"{index + 1:4}: {lines[index]}")
    return True


def main() -> None:
    found = 0
    for path in SOURCES:
        if not path.exists():
            raise SystemExit(f"missing Fret Zealot source: {path.relative_to(ROOT)}")
        print(f"=== {path.relative_to(ROOT)}")
        if path.name == "ExternalDeviceManager.java":
            lines = path.read_text(encoding="utf-8").splitlines()
            print(f"\n--- {path.relative_to(ROOT)}:1 state")
            for index in range(min(240, len(lines))):
                print(f"{index + 1:4}: {lines[index]}")
        for method in METHODS:
            found += int(print_method(path, method))
    if not found:
        raise SystemExit("no expected Fret Zealot methods found")
    result = subprocess.run(
        [
            "git", "diff", "--",
            "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java",
            "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
            "Makefile",
            "tests/check_fret_zealot_auto_root_stability.py",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    print("\n=== relevant working-tree diff")
    print(result.stdout or "(no tracked changes)")


if __name__ == "__main__":
    main()
