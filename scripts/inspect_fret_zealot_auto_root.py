#!/usr/bin/env python3
"""Print the Fret Zealot auto-root and packet-dispatch implementation."""

from pathlib import Path


SOURCE_ROOT = Path("android/app/src/main/java/dev/benalu/musicanalyzer")
TERMS = (
    "sendPacket",
    "refreshFretZealotOutput",
    "lastFretZealotPacket",
    "complete",
    "pending",
    "queue",
    "clear",
    "write",
)


def main() -> None:
    for source in sorted(SOURCE_ROOT.glob("*FretZealot*.java")):
        print(f"== {source} ==")
        print(source.read_text(encoding="utf-8"))
    source = SOURCE_ROOT / "ExternalDeviceManager.java"
    lines = source.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "refreshFretZealotOutput" not in line:
            continue
        start = max(0, index - 2)
        end = min(len(lines), index + 32)
        print(f"== {source}:{index + 1} ==")
        for line_index in range(start, end):
            print(f"{line_index + 1:5}: {lines[line_index]}")
    test_source = Path("tests/check_android_project.py")
    print(f"== {test_source} Fret Zealot assertions ==")
    for index, line in enumerate(test_source.read_text(encoding="utf-8").splitlines(), 1):
        if ("FretZealot" in line or "fretZealot" in line or "automatic root" in line.lower()
                or "stale" in line.lower() or "reconciliation" in line.lower()):
            print(f"{index:5}: {line}")
    test_lines = test_source.read_text(encoding="utf-8").splitlines()
    print(f"== {test_source}:320-430 ==")
    for index in range(319, min(430, len(test_lines))):
        print(f"{index + 1:5}: {test_lines[index]}")


if __name__ == "__main__":
    main()
