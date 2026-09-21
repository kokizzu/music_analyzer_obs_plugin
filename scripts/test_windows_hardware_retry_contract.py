#!/usr/bin/env python3
"""Check the source-level guarantees of Windows hardware retry behavior."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")
FRET_SOURCE = Path("src/fret_control.cpp")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fret_source = FRET_SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        "constexpr auto kHardwareRetryInitialDelay = std::chrono::seconds(2);",
        "constexpr auto kHardwareRetryMaximumDelay = std::chrono::seconds(30);",
        "struct HardwareRetryState",
        "retry.force(now);",
        "retry.failed(HardwareClock::now());",
        'publish_hardware_status("midi", midi_connected, true);',
        'publish_hardware_status("litejam", litejam_connected, true);',
        'publish_hardware_status("fret-zealot", fret_zealot_connected, true);',
        'log_hardware_hresult("Fret Zealot", "write scale packet", result);',
        'log_hardware_hresult("LiteJam", "write scale packet", result);',
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise SystemExit("missing Windows hardware retry contract: " + "; ".join(missing))
    if "std::vector<uint8_t> packet = {0x40, 0x00, 0x00, 0x00};" not in fret_source:
        raise SystemExit("missing Fret Zealot clear packet prefix")
    if "const int fret_zealot_pixel = 5 - static_cast<int>(string);" not in fret_source:
        raise SystemExit("missing Fret Zealot high-E-to-low-E pixel mapping")

    for device in ("midi", "litejam", "fret-zealot"):
        if source.count(f'publish_hardware_status("{device}"') < 2:
            raise SystemExit(f"missing connected/disconnected status transitions for {device}")

    print("Windows hardware retry contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
