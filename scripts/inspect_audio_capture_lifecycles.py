#!/usr/bin/env python3
"""Print the native live-audio capture paths for platform lifecycle review."""

from pathlib import Path


def print_file(path: Path, ranges: tuple[tuple[int, int], ...] | None = None) -> None:
    print(f"[{path}]")
    lines = path.read_text(encoding="utf-8").splitlines()
    selected = ranges or ((1, len(lines)),)
    for start, end in selected:
        for number in range(start, min(end, len(lines)) + 1):
            print(f"{number:4}: {lines[number - 1]}")


def main() -> int:
    print_file(Path("src/windows_loopback.hpp"))
    print_file(Path("android/app/src/main/cpp/android_bridge.cpp"), ((275, 430),))
    print_file(Path("android/app/src/main/java/dev/benalu/musicanalyzer/MainActivity.java"),
               ((1, 260), (650, 755)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
