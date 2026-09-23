#!/usr/bin/env python3
"""Check the source-level guarantees of Windows hardware retry behavior."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")
RETRY_SOURCE = Path("src/windows_hardware_retry.hpp")
WORKER_SOURCE = Path("src/windows_hardware_worker.hpp")
FRET_SOURCE = Path("src/fret_control.cpp")


def main() -> int:
    source = (SOURCE.read_text(encoding="utf-8") + "\n" +
              RETRY_SOURCE.read_text(encoding="utf-8") + "\n" +
              WORKER_SOURCE.read_text(encoding="utf-8"))
    fret_source = FRET_SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        "static constexpr duration initial_delay{2};",
        "static constexpr duration maximum_delay{30};",
        "class HardwareRetryState",
        "retry.force(now);",
        "retry.failed(HardwareRetryState::clock::now());",
    'run_hardware_worker(worker_state, midi_backend(), "midi", midi_status,',
    'run_hardware_worker(worker_state, litejam_backend(), "litejam", litejam_status,',
    'run_hardware_worker(worker_state, fret_zealot_backend(), "fret-zealot", fret_zealot_status,',
        'log_hardware_hresult("Fret Zealot", "write scale packet", result);',
        'log_hardware_hresult("LiteJam", "write scale packet", result);',
        'publish(device, status, false, "device-missing");',
        'publish(device, status, true, "output-sent");',
        'publish(device, status, false, "output-failed");',
        'publish(device, status, false, "worker-stopped");',
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise SystemExit("missing Windows hardware retry contract: " + "; ".join(missing))
    if "std::vector<uint8_t> packet = {0x40, 0x00, 0x00, 0x00};" not in fret_source:
        raise SystemExit("missing Fret Zealot clear packet prefix")
    if "const int fret_zealot_pixel = 5 - static_cast<int>(string);" not in fret_source:
        raise SystemExit("missing Fret Zealot high-E-to-low-E pixel mapping")

    print("Windows hardware retry contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
