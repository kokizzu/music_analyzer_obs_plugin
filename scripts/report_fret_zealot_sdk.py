#!/usr/bin/env python3
"""Print the small part of the Android SDK that defines Fret Zealot reset commands."""

from pathlib import Path


SOURCE = Path("android/fz-android-sdk/src/main/java/com/fz/blelib/LEDBLELib.java")
TOKENS = (
    "COMMAND_SET_ALL",
    "LOWEST_SDK_INTENSITY",
    "addBuffer",
    "sendCommandBufferClear",
    "sendCommandFlush",
    "set_all",
    "sendCommand",
)
CONTEXT = 18


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    ranges: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not any(token in line for token in TOKENS):
            continue
        start = max(0, index - CONTEXT)
        end = min(len(lines), index + CONTEXT + 1)
        if ranges and start <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
        else:
            ranges.append((start, end))

    print(f"source: {SOURCE}")
    print(f"matches: {sum(any(token in line for token in TOKENS) for line in lines)}")
    for start, end in ranges:
        print(f"--- lines {start + 1}-{end} ---")
        for number in range(start, end):
            print(f"{number + 1:4}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
