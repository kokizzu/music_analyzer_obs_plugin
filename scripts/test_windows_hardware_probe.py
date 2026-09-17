#!/usr/bin/env python3
"""Static checks for the Windows hardware-only verification command."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/standalone.cpp").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Windows hardware probe check failed: {message}")


require('arg == "--hardware-only"' in SOURCE,
        "standalone must expose a hardware-only command-line mode")
require("if (options.hardware_test_root < 0)" in SOURCE and "if (options.hardware_only)" in SOURCE,
        "hardware-only mode must require an explicit test root")
require("hardware.start()" in SOURCE and "hardware.update(options.hardware_test_root" in SOURCE,
        "hardware-only mode must start the shared controller and send the requested root")
require("std::this_thread::sleep_for" in SOURCE and "hardware.stop()" in SOURCE,
        "hardware-only mode must allow asynchronous BLE writes to settle and stop cleanly")
require("--hardware-only" in SOURCE,
        "hardware-only mode must be documented in the standalone usage text")

print("Windows hardware probe checks: ok")
