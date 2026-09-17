#!/usr/bin/env python3
"""Check that Windows hardware outputs recover when a device is replugged."""

from pathlib import Path


def require(text: str, fragment: str) -> None:
    if fragment not in text:
        raise SystemExit(f"windows hardware reconnect check: missing {fragment}")


def main() -> int:
    path = Path("src/windows_hardware_control.cpp")
    text = path.read_text(encoding="utf-8")
    for fragment in (
        "bool still_present(const std::string &preferred)",
        "bool still_present()",
        "BluetoothGATTGetServices(handle_",
        "midi_sent_revision != revision || !midi.still_present(options.midi_output)",
        "litejam_sent_revision != revision || !litejam.still_present()",
        "fret_zealot_sent_revision != revision || !fret_zealot.still_present()",
    ):
        require(text, fragment)
    print("Windows hardware reconnect checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
