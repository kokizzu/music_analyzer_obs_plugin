#!/usr/bin/env python3
"""Check that the Windows audio diagnostic path remains wired end to end."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDALONE = (ROOT / "src" / "standalone.cpp").read_text(encoding="utf-8")
LOOPBACK = (ROOT / "src" / "windows_loopback.hpp").read_text(encoding="utf-8")
DOC = (ROOT / "docs" / "windows_standalone.md").read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


require(STANDALONE, 'arg == "--debug-audio"', "debug-audio option parsing")
require(STANDALONE, "options.debug_audio", "debug-audio option wiring")
require(STANDALONE, "maybe_log_diagnostics", "diagnostic polling")
require(LOOPBACK, "set_diagnostics", "diagnostic configuration")
require(LOOPBACK, "diagnostic_packets_", "packet accounting")
require(LOOPBACK, "diagnostic_silent_frames_", "silent-frame accounting")
require(LOOPBACK, "WASAPI audio diagnostics", "diagnostic output")
require(DOC, "--debug-audio", "Windows diagnostic documentation")

print("Windows audio diagnostic checks: ok")
