#!/usr/bin/env python3
"""Print Windows audio lifecycle and endpoint-recovery code."""

from pathlib import Path


SOURCES = (
    Path("src/windows_loopback.cpp"),
    Path("src/windows_loopback.hpp"),
    Path("src/windows_input_capture.cpp"),
    Path("src/windows_input_capture.hpp"),
)
TOKENS = (
    "AUDCLNT",
    "IMMDevice",
    "GetDefaultAudioEndpoint",
    "Initialize",
    "capture",
    "device",
    "reconnect",
    "invalid",
)
CONTEXT = 5


def main() -> int:
    for source in SOURCES:
        if not source.is_file():
            continue
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        if source.name == "windows_input_capture.hpp":
            print(f"=== {source} ===")
            for number, line in enumerate(lines, 1):
                print(f"{number}: {line}")
            continue
        emitted: set[int] = set()
        for index, line in enumerate(lines):
            if not any(token.lower() in line.lower() for token in TOKENS):
                continue
            emitted.update(range(max(0, index - CONTEXT), min(len(lines), index + CONTEXT + 1)))
        print(f"=== {source} ===")
        for number in sorted(emitted):
            print(f"{number + 1}: {lines[number]}")
    print("=== endpoint_changed call sites ===")
    for source in sorted(Path("src").rglob("*.cpp")):
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            if "endpoint_changed" in line:
                print(f"{source}:{number}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
