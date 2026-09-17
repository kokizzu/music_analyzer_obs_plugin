#!/usr/bin/env python3
"""Prevent BLE discovery from regressing to the wrong Windows interface GUID."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "src" / "windows_bluetooth_gatt.hpp"
CONTROL = ROOT / "src" / "windows_hardware_control.cpp"


def main() -> int:
    header = HEADER.read_text(encoding="utf-8")
    control = CONTROL.read_text(encoding="utf-8")
    expected = (
        "0x6e3bb679",
        "0x4372",
        "0x40c8",
        "0x9e, 0xaa, 0x45, 0x09, 0xdf, 0x26, 0x0c, 0xd8",
    )
    if "kBluetoothGattServiceInterface" not in header:
        print("missing GATT service interface symbol", file=sys.stderr)
        return 1
    if any(value not in header for value in expected):
        print("GATT service interface GUID does not match Windows", file=sys.stderr)
        return 1
    if "kBluetoothLeDeviceInterface" in header or "kBluetoothLeDeviceInterface" in control:
        print("generic LE device interface symbol remains in BLE discovery", file=sys.stderr)
        return 1
    uses = len(re.findall(r"kBluetoothGattServiceInterface", control))
    if uses < 2:
        print("BLE discovery does not use the GATT service interface for both enumeration calls", file=sys.stderr)
        return 1
    print("Windows GATT service interface: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
