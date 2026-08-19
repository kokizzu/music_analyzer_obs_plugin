#!/usr/bin/env python3
"""Regression checks for class-aware drum active-context auditing."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_drum_competing_active_contexts import Candidate, matches_row, replay  # noqa: E402
from evaluate_egmd_drum_recovery import DrumEvent  # noqa: E402
from audit_drum_competing_active_contexts import candidates_for  # noqa: E402


def event(expected: set[str], kick: float, hihat: float) -> DrumEvent:
    return DrumEvent("mix", 0, expected, set(), {
        "kick": {"active": float(kick > 0.30), "level": kick},
        "hihat": {"active": float(hihat > 0.30), "level": hihat},
    })


def main() -> int:
    events = [
        event({"kick"}, 0.90, 0.70),
        event({"kick"}, 0.80, 0.60),
        event({"hihat"}, 0.50, 0.90),
    ]
    candidates = candidates_for(events, "hihat", "kick")
    assert any(candidate.false_suppressed == 2 and candidate.true_suppressed == 0 for candidate in candidates)
    candidate = Candidate("hihat", "kick", "ratio", 1.20, 2, 0)
    assert matches_row({"hihat_level": "0.70", "kick_level": "0.90"}, candidate) is True
    assert matches_row({"hihat_level": "0.90", "kick_level": "0.70"}, candidate) is False
    assert matches_row({"hihat_level": "0.70"}, candidate) is None
    with tempfile.TemporaryDirectory() as temporary:
        protected = Path(temporary) / "protected.tsv"
        protected.write_text(
            "expected\tgot\tkick_level\thihat_level\n"
            "hihat\thihat\t0.20\t0.90\n"
            "hihat\thihat\t0.90\t0.70\n",
            encoding="utf-8",
        )
        result = replay(candidate, [protected])
    assert result.rows == 2
    assert result.primary_suppressed == 1
    assert result.correct_suppressed == 1
    assert result.unsupported == 0
    print("test_audit_drum_competing_active_contexts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
