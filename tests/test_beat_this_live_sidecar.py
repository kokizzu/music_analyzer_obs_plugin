#!/usr/bin/env python3
"""Unit tests for the disabled-by-default Beat This live sidecar protocol."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "beat_this_live_sidecar.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("beat_this_live_sidecar", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def packet(sample_rate: int, sample_count: int | None = None) -> bytes:
    count = sample_count if sample_count is not None else MODULE.expected_samples(sample_rate)
    return MODULE.HEADER.pack(MODULE.MAGIC, sample_rate, count) + (b"\0" * count * MODULE.SAMPLE_BYTES)


def main() -> int:
    sample_rate = 8_000
    count = MODULE.expected_samples(sample_rate)
    assert count == 160_000
    decoded = MODULE.read_packet(io.BytesIO(packet(sample_rate)))
    assert decoded is not None and decoded[0] == sample_rate and len(decoded[1]) == count * 4
    assert MODULE.read_packet(io.BytesIO()) is None

    try:
        MODULE.read_packet(io.BytesIO(packet(sample_rate, count - 1)))
    except ValueError as error:
        assert "exactly" in str(error)
    else:
        raise AssertionError("short window must be rejected")
    try:
        MODULE.read_packet(io.BytesIO(b"x" * MODULE.HEADER.size))
    except ValueError as error:
        assert "magic" in str(error)
    else:
        raise AssertionError("wrong protocol magic must be rejected")
    try:
        MODULE.cached_checkpoint(Path("/external/cache"), "../final0")
    except ValueError as error:
        assert "simple cached" in str(error)
    else:
        raise AssertionError("non-cache checkpoint path must be rejected")

    beats = [index * 0.4 for index in range(45)]
    ready = MODULE.gated_response(beats, sample_rate, count)
    assert ready["status"] == "ready" and ready["intervals"] == 44 and ready["bpm"] == 150.0
    gated = MODULE.gated_response([index * 0.5 for index in range(41)], sample_rate, count)
    assert gated["status"] == "gated" and gated["bpm"] == 0.0 and gated["intervals"] == 40

    output = io.BytesIO()
    assert MODULE.serve(io.BytesIO(packet(sample_rate)), output, lambda _samples, _rate: beats) == 0
    replay = json.loads(output.getvalue().decode("ascii"))
    assert replay == ready
    print("test_beat_this_live_sidecar: 10 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
