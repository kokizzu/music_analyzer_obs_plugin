#!/usr/bin/env python3
"""Find source-scoped two-feature drum suppression contexts on real mixes.

The candidate is allowed only on non-one-shot sources at runtime.  It therefore
requires no annotated target loss across every supplied real-mix corpus and
must suppress false targets in multiple recordings.  Results are diagnostic:
each candidate still needs an isolated runtime measurement before use.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from evaluate_egmd_drum_recovery import DrumEvent, active, read_events, value


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
FEATURES = (
    "level", "trigger_ratio", "band", "seg", "shape", "rms", "low", "mid", "high",
    "transient", "onset", "kick_body", "snare_body", "tom_body", "snare_crack",
    "upper_tom", "body_shape",
)


@dataclass(frozen=True)
class Predicate:
    feature: str
    operator: str
    threshold: float

    def matches(self, event: DrumEvent, category: str) -> bool:
        observed = value(event, category, self.feature)
        return observed <= self.threshold if self.operator == "<=" else observed >= self.threshold

    def text(self) -> str:
        return f"{self.feature}{self.operator}{self.threshold:.6g}"


@dataclass(frozen=True)
class Candidate:
    category: str
    first: Predicate
    second: Predicate
    false_suppressed: int
    recordings: int

    def text(self) -> str:
        return f"{self.category} when {self.first.text()} and {self.second.text()}"


def counts(events: list[DrumEvent], category: str, predicates: tuple[Predicate, ...]) -> tuple[int, int, int]:
    false_total = true_total = 0
    recordings: set[str] = set()
    for event in events:
        if not active(event, category) or not all(predicate.matches(event, category) for predicate in predicates):
            continue
        if category in event.expected:
            true_total += 1
        else:
            false_total += 1
            recordings.add(event.recording)
    return false_total, true_total, len(recordings)


def primitives(events: list[DrumEvent], category: str, min_false: int, per_direction: int) -> list[Predicate]:
    false_events = [event for event in events if active(event, category) and category not in event.expected]
    selected: list[tuple[int, int, Predicate]] = []
    for feature in FEATURES:
        values = sorted({value(event, category, feature) for event in false_events})
        for operator in ("<=", ">="):
            ranked: list[tuple[int, int, Predicate]] = []
            for threshold in values:
                predicate = Predicate(feature, operator, threshold)
                false_total, true_total, _ = counts(events, category, (predicate,))
                if false_total >= min_false:
                    ranked.append((true_total, -false_total, predicate))
            selected.extend(sorted(ranked, key=lambda item: (item[0], item[1], item[2].threshold))[:per_direction])
    return [item[2] for item in selected]


def find_candidates(events: list[DrumEvent], min_false: int, min_recordings: int, per_direction: int) -> list[Candidate]:
    result: list[Candidate] = []
    for category in CATEGORIES:
        seeds = primitives(events, category, min_false, per_direction)
        by_pair: dict[tuple[str, str], Candidate] = {}
        for first, second in combinations(seeds, 2):
            if first.feature == second.feature:
                continue
            first, second = sorted((first, second), key=lambda item: item.text())
            false_total, true_total, recordings = counts(events, category, (first, second))
            if false_total < min_false or true_total or recordings < min_recordings:
                continue
            candidate = Candidate(category, first, second, false_total, recordings)
            key = (first.feature, second.feature)
            previous = by_pair.get(key)
            if previous is None or (candidate.false_suppressed, candidate.recordings, candidate.text()) > (
                previous.false_suppressed, previous.recordings, previous.text()
            ):
                by_pair[key] = candidate
        result.extend(by_pair.values())
    return sorted(result, key=lambda item: (-item.false_suppressed, -item.recordings, item.text()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-input", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-false", type=int, default=2)
    parser.add_argument("--min-recordings", type=int, default=2)
    parser.add_argument("--per-direction", type=int, default=8)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--category", choices=CATEGORIES)
    args = parser.parse_args()
    events = read_events(args.real_input)
    candidates = find_candidates(events, args.min_false, args.min_recordings, args.per_direction)
    if args.category is not None:
        candidates = [candidate for candidate in candidates if candidate.category == args.category]
    lines = [
        "drum_source_scoped_context_audit: "
        f"events={len(events)} candidates={len(candidates)} min_false={args.min_false} "
        f"min_recordings={args.min_recordings}"
    ]
    for candidate in candidates[:args.limit]:
        lines.append(
            f"context {candidate.text()}: false_suppressed={candidate.false_suppressed} "
            f"recordings={candidate.recordings} true_suppressed=0"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
