#!/usr/bin/env python3
"""Check that Windows hardware outputs remain independently scheduled."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")
WORKER_SOURCE = Path("src/windows_hardware_worker.hpp")
NOTIFICATION_SOURCE = Path("src/windows_device_notifications.hpp")


def main() -> int:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in (SOURCE, WORKER_SOURCE, NOTIFICATION_SOURCE)
    )
    required = (
        "midi_worker = std::thread(&Impl::run_midi_guarded, this)",
        "litejam_worker = std::thread(&Impl::run_litejam_guarded, this)",
        "fret_zealot_worker = std::thread(&Impl::run_fret_zealot_guarded, this)",
        "void run_midi_guarded()",
        "void run_litejam_guarded()",
        "void run_fret_zealot_guarded()",
        "catch (...) {",
        "midiOutReset(handle)",
        "template <typename ShouldContinue>",
        "hardware_write_if_current(should_continue",
        "if (!should_continue())",
        "worker_state.update(",
        "run_hardware_worker(worker_state,",
        "worker_state.current(",
        "worker_state.request_stop()",
        "HardwareWorkerLifecycleState",
        "lifecycle_state.begin_start()",
        "lifecycle_state.begin_stop()",
        "sent_device_generation",
        "device_notifications.start()",
        "RegisterDeviceNotificationW(",
        "if (!state.current(command.revision))",
        "const bool write_succeeded =",
        "std::thread midi_worker;",
        "std::thread litejam_worker;",
        "std::thread fret_zealot_worker;",
    )
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise SystemExit("missing independent hardware worker contract: " + "; ".join(missing))
    if source.count("HardwareRetryState retry;") != 1:
        raise SystemExit("expected one shared retry loop for all hardware workers")
    print("Windows hardware worker contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
