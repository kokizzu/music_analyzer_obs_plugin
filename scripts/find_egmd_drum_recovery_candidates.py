#!/usr/bin/env python3
"""Find conservative cross-real drum recovery candidates from annotated logs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from evaluate_egmd_drum_recovery import DrumEvent, active, read_events, value


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
FEATURES = ("trigger_ratio", "band", "seg", "shape", "level", "low", "mid", "high", "rms", "transient", "onset", "kick_body", "snare_body", "tom_body", "snare_crack", "upper_tom", "body_shape")
# A recovery must be supported by an event, never by a settled/no-event frame.
# In particular, `onset <= threshold` rediscovered the obsolete unconditional
# HiHat recovery and would hold an idle OBS input active.  Both envelope-ratio
# features may only contribute positive event-strength lower bounds.
FEATURE_OPERATORS = {
    "transient": (">=",),
    "onset": (">=",),
}


def feature_value(event: DrumEvent, category: str, feature: str) -> float:
    if feature == "trigger_ratio":
        return value(event, category, "trigger") / max(value(event, category, "threshold"), 1.0e-6)
    return value(event, category, feature)


@dataclass(frozen=True)
class Candidate:
    category: str
    feature: str
    operator: str
    threshold: float
    recovered: tuple[tuple[str, int], ...]

    def matches(self, event: DrumEvent) -> bool:
        observed = feature_value(event, self.category, self.feature)
        return observed >= self.threshold if self.operator == ">=" else observed <= self.threshold

    @property
    def total_recovered(self) -> int:
        return sum(count for _, count in self.recovered)

    def text(self) -> str:
        return f"{self.category} {self.feature}{self.operator}{self.threshold:.6g}"


def candidate_counts(candidate: Candidate, corpora: dict[str, list[DrumEvent]]) -> tuple[bool, tuple[tuple[str, int], ...]]:
    recovered: list[tuple[str, int]] = []
    for corpus, events in sorted(corpora.items()):
        gained = sum(candidate.category in event.expected and not active(event, candidate.category) and candidate.matches(event) for event in events)
        false = sum(candidate.category not in event.expected and candidate.matches(event) for event in events)
        if gained == 0 or false:
            return False, ()
        recovered.append((corpus, gained))
    return True, tuple(recovered)


def find_candidates(corpora: dict[str, list[DrumEvent]]) -> tuple[int, list[Candidate]]:
    misses = sum(category in event.expected and not active(event, category) for events in corpora.values() for event in events for category in CATEGORIES)
    found: list[Candidate] = []
    for category in CATEGORIES:
        missed = [event for events in corpora.values() for event in events if category in event.expected and not active(event, category)]
        for feature in FEATURES:
            for operator in FEATURE_OPERATORS.get(feature, (">=", "<=")):
                for threshold in sorted({feature_value(event, category, feature) for event in missed}):
                    safe, recovered = candidate_counts(Candidate(category, feature, operator, threshold, ()), corpora)
                    if safe:
                        found.append(Candidate(category, feature, operator, threshold, recovered))
    chosen: dict[tuple[str, str, str], Candidate] = {}
    for candidate in sorted(found, key=lambda item: (-item.total_recovered, item.text())):
        chosen.setdefault((candidate.category, candidate.feature, candidate.operator), candidate)
    return misses, sorted(chosen.values(), key=lambda item: (-item.total_recovered, item.text()))


def parse_input(raw: str) -> tuple[str, Path]:
    try:
        name, path = raw.split("=", 1)
    except ValueError as error:
        raise ValueError("--real-input must be NAME=PATH") from error
    return name, Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-input", action="append", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    corpora = {name: read_events([path]) for name, path in map(parse_input, args.real_input)}
    if len(corpora) < 2:
        parser.error("at least two independent real inputs are required")
    misses, candidates = find_candidates(corpora)
    lines = [f"drum_recovery_candidate_audit: corpora={len(corpora)} missed_events={misses} cross_real_zero_false_candidates={len(candidates)}"]
    for candidate in candidates:
        recovered = " ".join(f"{name}:{count}" for name, count in candidate.recovered)
        lines.append(f"candidate {candidate.text()}: recovered={candidate.total_recovered} corpora={recovered} false=0 runtime_trial_required=1")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
