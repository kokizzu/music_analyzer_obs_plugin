#!/usr/bin/env python3
"""Replay cross-real false-positive caps against protected primary drum rows."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from search_egmd_false_positive_caps import Candidate, NamedEvent, find_candidates, non_dominated
from evaluate_egmd_drum_recovery import read_events


def protected_value(row: dict[str, str], candidate: Candidate) -> float | None:
    feature = candidate.feature
    category = candidate.category
    if feature == "level":
        field = f"{category}_level"
    elif feature == "trigger_ratio":
        try:
            return float(row[f"{category}_trigger"]) / max(float(row[f"{category}_threshold"]), 1.0e-6)
        except (KeyError, ValueError):
            return None
    elif feature in {"low", "mid", "high"}:
        field = f"energy_{feature}"
    elif feature in {"kick_body", "snare_body", "tom_body", "snare_crack", "upper_tom", "body_shape"}:
        field = "upper_tom_body" if feature == "upper_tom" else feature
    else:
        return None
    try:
        return float(row[field])
    except (KeyError, ValueError):
        return None


def matches(value: float, candidate: Candidate) -> bool:
    return value <= candidate.threshold if candidate.operator == "<=" else value >= candidate.threshold


@dataclass(frozen=True)
class ProtectedResult:
    rows: int
    primary_suppressed: int
    correct_suppressed: int
    unsupported: int


def replay(candidate: Candidate, paths: list[Path]) -> ProtectedResult:
    rows = primary_suppressed = correct_suppressed = unsupported = 0
    for path in paths:
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                if row.get("got") != candidate.category:
                    continue
                rows += 1
                value = protected_value(row, candidate)
                if value is None:
                    unsupported += 1
                    continue
                if matches(value, candidate):
                    primary_suppressed += 1
                    correct_suppressed += int(row.get("expected") == candidate.category)
    return ProtectedResult(rows, primary_suppressed, correct_suppressed, unsupported)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real-input", action="append", required=True,
                        help="NAME=verbose-real-window-log")
    parser.add_argument("--protected", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    named_events: list[NamedEvent] = []
    for raw in args.real_input:
        try:
            corpus, text = raw.split("=", 1)
        except ValueError as error:
            raise SystemExit("--real-input must be NAME=PATH") from error
        path = Path(text)
        named_events.extend(NamedEvent(corpus, event) for event in read_events([path]))
    candidates = non_dominated(find_candidates(named_events, minimum_false_suppressed=2))
    corpus_names = {event.corpus for event in named_events}
    cross = [candidate for candidate in candidates
             if all(dict(candidate.corpus_false_suppressed).get(name, 0) > 0 for name in corpus_names)]
    lines = [f"drum_false_positive_cap_audit: real_candidates={len(candidates)} "
             f"cross_real_candidates={len(cross)} protected_runtime_safe=0/{len(cross)}"]
    safe = 0
    for candidate in cross:
        result = replay(candidate, args.protected)
        eligible = result.unsupported == 0 and result.correct_suppressed == 0
        safe += int(eligible)
        lines.append(
            f"cap {candidate.category} {candidate.feature}{candidate.operator}{candidate.threshold:.6g}: "
            f"real_false_suppressed={candidate.false_suppressed} "
            f"protected_primary_suppressed={result.primary_suppressed}/{result.rows} "
            f"protected_correct_suppressed={result.correct_suppressed} "
            f"unsupported={result.unsupported} eligible={int(eligible)}"
        )
    lines[0] = (f"drum_false_positive_cap_audit: real_candidates={len(candidates)} "
                f"cross_real_candidates={len(cross)} protected_runtime_safe={safe}/{len(cross)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
