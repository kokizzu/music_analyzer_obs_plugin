#!/usr/bin/env python3
"""Unit checks for the conservative real-mix false-positive cap search."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evaluate_egmd_drum_recovery import DrumEvent  # noqa: E402
from search_egmd_false_positive_caps import NamedEvent, find_candidates  # noqa: E402


def event(expected: set[str], kick_mid: float) -> DrumEvent:
    return DrumEvent(
        recording="fixture",
        sample=1,
        expected=expected,
        missing=set(),
        metrics={"kick": {"active": 1.0, "mid": kick_mid}},
    )


class SearchFalsePositiveCapsTests(unittest.TestCase):
    def test_reports_cross_corpus_cap_without_true_suppression(self) -> None:
        candidates = find_candidates(
            [
                NamedEvent("MDB", event({"snare"}, 0.50)),
                NamedEvent("STAR", event({"hihat"}, 0.55)),
                NamedEvent("MDB", event({"kick"}, 0.20)),
            ],
            minimum_false_suppressed=2,
        )
        self.assertTrue(
            any(
                candidate.category == "kick"
                and candidate.feature == "mid"
                and candidate.operator == ">="
                and candidate.false_suppressed == 2
                and candidate.true_suppressed == 0
                for candidate in candidates
            )
        )

    def test_rejects_cap_that_would_suppress_an_annotated_event(self) -> None:
        candidates = find_candidates(
            [
                NamedEvent("MDB", event({"snare"}, 0.50)),
                NamedEvent("STAR", event({"hihat"}, 0.55)),
                NamedEvent("STAR", event({"kick"}, 0.60)),
            ],
            minimum_false_suppressed=2,
        )
        self.assertFalse(
            any(
                candidate.category == "kick"
                and candidate.feature == "mid"
                and candidate.operator == ">="
                and candidate.threshold <= 0.55
                for candidate in candidates
            )
        )


if __name__ == "__main__":
    unittest.main()
