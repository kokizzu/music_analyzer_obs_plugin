#!/usr/bin/env python3
"""Summarize Basic Pitch replay tests and Make targets without shell probing."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
TESTS = (
    ROOT / "tests/basic_pitch_vocal_fusion.cpp",
    ROOT / "tests/basic_pitch_onnx_musicnet.cpp",
    ROOT / "tests/basic_pitch_onnx_signal.cpp",
    ROOT / "tests/basic_pitch_onnx_decoder.cpp",
)


def print_make_targets() -> None:
    print("## Make targets")
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if "basic-pitch" in line.lower() and re.match(r"^[A-Za-z0-9_.-]+:", line):
            print(line)


def print_test_contract(path: Path) -> None:
    print(f"## {path.relative_to(ROOT)}")
    lines = path.read_text(encoding="utf-8").splitlines()
    selected: list[tuple[int, str]] = []
    for index, line in enumerate(lines, start=1):
        if ("TEST(" in line or "REQUIRE" in line or "CHECK(" in line or
                "EXPECT_" in line or "assert(" in line or
                "MusicNet" in line or "fusion" in line.lower()):
            selected.append((index, line.rstrip()))
    if not selected:
        print("no test assertions found")
        return
    for index, line in selected:
        print(f"{index:6d}: {line}")


def main() -> int:
    print_make_targets()
    for path in TESTS:
        print_test_contract(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
