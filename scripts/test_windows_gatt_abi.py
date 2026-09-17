#!/usr/bin/env python3
"""Check the local declarations used to call the Windows GATT API."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HEADER = REPO_ROOT / "src" / "windows_bluetooth_gatt.hpp"


def main() -> None:
    source = HEADER.read_text(encoding="utf-8")
    assert "typedef ULONG64 MAO_BTH_LE_GATT_RELIABLE_WRITE_CONTEXT;" in source
    assert "MAO_BTH_LE_GATT_RELIABLE_WRITE_CONTEXT, ULONG);" in source
    assert "constexpr ULONG kGattFlagWriteWithoutResponse = 0x00000020;" in source
    print("Windows GATT ABI declarations: PASS")


if __name__ == "__main__":
    main()
