#!/usr/bin/env python3
"""Print the bounded Fret Zealot LED queue implementation for review."""

from pathlib import Path


SOURCE = Path("android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java")
TEST_SOURCE = Path("tests/check_fret_zealot_auto_root_guard.py")
ANDROID_TEST_SOURCE = Path("tests/check_android_project.py")
MARKERS = (
    "activeScaleFrameCursor",
    "activeScaleFramePhase",
    "queuedScaleFrame",
    "send",
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    printed: set[int] = set()
    for marker in MARKERS:
        matches = [
            index for index, line in enumerate(lines)
            if index >= 100 and marker.lower() in line.lower()
        ]
        for index in matches[:4]:
            start = max(0, index - 10)
            end = min(len(lines), index + 48)
            fresh = [line_number for line_number in range(start, end) if line_number not in printed]
            if not fresh:
                continue
            print(f"\n--- {SOURCE}:{index + 1} marker={marker} ---")
            for line_number in fresh:
                print(f"{line_number + 1:5}: {lines[line_number]}")
                printed.add(line_number)

    print(f"\n--- {TEST_SOURCE} ---")
    for line_number, line in enumerate(TEST_SOURCE.read_text(encoding="utf-8").splitlines(), start=1):
        if "assert" in line or "FretZealot" in line or "flush" in line.lower():
            print(f"{line_number:5}: {line}")

    print(f"\n--- {ANDROID_TEST_SOURCE}:380-440 ---")
    android_test_lines = ANDROID_TEST_SOURCE.read_text(encoding="utf-8").splitlines()
    for line_number in range(379, min(440, len(android_test_lines))):
        print(f"{line_number + 1:5}: {android_test_lines[line_number]}")


if __name__ == "__main__":
    main()
