#!/usr/bin/env python3
"""Regression check for DCS read-only candidate-evidence parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_dagstuhl_vocal_evidence.py"
SPEC = importlib.util.spec_from_file_location("inspect_dcs_evidence", SCRIPT)
assert SPEC and SPEC.loader
INSPECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECTOR)


def main() -> int:
    parsed = INSPECTOR.candidates(
        "60,vocal,0.800,0,0,0,0.800,0,0.900,0.700,1,0;"
        "64,keys,1.000,0,1.000,0,0,0,0.800,0.600,0,1"
    )
    assert sorted(parsed) == [60, 64]
    assert parsed[60][1] == "vocal"
    assert parsed[64][11] == "1"
    assert INSPECTOR.candidates("--") == {}
    print("test_inspect_dagstuhl_vocal_evidence: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
