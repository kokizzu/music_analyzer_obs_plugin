#!/usr/bin/env python3
"""Report whether the optional Beat This! diagnostic can run locally.

It intentionally performs no installation or model download.  The output is
used to choose a reproducible, isolated inference environment rather than
adding Python packages to OBS or to the system interpreter.
"""
from __future__ import annotations

import importlib.util
import platform
import sys


def main() -> int:
    print(f"Beat This environment\tpython={sys.version.split()[0]}\tplatform={platform.platform()}")
    for module in ("torch", "beat_this", "einops", "soxr", "rotary_embedding_torch"):
        print(f"Beat This environment\tmodule={module}\tavailable={int(importlib.util.find_spec(module) is not None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
