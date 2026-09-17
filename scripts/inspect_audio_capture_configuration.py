#!/usr/bin/env python3
"""Print the source sections that define the native audio capture formats."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def print_range(path: Path, start: int, end: int) -> None:
    print(f"[{path.relative_to(ROOT)}:{start}-{end}]")
    lines = path.read_text(encoding="utf-8").splitlines()
    for number in range(start, min(end, len(lines)) + 1):
        print(f"{number:4}: {lines[number - 1]}")


def print_matches(path: Path, needles: tuple[str, ...], radius: int = 28) -> None:
    print(f"[{path.relative_to(ROOT)}:matches]")
    lines = path.read_text(encoding="utf-8").splitlines()
    printed: set[int] = set()
    for needle in needles:
        for index, line in enumerate(lines):
            if needle not in line:
                continue
            start = max(0, index - radius)
            end = min(len(lines), index + radius + 1)
            for line_index in range(start, end):
                if line_index in printed:
                    continue
                printed.add(line_index)
                print(f"{line_index + 1:4}: {lines[line_index]}")


print_matches(ROOT / "src/standalone.cpp", (
    "build_live_audio_sources",
    "open_live_capture_device",
    "initial_live_audio_source_index",
))
print_range(ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/MainActivity.java", 300, 650)
print_range(ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/MainActivity.java", 650, 810)
print_range(ROOT / "src/windows_loopback.hpp", 46, 126)
