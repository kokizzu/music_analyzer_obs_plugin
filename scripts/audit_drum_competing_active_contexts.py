#!/usr/bin/env python3
"""Audit class-aware drum suppression contexts on annotated real mixes.

A candidate suppresses one active drum class only when another detected class is
active and either has a sufficiently high level or dominates the target level.
Candidates must remove no annotated target event in any supplied real-mix input,
then must preserve every correct protected one-shot primary row.  This is an
offline guardrail; it does not change runtime detection.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from evaluate_egmd_drum_recovery import DrumEvent, active, read_events, value


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
ACTIVE_LEVEL = 0.30


@dataclass(frozen=True)
class Candidate:
    target: str
    competitor: str
    mode: str
    threshold: float
    false_suppressed: int
    true_suppressed: int

    def text(self) -> str:
        if self.mode == "level":
            return f"{self.target} when {self.competitor}_level>={self.threshold:.6g}"
        return f"{self.target} when {self.competitor}/{self.target}>={self.threshold:.6g}"


def matches_event(event: DrumEvent, candidate: Candidate) -> bool:
    if not active(event, candidate.target) or value(event, candidate.competitor, "level") <= ACTIVE_LEVEL:
        return False
    competitor_level = value(event, candidate.competitor, "level")
    if candidate.mode == "level":
        return competitor_level >= candidate.threshold
    return competitor_level / max(value(event, candidate.target, "level"), 1.0e-6) >= candidate.threshold


def candidates_for(events: list[DrumEvent], target: str, competitor: str) -> list[Candidate]:
    false_events = [
        event for event in events
        if target not in event.expected and active(event, target)
        and value(event, competitor, "level") > ACTIVE_LEVEL
    ]
    if not false_events:
        return []
    candidates: list[Candidate] = []
    for mode in ("level", "ratio"):
        thresholds = {
            value(event, competitor, "level")
            if mode == "level"
            else value(event, competitor, "level") / max(value(event, target, "level"), 1.0e-6)
            for event in false_events
        }
        for threshold in sorted(thresholds):
            false_suppressed = true_suppressed = 0
            probe = Candidate(target, competitor, mode, threshold, 0, 0)
            for event in events:
                if not matches_event(event, probe):
                    continue
                if target in event.expected:
                    true_suppressed += 1
                else:
                    false_suppressed += 1
            if false_suppressed and not true_suppressed:
                candidates.append(Candidate(target, competitor, mode, threshold, false_suppressed, true_suppressed))
    return candidates


def non_dominated(candidates: list[Candidate]) -> list[Candidate]:
    """Keep the strongest zero-real-regression context per class relationship."""
    chosen: dict[tuple[str, str, str], Candidate] = {}
    for candidate in sorted(
        candidates,
        key=lambda item: (-item.false_suppressed, item.target, item.competitor, item.mode, item.threshold),
    ):
        chosen.setdefault((candidate.target, candidate.competitor, candidate.mode), candidate)
    return list(sorted(chosen.values(), key=lambda item: (-item.false_suppressed, item.text())))


@dataclass(frozen=True)
class ProtectedResult:
    rows: int
    primary_suppressed: int
    correct_suppressed: int
    unsupported: int


def matches_row(row: dict[str, str], candidate: Candidate) -> bool | None:
    try:
        target_level = float(row[f"{candidate.target}_level"])
        competitor_level = float(row[f"{candidate.competitor}_level"])
    except (KeyError, ValueError):
        return None
    if competitor_level <= ACTIVE_LEVEL:
        return False
    if candidate.mode == "level":
        return competitor_level >= candidate.threshold
    return competitor_level / max(target_level, 1.0e-6) >= candidate.threshold


def replay(candidate: Candidate, paths: list[Path]) -> ProtectedResult:
    rows = primary_suppressed = correct_suppressed = unsupported = 0
    for path in paths:
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source, delimiter="\t"):
                if row.get("got") != candidate.target:
                    continue
                rows += 1
                matched = matches_row(row, candidate)
                if matched is None:
                    unsupported += 1
                elif matched:
                    primary_suppressed += 1
                    correct_suppressed += int(row.get("expected") == candidate.target)
    return ProtectedResult(rows, primary_suppressed, correct_suppressed, unsupported)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-input", action="append", required=True, type=Path,
                        help="verbose annotated real-mix window log; may be repeated")
    parser.add_argument("--protected", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--runtime-replayed-context", action="append", default=[],
                        help="eligible context text already replayed through the runtime detector")
    parser.add_argument("--runtime-gain-context", action="append", default=[],
                        help="replayed eligible context with a verified cross-corpus runtime gain")
    args = parser.parse_args()
    events = read_events(args.real_input)
    candidates = non_dominated([
        candidate
        for target in CATEGORIES
        for competitor in CATEGORIES
        if competitor != target
        for candidate in candidates_for(events, target, competitor)
    ])
    replayed = set(args.runtime_replayed_context)
    gained = set(args.runtime_gain_context)
    safe = 0
    safe_contexts: set[str] = set()
    lines = [
        "drum_competing_active_context_audit: "
        f"real_candidates={len(candidates)} protected_runtime_safe=0/{len(candidates)}"
    ]
    for candidate in candidates:
        result = replay(candidate, args.protected)
        eligible = result.unsupported == 0 and result.correct_suppressed == 0
        safe += int(eligible)
        if eligible:
            safe_contexts.add(candidate.text())
        lines.append(
            f"context {candidate.text()}: real_false_suppressed={candidate.false_suppressed} "
            f"protected_primary_suppressed={result.primary_suppressed}/{result.rows} "
            f"protected_correct_suppressed={result.correct_suppressed} "
            f"unsupported={result.unsupported} eligible={int(eligible)} "
            f"runtime_replayed={int(candidate.text() in replayed)} "
            f"runtime_gain={int(candidate.text() in gained)}"
        )
    unknown_replayed = replayed - safe_contexts
    unknown_gained = gained - safe_contexts
    if unknown_replayed:
        raise ValueError(f"runtime-replayed contexts are not currently eligible: {sorted(unknown_replayed)}")
    if unknown_gained:
        raise ValueError(f"runtime-gain contexts are not currently eligible: {sorted(unknown_gained)}")
    if not gained.issubset(replayed):
        raise ValueError("runtime-gain contexts must also be marked runtime-replayed")
    replayed_safe = len(replayed & safe_contexts)
    gained_safe = len(gained & safe_contexts)
    lines[0] = (
        "drum_competing_active_context_audit: "
        f"real_candidates={len(candidates)} protected_runtime_safe={safe}/{len(candidates)} "
        f"runtime_replayed={replayed_safe}/{safe} runtime_gain={gained_safe}/{replayed_safe}"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
