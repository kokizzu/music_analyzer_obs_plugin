#!/usr/bin/env python3
"""Audit two-feature real-mix drum false-positive suppression contexts.

This is intentionally a bounded diagnostic.  Each context is a conjunction of
two observable detector features for one active drum category.  It must remove
at least one false window in *each* supplied real-mix corpus, remove no
annotated event there, and then survive a protected one-shot primary replay.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from evaluate_egmd_drum_recovery import DrumEvent, active, read_events, value
from search_egmd_false_positive_caps import CATEGORIES, NamedEvent


# Every feature below is available in the protected attribute rows.  Deliberately
# omit ``rms``, ``supported``, ``transient``, and ``onset``: the latter two are
# logged for real mixes but not exported by every one-shot probe.
FEATURES = (
    "level", "trigger_ratio", "band", "seg", "shape", "low", "mid", "high",
    "kick_body", "snare_body", "tom_body", "snare_crack",
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
class Context:
    category: str
    first: Predicate
    second: Predicate
    false_suppressed: int
    corpus_false_suppressed: tuple[tuple[str, int], ...]

    def matches(self, event: DrumEvent) -> bool:
        return active(event, self.category) and self.first.matches(event, self.category) and self.second.matches(event, self.category)

    def text(self) -> str:
        return f"{self.category} {self.first.text()} & {self.second.text()}"


@dataclass(frozen=True)
class ProtectedResult:
    rows: int
    primary_suppressed: int
    correct_suppressed: int
    unsupported: int


def canonical_pair(first: Predicate, second: Predicate) -> tuple[Predicate, Predicate]:
    return tuple(sorted((first, second), key=lambda item: (item.feature, item.operator, item.threshold)))  # type: ignore[return-value]


def corpus_counts(context: Context, events: list[NamedEvent]) -> tuple[int, int, tuple[tuple[str, int], ...]]:
    false_total = true_total = 0
    by_corpus = {item.corpus: 0 for item in events}
    for item in events:
        event = item.event
        if not isinstance(event, DrumEvent) or not context.matches(event):
            continue
        if context.category in event.expected:
            true_total += 1
        else:
            false_total += 1
            by_corpus[item.corpus] += 1
    return false_total, true_total, tuple(sorted(by_corpus.items()))


def source_safe_primitives(category: str, events: list[DrumEvent]) -> list[Predicate]:
    """Keep one strongest zero-true primitive per feature/direction.

    The primitive is only a search seed.  The final two-feature context is
    re-evaluated across every real corpus and protected one-shot input.
    """
    selected: dict[tuple[str, str], tuple[int, Predicate]] = {}
    for feature in FEATURES:
        values = sorted({value(event, category, feature) for event in events if active(event, category) and category not in event.expected})
        for operator in ("<=", ">="):
            for threshold in values:
                predicate = Predicate(feature, operator, threshold)
                false_count = true_count = 0
                for event in events:
                    if not active(event, category) or not predicate.matches(event, category):
                        continue
                    if category in event.expected:
                        true_count += 1
                    else:
                        false_count += 1
                if false_count == 0 or true_count:
                    continue
                key = (feature, operator)
                previous = selected.get(key)
                if previous is None or false_count > previous[0] or (
                    false_count == previous[0] and predicate.threshold < previous[1].threshold
                ):
                    selected[key] = (false_count, predicate)
    return [entry[1] for _, entry in sorted(selected.items())]


def find_contexts(events: list[NamedEvent]) -> tuple[int, list[Context]]:
    corpus_names = sorted({item.corpus for item in events})
    primitives: dict[str, set[Predicate]] = {category: set() for category in CATEGORIES}
    for corpus in corpus_names:
        source_events = [item.event for item in events if item.corpus == corpus]
        typed_events = [event for event in source_events if isinstance(event, DrumEvent)]
        for category in CATEGORIES:
            primitives[category].update(source_safe_primitives(category, typed_events))

    raw: list[Context] = []
    primitive_count = sum(len(items) for items in primitives.values())
    for category, category_primitives in primitives.items():
        for first, second in combinations(sorted(category_primitives, key=Predicate.text), 2):
            if first.feature == second.feature:
                continue
            first, second = canonical_pair(first, second)
            provisional = Context(category, first, second, 0, ())
            false_total, true_total, by_corpus = corpus_counts(provisional, events)
            if true_total or not all(dict(by_corpus).get(corpus, 0) > 0 for corpus in corpus_names):
                continue
            raw.append(Context(category, first, second, false_total, by_corpus))

    # One representative per exact feature pair prevents threshold variants from
    # masquerading as independent opportunities.
    chosen: dict[tuple[str, str, str], Context] = {}
    for context in sorted(raw, key=lambda item: (-item.false_suppressed, item.text())):
        key = (context.category, context.first.feature, context.second.feature)
        chosen.setdefault(key, context)
    return primitive_count, sorted(chosen.values(), key=lambda item: (-item.false_suppressed, item.text()))


def protected_value(row: dict[str, str], category: str, feature: str) -> float | None:
    if feature in {"low", "mid", "high"}:
        field = f"energy_{feature}"
    elif feature == "upper_tom":
        field = "upper_tom_body"
    elif feature in {
        "kick_body", "snare_body", "tom_body", "snare_crack", "body_shape",
    }:
        field = feature
    elif feature == "trigger_ratio":
        try:
            return float(row[f"{category}_trigger"]) / max(float(row[f"{category}_threshold"]), 1.0e-6)
        except (KeyError, ValueError):
            return None
    else:
        field = f"{category}_{'shape' if feature == 'shape' else feature}"
    try:
        return float(row[field])
    except (KeyError, ValueError):
        return None


def predicate_matches_row(row: dict[str, str], category: str, predicate: Predicate) -> bool | None:
    observed = protected_value(row, category, predicate.feature)
    if observed is None:
        return None
    return observed <= predicate.threshold if predicate.operator == "<=" else observed >= predicate.threshold


def replay(context: Context, paths: list[Path]) -> ProtectedResult:
    rows = primary_suppressed = correct_suppressed = unsupported = 0
    for path in paths:
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                if row.get("got") != context.category:
                    continue
                rows += 1
                first = predicate_matches_row(row, context.category, context.first)
                second = predicate_matches_row(row, context.category, context.second)
                if first is None or second is None:
                    unsupported += 1
                    continue
                if first and second:
                    primary_suppressed += 1
                    correct_suppressed += int(row.get("expected") == context.category)
    return ProtectedResult(rows, primary_suppressed, correct_suppressed, unsupported)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-input", action="append", required=True, help="NAME=verbose-real-window-log")
    parser.add_argument("--protected", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    events: list[NamedEvent] = []
    for raw in args.real_input:
        try:
            corpus, text = raw.split("=", 1)
        except ValueError as error:
            raise SystemExit("--real-input must be NAME=PATH") from error
        events.extend(NamedEvent(corpus, event) for event in read_events([Path(text)]))
    primitive_count, contexts = find_contexts(events)
    results = [(context, replay(context, args.protected)) for context in contexts]
    safe = sum(result.unsupported == 0 and result.correct_suppressed == 0 for _, result in results)
    lines = [
        f"drum_false_positive_context_audit: primitives={primitive_count} "
        f"cross_real_contexts={len(contexts)} protected_runtime_safe={safe}/{len(contexts)}"
    ]
    for context, result in results:
        by_corpus = " ".join(f"{name}:{count}" for name, count in context.corpus_false_suppressed)
        eligible = result.unsupported == 0 and result.correct_suppressed == 0
        lines.append(
            f"context {context.text()}: real_false_suppressed={context.false_suppressed} "
            f"corpora={by_corpus} protected_primary_suppressed={result.primary_suppressed}/{result.rows} "
            f"protected_correct_suppressed={result.correct_suppressed} unsupported={result.unsupported} "
            f"eligible={int(eligible)}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
