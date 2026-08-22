#!/usr/bin/env python3
"""Regression checks for cross-real drum recovery candidate mining."""

from __future__ import annotations

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import find_egmd_drum_recovery_candidates as MODULE  # noqa: E402


def event(expected: set[str], active_snare: float, band: float) -> object:
    metrics = {"snare": {"active": active_snare, "band": band, "trigger": band, "threshold": 1.0}}
    for category in expected - {"snare"}:
        metrics[category] = {"active": 1.0}
    return MODULE.DrumEvent("fixture", 1, expected, set(), metrics)


def main() -> int:
    corpora = {"MDB": [event({"snare"}, 0.0, 8.0), event({"kick"}, 0.0, 2.0)], "STAR": [event({"snare"}, 0.0, 9.0), event({"hihat"}, 0.0, 3.0)]}
    misses, candidates = MODULE.find_candidates(corpora)
    assert misses == 2
    assert any(item.text() == "snare band>=8" and item.recovered == (("MDB", 1), ("STAR", 1)) for item in candidates)
    assert not any(item.feature in {"transient", "onset"} and item.operator == "<=" for item in candidates)
    blocked = {"MDB": [event({"snare"}, 0.0, 8.0), event({"kick"}, 0.0, 9.0)], "STAR": [event({"snare"}, 0.0, 9.0), event({"hihat"}, 0.0, 3.0)]}
    _, candidates = MODULE.find_candidates(blocked)
    assert not any(item.category == "snare" and item.feature == "band" and item.operator == ">=" for item in candidates)
    print("test_find_egmd_drum_recovery_candidates: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
