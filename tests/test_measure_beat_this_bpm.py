#!/usr/bin/env python3
"""Unit tests for Beat This BPM aggregation without its optional runtime."""
from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_beat_this_bpm.py"
SPEC = importlib.util.spec_from_file_location("measure_beat_this_bpm", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    bpm, intervals = MODULE.tempo_from_beats([0.0, 0.5, 1.0, 1.5, 2.0], 0.25, 1.5)
    assert abs(bpm - 120.0) < 1e-6 and intervals == 2
    bpm, intervals = MODULE.tempo_from_beats([0.0, 1.0], 2.0, 1.0)
    assert bpm == 0.0 and intervals == 0
    try:
        MODULE.tempo_from_beats([0.0], 0.0, 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero duration must fail")
    print("test_measure_beat_this_bpm: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
