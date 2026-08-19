#!/usr/bin/env python3
"""Unit checks for bounded Beat This rolling-window slicing."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_beat_this_rolling_bpm.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("measure_beat_this_rolling_bpm", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    assert MODULE.rolling_window_bounds(3000, 100, 10.0, 20.0, 20.0) == (1000, 3000, 0.0, 20.0)
    assert MODULE.rolling_window_bounds(3000, 100, 3.0, 20.0, 20.0) == (300, 2300, 0.0, 20.0)
    assert MODULE.rolling_window_bounds(5000, 100, 30.0, 20.0, 25.0) == (2500, 5000, 5.0, 20.0)
    try:
        MODULE.rolling_window_bounds(3000, 100, 10.0, 20.0, 10.0)
    except ValueError:
        pass
    else:
        raise AssertionError("a window smaller than the stable span must fail")
    print("test_measure_beat_this_rolling_bpm: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
