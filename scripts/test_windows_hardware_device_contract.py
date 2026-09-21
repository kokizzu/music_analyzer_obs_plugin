#!/usr/bin/env python3
"""Check Windows hardware pacing, retry, and reconnect identity contracts."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    required = (
        "constexpr DWORD kFretZealotLegacyWriteDelayMs = 20;",
        "constexpr DWORD kFretZealotModernWriteDelayMs = 1;",
        "constexpr DWORD kGattWriteRetryDelayMs = 50;",
        "constexpr int kGattWriteAttempts = 3;",
        "bool is_transient_gatt_error(HRESULT result)",
        "HRESULT write_gatt_with_retry(const char *device, Writer writer)",
        "write_delay_ms = kFretZealotModernWriteDelayMs;",
        "write_delay_ms_ = write_delay_ms;",
        "write_gatt_with_retry(\"Fret Zealot\"",
        "write_gatt_with_retry(\"LiteJam\"",
        "caps.wMid == manufacturer_id_",
        "caps.wPid == product_id_",
        "std::wstring last_path_;",
        "exact_path_only && path != last_path_",
    )
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise SystemExit("missing Windows hardware device contract: " + "; ".join(missing))
    print("Windows hardware device contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
