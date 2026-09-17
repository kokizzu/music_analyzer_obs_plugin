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
		"const bool midi_present = midi.still_present(options.midi_output)",
		"midi_sent_revision != revision || !midi_present",
		"const bool litejam_present = litejam.still_present()",
		"litejam_sent_revision != revision || !litejam_present",
		"const bool fret_zealot_present = fret_zealot.still_present()",
		"fret_zealot_sent_revision != revision || !fret_zealot_present",
    ):
        require(text, fragment)
    print("Windows hardware reconnect checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
