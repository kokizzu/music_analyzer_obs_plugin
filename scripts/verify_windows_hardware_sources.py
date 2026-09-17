#!/usr/bin/env python3
"""Verify that the Windows hardware-control sources are complete enough to build."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "src/windows_hardware_control.hpp": (
        "class WindowsHardwareController",
        "WindowsHardwareOptions",
    ),
    "src/windows_bluetooth_gatt.hpp": (
        "BluetoothGATTGetServices",
        "kFretZealotService",
    ),
    "src/windows_hardware_control.cpp": (
        "WindowsHardwareController::Impl",
        "midiOutGetNumDevs",
        "BluetoothGATTSetCharacteristicValue",
    ),
}


def main() -> int:
    failed = False
    for relative, needles in EXPECTED.items():
        path = ROOT / relative
        if not path.is_file():
            print(f"MISSING {relative}")
            failed = True
            continue

        text = path.read_text(encoding="utf-8")
        print(f"OK {relative} lines={len(text.splitlines())} bytes={len(text.encode('utf-8'))}")
        for needle in needles:
            if needle not in text:
                print(f"  MISSING required text: {needle}")
                if relative.endswith("windows_bluetooth_gatt.hpp"):
                    for line_number, line in enumerate(text.splitlines(), 1):
                        if "uuid" in line.lower() or "fret" in line.lower():
                            print(f"  {line_number}: {line}")
                failed = True

        if relative.endswith(".cpp") and not text.rstrip().endswith("#endif"):
            print("  MISSING final platform guard")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
