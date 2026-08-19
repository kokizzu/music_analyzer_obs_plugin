#!/usr/bin/env python3
"""Report whether the optional Beat This! diagnostic can run locally.

It intentionally performs no installation or model download.  The output is
used to choose a reproducible, isolated inference environment rather than
adding Python packages to OBS or to the system interpreter.
"""
from __future__ import annotations

import importlib.util
import argparse
import platform
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-cache-root", type=Path)
    parser.add_argument("--diagnostic-log", type=Path)
    args = parser.parse_args()
    print(f"Beat This environment\tpython={sys.version.split()[0]}\tplatform={platform.platform()}")
    for module in ("torch", "beat_this", "einops", "soxr", "rotary_embedding_torch"):
        print(f"Beat This environment\tmodule={module}\tavailable={int(importlib.util.find_spec(module) is not None)}")
    if args.model_cache_root is not None:
        checkpoints = args.model_cache_root / "cache" / "hub" / "checkpoints"
        print(f"Beat This environment\tcheckpoint_dir={checkpoints}\texists={int(checkpoints.is_dir())}")
    if args.diagnostic_log is not None:
        rows = 0
        if args.diagnostic_log.is_file():
            rows = sum(
                line.startswith("Beat This tempo diag\t")
                for line in args.diagnostic_log.read_text(encoding="utf-8", errors="replace").splitlines()
            )
        print(f"Beat This environment\tdiagnostic_log={args.diagnostic_log}\trows={rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
