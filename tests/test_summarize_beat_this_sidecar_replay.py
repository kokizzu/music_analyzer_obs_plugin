#!/usr/bin/env python3
"""Tests for strict Beat This! sidecar replay aggregation."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_beat_this_sidecar_replay.py"
SPEC = importlib.util.spec_from_file_location("summarize_beat_this_sidecar_replay", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def row(identifier: int, status: str) -> str:
    return (
        "Beat This sidecar replay"
        f"\tid={identifier}\texpected=120.00\traw=0.00\tintervals=0"
        "\tpacket_seconds=20\twall_seconds=0.500\tmodel=final0\terror=0.00"
        f"\tstatus={status}\n"
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        first, second = root / "first.log", root / "second.log"
        first.write_text(row(1, "hit") + row(2, "withheld"), encoding="utf-8")
        second.write_text(row(3, "miss") + row(4, "unavailable"), encoding="utf-8")
        rendered = MODULE.render([first, second])
    assert rendered == (
        "beat_this_sidecar_replay: rows=4 ready=2 correct=1 wrong=1 withheld=1 unavailable=1 max_wall_seconds=0.500\n"
    )
    print("test_summarize_beat_this_sidecar_replay: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
