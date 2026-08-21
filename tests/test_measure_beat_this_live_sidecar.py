#!/usr/bin/env python3
"""Checks for the model-free Beat This sidecar replay helpers."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "measure_beat_this_live_sidecar.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("measure_beat_this_live_sidecar", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def main() -> int:
    assert MODULE.trailing_window_bounds(5_000, 100, 10.0) == (1_000, 3_000)
    try:
        MODULE.trailing_window_bounds(1_999, 100, 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("short audio must not be zero-padded")
    payload = MODULE.packet(np.zeros(160_000, dtype=np.float32), 8_000)
    magic, rate, count = MODULE.HEADER.unpack(payload[:MODULE.HEADER.size])
    assert magic == MODULE.MAGIC and rate == 8_000 and count == 160_000
    ready = MODULE.parse_reply(json.dumps({"protocol": MODULE.PROTOCOL, "status": "ready", "bpm": 150.0, "intervals": 44, "sample_rate": 8_000, "samples": 160_000}), 8_000)
    assert ready["bpm"] == 150.0
    try:
        MODULE.parse_reply('{"protocol":"mao-beat-this-v1","status":"gated","bpm":1.0,"intervals":0,"sample_rate":8000,"samples":160000}', 8_000)
    except ValueError:
        pass
    else:
        raise AssertionError("gated replies must not leak a BPM")
    print("test_measure_beat_this_live_sidecar: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
