#!/usr/bin/env python3
"""Print the Fret Zealot scale update paths for a focused regression review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java": (
        "dimChannel",
        "sendPacket",
        "onScaleFrameFlushed",
        "finishScaleFrame",
        "queueOrStartScaleFrame",
        "startScaleFrame",
        "writeScaleFrameDelta",
        "setPixel",
        "samePixel",
    ),
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java": (
        "refreshOutputs",
        "refreshFretZealotOutput",
    ),
    ROOT / "tests/check_android_project.py": (),
}


def print_method(lines: list[str], method: str) -> None:
    marker = method + "("
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if marker in line
            and (" void " in line or " boolean " in line or " byte " in line)
            and "{" in line
        ),
        None,
    )
    if start is None:
        print(f"missing method: {method}")
        return
    depth = 0
    opened = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{")
        if "{" in line:
            opened = True
        print(f"{index + 1:4}: {line}")
        depth -= line.count("}")
        if opened and depth == 0:
            return


def main() -> None:
    for path, methods in FILES.items():
        lines = path.read_text(encoding="utf-8").splitlines()
        print(f"== {path.relative_to(ROOT)} ==")
        if not methods:
            for index in range(330, min(432, len(lines))):
                print(f"{index + 1:4}: {lines[index]}")
            print()
            continue
        for method in methods:
            print_method(lines, method)
            print()


if __name__ == "__main__":
    main()
