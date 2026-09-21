#!/usr/bin/env python3
"""Check that Windows hardware outputs remain independently scheduled."""

from pathlib import Path


SOURCE = Path("src/windows_hardware_control.cpp")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
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
        "condition.notify_all()",
        "bool wait_for_state(",
        "bool revision_is_current(",
        "if (!revision_is_current(revision))",
        "const bool write_succeeded =",
        "std::thread midi_worker;",
        "std::thread litejam_worker;",
        "std::thread fret_zealot_worker;",
    )
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise SystemExit("missing independent hardware worker contract: " + "; ".join(missing))
    if source.count("HardwareRetryState retry;") != 3:
        raise SystemExit("expected one retry state per hardware worker")
    print("Windows hardware worker contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
