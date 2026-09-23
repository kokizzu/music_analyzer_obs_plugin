#!/usr/bin/env python3
from pathlib import Path


RANGES = (
    ("src/windows_hardware_control.cpp", 230, 380),
    ("src/windows_hardware_control.cpp", 760, 1080),
    ("src/windows_hardware_worker.hpp", 1, 180),
    ("src/windows_input_capture.hpp", 1, 160),
    ("src/capture_queue.hpp", 1, 180),
)


def report(path: str, start: int, end: int) -> None:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    print(f"=== {path}:{start}-{end} ===")
    for number in range(start, min(end, len(lines)) + 1):
        print(f"{number}: {lines[number - 1]}")


for path, start, end in RANGES:
    report(path, start, end)
