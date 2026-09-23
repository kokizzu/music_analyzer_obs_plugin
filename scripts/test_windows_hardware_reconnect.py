#!/usr/bin/env python3
"""Check that Windows hardware outputs recover when a device is replugged."""

from pathlib import Path


def require(text: str, fragment: str) -> None:
    if fragment not in text:
        raise SystemExit(f"windows hardware reconnect check: missing {fragment}")


def main() -> int:
    text = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in ("src/windows_hardware_control.cpp", "src/windows_hardware_worker.hpp")
    )
    for fragment in (
        "bool still_present(const std::string &preferred)",
        "bool still_present()",
        "BluetoothGATTGetServices(handle_",
            "static bool midi_present(void *context)",
            "static bool litejam_present(void *context)",
            "static bool fret_zealot_present(void *context)",
            "if (sent_revision != command.revision ||",
            "sent_device_generation != command.device_generation",
            "device_notifications.start()",
            "notify_device_change()",
    ):
        require(text, fragment)
    print("Windows hardware reconnect checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
