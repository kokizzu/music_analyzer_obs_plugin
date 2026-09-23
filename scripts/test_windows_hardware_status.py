#!/usr/bin/env python3
"""Check the physical Windows probe contract without requiring Windows hardware."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, markers: tuple[str, ...]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{path}: missing " + ", ".join(missing))


def main() -> int:
    require(
        "src/windows_hardware_control.hpp",
        (
            "struct WindowsHardwareStatus",
            "WindowsHardwareStatus status() const",
            "WindowsHardwareDeviceStatus midi",
        ),
    )
    require(
        "src/windows_hardware_status.hpp",
        (
            "enum class WindowsHardwareStatusReason",
            "WindowsHardwareDeviceStatus",
            "WindowsHardwareStatusChange",
            "WindowsHardwareStatusState",
            "record(bool new_connected",
            "snapshot() const",
            "transitions",
            "failures",
        ),
    )
    require(
        "src/windows_hardware_control.cpp",
        (
        'run_hardware_worker(worker_state, midi_backend(), "midi", midi_status',
        'run_hardware_worker(worker_state, litejam_backend(), "litejam", litejam_status',
        'run_hardware_worker(worker_state, fret_zealot_backend(), "fret-zealot", fret_zealot_status',
        '"output-failed"',
        '"worker-exception"',
            "WindowsHardwareController::status() const",
        ),
    )
    require(
        "src/standalone.cpp",
        (
            "--require-midi",
            "--require-litejam",
            "--require-fret-zealot",
            "Windows hardware probe: midi=%s litejam=%s fret-zealot=%s",
            "required device was not connected",
        ),
    )
    print("Windows hardware status contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
