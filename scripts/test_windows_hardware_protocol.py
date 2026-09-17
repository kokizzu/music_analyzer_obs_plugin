#!/usr/bin/env python3
"""Check that the Windows hardware backend retains all native output paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    ROOT / "src" / "windows_hardware_control.cpp",
    ROOT / "src" / "windows_hardware_control.hpp",
    ROOT / "src" / "windows_bluetooth_gatt.hpp",
)

REQUIREMENTS = {
    "Akai MIDI discovery and output": (
        "windows_midi_output_name_matches",
        "akai",
        "mpc",
        "mpd",
        "pad",
        "midiOutGetNumDevs",
        "midiOutOpen",
        "midiOutShortMsg",
        "windows_midi_uses_pad_note_feedback",
        "midi_protocol",
        "build_mpc_pad_note_messages",
        "protocol=",
    ),
    "Fret Zealot BLE output": (
        "fret_zealot_name_matches",
        "BluetoothGATTSetCharacteristicValue",
        "kFretZealotService",
        "kFretZealotWriteCharacteristic",
        "kFretZealot2Service",
        "kFretZealot2WriteCharacteristic",
    ),
    "LiteJam BLE output": (
        "litejam_name_matches",
        "kLiteJamServiceShortUuid",
        "kLiteJamLedCharacteristicShortUuid",
        "kLiteJamService",
        "kLiteJamLedCharacteristic",
    ),
    "Reconnect output retry": (
        "const bool midi_present = midi.still_present",
        "midi_sent_revision != revision || !midi_present",
        "litejam_sent_revision != revision || !litejam_present",
        "fret_zealot_sent_revision != revision || !fret_zealot_present",
    ),
}


def main() -> int:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SOURCE_PATHS).lower()
    missing = {
        name: tuple(marker for marker in markers if marker.lower() not in source)
        for name, markers in REQUIREMENTS.items()
    }
    missing = {name: markers for name, markers in missing.items() if markers}
    if missing:
        for name, markers in missing.items():
            print(f"{name}: missing {', '.join(markers)}")
        return 1
    print("Windows hardware protocol contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
