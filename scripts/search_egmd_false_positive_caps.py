#!/usr/bin/env python3
"""Find simple cross-corpus caps for active E-GMD drum false positives.

This is deliberately a diagnostic, not a learned runtime classifier.  It
searches one-feature predicates over verbose all-window logs and only reports
rules that suppress false activations without suppressing an annotated event
in *any* supplied corpus.  Keeping the predicate simple makes a subsequent
runtime rule inspectable and avoids accepting an apparent gain from a
corpus-specific model.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from evaluate_egmd_drum_recovery import active, read_events, value


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
FEATURES = (
    "level",
    "trigger_ratio",
    "supported",
    "rms",
    "low",
    "mid",
    "high",
    "transient",
    "onset",
    "kick_body",
    "snare_body",
    "tom_body",
    "snare_crack",
    "upper_tom",
    "body_shape",
)


@dataclass(frozen=True)
class NamedEvent:
    corpus: str
    event: object


@dataclass(frozen=True)
class Candidate:
    category: str
    feature: str
    operator: str
    threshold: float
    false_suppressed: int
    true_suppressed: int
    corpus_false_suppressed: tuple[tuple[str, int], ...]

    def key(self) -> tuple[int, int, int, str, str, float]:
        # Prefer rules that help both corpora, then total false-positive gain,
        # then a deterministic compact textual ordering.
        covered_corpora = sum(1 for _, count in self.corpus_false_suppressed if count > 0)
        return (-covered_corpora, -self.false_suppressed, self.true_suppressed, self.category,
                self.feature, self.threshold)


def parse_input(value_text: str) -> tuple[str, Path]:
    try:
        name, raw_path = value_text.split("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("input must be NAME=PATH") from exc
    if not name or not raw_path:
        raise argparse.ArgumentTypeError("input must be NAME=PATH")
    return name, Path(raw_path)


def predicate_matches(event: object, category: str, feature: str, operator: str, threshold: float) -> bool:
    observed = value(event, category, feature)
    return observed <= threshold if operator == "<=" else observed >= threshold


def threshold_values(events: Iterable[NamedEvent], category: str, feature: str) -> list[float]:
    return sorted({value(item.event, category, feature) for item in events if active(item.event, category)})


def find_candidates(events: list[NamedEvent], minimum_false_suppressed: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    corpus_names = tuple(sorted({item.corpus for item in events}))
    for category in CATEGORIES:
        for feature in FEATURES:
            for operator in ("<=", ">="):
                for threshold in threshold_values(events, category, feature):
                    false_suppressed = 0
                    true_suppressed = 0
                    by_corpus = {name: 0 for name in corpus_names}
                    for item in events:
                        event = item.event
                        if not active(event, category) or not predicate_matches(
                            event, category, feature, operator, threshold
                        ):
                            continue
                        if category in event.expected:
                            true_suppressed += 1
                        else:
                            false_suppressed += 1
                            by_corpus[item.corpus] += 1
                    if true_suppressed or false_suppressed < minimum_false_suppressed:
                        continue
                    candidates.append(
                        Candidate(
                            category,
                            feature,
                            operator,
                            threshold,
                            false_suppressed,
                            true_suppressed,
                            tuple((name, by_corpus[name]) for name in corpus_names),
                        )
                    )
    return candidates


def non_dominated(candidates: list[Candidate]) -> list[Candidate]:
    """Keep the strongest predicate for each category/feature/direction."""
    selected: dict[tuple[str, str, str], Candidate] = {}
    for candidate in sorted(candidates, key=Candidate.key):
        selected.setdefault((candidate.category, candidate.feature, candidate.operator), candidate)
    return sorted(selected.values(), key=Candidate.key)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=parse_input, required=True)
    parser.add_argument("--minimum-false-suppressed", type=int, default=2)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    if args.minimum_false_suppressed < 1:
        parser.error("--minimum-false-suppressed must be positive")
    if args.limit < 1:
        parser.error("--limit must be positive")

    events: list[NamedEvent] = []
    for corpus, path in args.input:
        if not path.is_file():
            parser.error(f"missing input: {path}")
        events.extend(NamedEvent(corpus, event) for event in read_events([path]))
    candidates = non_dominated(find_candidates(events, args.minimum_false_suppressed))
    print(f"search_egmd_false_positive_caps: events={len(events)} candidates={len(candidates)}")
    for candidate in candidates[: args.limit]:
        per_corpus = " ".join(f"{name}:{count}" for name, count in candidate.corpus_false_suppressed)
        print(
            f"cap {candidate.category} when {candidate.feature} {candidate.operator} "
            f"{candidate.threshold:.6g}: false_suppressed={candidate.false_suppressed} "
            f"true_suppressed={candidate.true_suppressed} corpora={per_corpus}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
