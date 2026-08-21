#!/usr/bin/env python3
"""Regression coverage for the MDB class-specific Rim audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "inspect_mdb_rim_coverage.py"
SPEC = importlib.util.spec_from_file_location("inspect_mdb_rim_coverage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    sample = "\n".join(
        (
            "E-GMD window SongA sample 1 expected kick,rim: levels BASS DRUM=0.80* RIM=0.00 "
            "BASS DRUM band=1.00 seg=1.00 shape=1.00 trig=2.00/1.00 supported=1 level=0.80* | "
            "RIM band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | "
            "rms=0.10 energy=0.80/0.10/0.10 transient=1.00 onset=1.00 body=1.00/1.00/1.00 "
            "crack=1.00 upperTom=1.00 bodyShape=0",
            "E-GMD window SongB sample 2 expected rim: levels RIM=0.50* "
            "RIM band=1.00 seg=1.00 shape=1.00 trig=2.00/1.00 supported=1 level=0.50* | "
            "rms=0.10 energy=0.10/0.10/0.80 transient=1.00 onset=1.00 body=1.00/1.00/1.00 "
            "crack=1.00 upperTom=1.00 bodyShape=0",
        )
    )
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "mdb.log"
        path.write_text(sample + "\n", encoding="utf-8")
        assert MODULE.summarize(path) == (1, 2)
    print("test_inspect_mdb_rim_coverage: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
