#!/usr/bin/env python3
"""Regression checks for source-scoped real-mix drum-context search."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_drum_source_scoped_contexts import find_candidates  # noqa: E402
from evaluate_egmd_drum_recovery import DrumEvent  # noqa: E402


def event(recording: str, expected: set[str], hihat: float, low: float, high: float) -> DrumEvent:
    return DrumEvent(recording, 0, expected, set(), {
        "hihat": {
            "active": float(hihat > 0.30), "level": hihat, "low": low, "high": high,
            "trigger_ratio": 2.0, "band": 1.0, "seg": 1.0, "shape": 1.0, "rms": 0.2,
            "mid": 0.1, "transient": 1.2, "onset": 3.0, "kick_body": 20.0,
            "snare_body": 20.0, "tom_body": 20.0, "snare_crack": 2.0,
            "upper_tom": 2.0, "body_shape": 0.0,
        },
    })


def main() -> int:
    events = [
        event("a", {"kick"}, 0.80, 0.80, 0.04),
        event("b", {"snare"}, 0.85, 0.82, 0.05),
        event("c", {"hihat"}, 0.90, 0.20, 0.30),
    ]
    candidates = find_candidates(events, min_false=2, min_recordings=2, per_direction=4)
    assert any(candidate.category == "hihat" and candidate.false_suppressed == 2 for candidate in candidates)
    print("test_audit_drum_source_scoped_contexts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
