#!/usr/bin/env python3
"""Verify the optional BasicPitch mirror does not reduce MedleyDB vocal recall."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BINARY = REPO_ROOT / "build" / "basic_pitch_medleydb_context"
RUNTIME = REPO_ROOT / "build" / "onnxruntime-linux-x64-1.29.0" / "lib" / "libonnxruntime.so"
MODEL = REPO_ROOT / "build" / "basic_pitch" / "nmp.onnx"
ROOTS = (
    REPO_ROOT / "build" / "medleydb_vocal_mix_context_samples",
    REPO_ROOT / "build" / "medleydb_vocal_stem_context_samples",
)


def summary(output: str) -> tuple[int, int, int]:
    match = re.search(r"medleydb-basic-pitch-context native=(\d+)/(\d+) fused=(\d+)/\d+", output)
    if not match:
        raise RuntimeError("missing BasicPitch context summary")
    return tuple(int(value) for value in match.groups())


def temporal_rows(output: str) -> list[tuple[int, float]]:
    return [
        (int(frames), float(onset))
        for frames, onset in re.findall(r"temporal_frames=(\d+) temporal_max_onset=([0-9.]+)", output)
    ]


def main() -> int:
    for root in ROOTS:
        result = subprocess.run([str(BINARY), str(root), str(RUNTIME), str(MODEL)], text=True, capture_output=True)
        sys.stdout.write(result.stdout)
        if result.returncode:
            sys.stderr.write(result.stderr)
            raise RuntimeError(f"context runner failed for {root.name}: {result.returncode}")
        native, total, fused = summary(result.stdout)
        if total == 0 or fused < native:
            raise RuntimeError(f"BasicPitch mirror regressed {root.name}: native={native}/{total} fused={fused}/{total}")
        if root.name == "medleydb_vocal_stem_context_samples" and fused < 7:
            raise RuntimeError(f"high-confidence stem recovery missing: fused={fused}/{total}")
        temporal = temporal_rows(result.stdout)
        if len(temporal) != total or not any(frames > 1 and onset > 0.0 for frames, onset in temporal):
            raise RuntimeError(f"continuous temporal evidence missing for {root.name}")
        print(
            f"basic-pitch-medleydb-context root={root.name} native={native}/{total} fused={fused}/{total} "
            f"temporal-rows={len(temporal)}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"test_basic_pitch_medleydb_context: {error}", file=sys.stderr)
        raise SystemExit(1)
