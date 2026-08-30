#!/usr/bin/env python3
"""Ensure the BasicPitch Vocal mirror stays off on real sustained piano controls."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / "basic_pitch_medleydb_context"
CONTROL_ROOT = ROOT / "build" / "iowa_piano_temporal_controls"
RUNTIME = ROOT / "build" / "onnxruntime-linux-x64-1.29.0" / "lib" / "libonnxruntime.so"
MODEL = ROOT / "build" / "basic_pitch" / "nmp.onnx"


def main() -> int:
    result = subprocess.run([str(BINARY), str(CONTROL_ROOT), str(RUNTIME), str(MODEL)], text=True, capture_output=True)
    sys.stdout.write(result.stdout)
    if result.returncode:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"context runner failed: {result.returncode}")
    rows = re.findall(r"expected_midi=\d+ native_hit=(\d+) fused_hit=(\d+)", result.stdout)
    if len(rows) != 6:
        raise RuntimeError(f"expected six piano controls, got {len(rows)}")
    if any(native != "0" or fused != "0" for native, fused in rows):
        raise RuntimeError("piano control activated the Vocal row")
    print("iowa-piano-temporal-controls vocal-hits=0/6")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"test_iowa_piano_temporal_controls: {error}", file=sys.stderr)
        raise SystemExit(1)
