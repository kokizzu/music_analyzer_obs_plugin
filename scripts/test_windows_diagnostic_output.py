#!/usr/bin/env python3
"""Ensure Windows hardware enumeration output reaches the diagnostic log."""

from pathlib import Path
import sys


SOURCE = Path(__file__).resolve().parents[1] / "src" / "standalone.cpp"
HARDWARE_SOURCE = Path(__file__).resolve().parents[1] / "src" / "windows_hardware_control.cpp"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    hardware_source = HARDWARE_SOURCE.read_text(encoding="utf-8")
    if 'freopen_s(&stream, log_path.c_str(), "a", stderr)' not in source:
        print("Windows diagnostic logger does not redirect stderr", file=sys.stderr)
        return 1
    expected_messages = (
        "No Windows MIDI output devices",
        "No paired LiteJam BLE interfaces",
        "No paired Fret Zealot BLE interfaces",
        "MIDI %u\\t%s\\n",
        "LiteJam\\t%s\\n",
        "Fret Zealot\\t%s\\n",
    )
    for message in expected_messages:
        if message not in hardware_source:
            print(f"hardware diagnostic message is missing: {message}", file=sys.stderr)
            return 1
    if (
        'std::printf("MIDI ' in hardware_source
        or 'std::printf("LiteJam' in hardware_source
        or 'std::printf("Fret Zealot' in hardware_source
        or 'std::puts("No ' in hardware_source
    ):
        print("hardware enumeration still writes only to stdout", file=sys.stderr)
        return 1
    if "Windows hardware probe:" not in source:
        print("Windows hardware probe diagnostics are missing", file=sys.stderr)
        return 1
    print("Windows diagnostic output: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
