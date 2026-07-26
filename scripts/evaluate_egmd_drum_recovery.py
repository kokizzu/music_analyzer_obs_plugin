#!/usr/bin/env python3
"""Score candidate real-track drum recovery rules from verbose E-GMD logs."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from summarize_egmd_drum_attributes import EVENT_RE
from summarize_egmd_drum_attributes import parse_details
from summarize_egmd_drum_attributes import split_categories


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


@dataclass(frozen=True)
class DrumEvent:
    recording: str
    sample: int
    expected: set[str]
    missing: set[str]
    metrics: dict[str, dict[str, float]]


@dataclass(frozen=True)
class CandidateRule:
    name: str
    category: str
    matches: Callable[[DrumEvent], bool]


def read_events(paths: list[Path]) -> list[DrumEvent]:
    events: dict[tuple[str, int, tuple[str, ...]], DrumEvent] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = EVENT_RE.match(line)
            if not match:
                continue
            expected = split_categories(match.group("expected"))
            missing = split_categories(match.group("missing"))
            metrics = parse_details(match.group("details"))
            key = (match.group("recording"), int(match.group("sample")), tuple(sorted(expected)))
            previous = events.get(key)
            if previous:
                missing = set(previous.missing) | missing
            events[key] = DrumEvent(
                recording=match.group("recording"),
                sample=int(match.group("sample")),
                expected=expected,
                missing=missing,
                metrics=metrics,
            )
    return list(events.values())


def value(event: DrumEvent, category: str, field: str) -> float:
    return float(event.metrics.get(category, {}).get(field, 0.0))


def active(event: DrumEvent, category: str) -> bool:
    return value(event, category, "active") > 0.0


def trigger_ratio(event: DrumEvent, category: str) -> float:
    threshold = value(event, category, "threshold")
    if threshold <= 0.0:
        return 0.0
    return value(event, category, "trigger") / threshold


def strongest(event: DrumEvent, categories: tuple[str, ...], field: str) -> float:
    return max((value(event, category, field) for category in categories), default=0.0)


def low_kick_body(event: DrumEvent) -> bool:
    return (
        value(event, "kick", "active") > 0.0
        or value(event, "kick", "supported") > 0.0
        or value(event, "kick", "trigger_ratio") >= 3.0
        or value(event, "kick", "low") >= 0.62
    )


def supported_low_snare(event: DrumEvent) -> bool:
    return (
        value(event, "snare", "supported") > 0.0
        and value(event, "snare", "level") >= 0.14
        and value(event, "snare", "body_shape") == 4.0
        and value(event, "snare", "trigger_ratio") >= 0.60
        and value(event, "snare", "rms") <= 0.030
        and value(event, "snare", "snare_body") >= 0.50
        and value(event, "snare", "snare_crack") >= value(event, "snare", "snare_body") * 0.050
        and value(event, "snare", "low") <= 0.55
        and value(event, "snare", "mid") >= value(event, "snare", "low") * 0.85
    )


def kick_backed_snare(event: DrumEvent) -> bool:
    return (
        low_kick_body(event)
        and trigger_ratio(event, "snare") >= 4.0
        and value(event, "snare", "transient") >= 1.55
        and value(event, "snare", "onset") >= 5.0
        and value(event, "snare", "snare_body") >= 8.0
        and value(event, "snare", "snare_crack") >= 1.0
        and value(event, "snare", "snare_crack") >= value(event, "snare", "snare_body") * 0.070
        and value(event, "snare", "mid") >= value(event, "snare", "low") * 0.08
    )


def embedded_ride(event: DrumEvent) -> bool:
    ride_seg = value(event, "ride", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        trigger_ratio(event, "ride") >= 3.0
        and value(event, "ride", "transient") >= 1.75
        and value(event, "ride", "onset") >= 3.0
        and value(event, "ride", "high") >= 0.010
        and ride_seg >= 0.95
        and ride_seg >= cymbal_max * 0.42
    )


def strong_embedded_ride(event: DrumEvent) -> bool:
    return embedded_ride(event) and trigger_ratio(event, "ride") >= 6.0


def embedded_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        trigger_ratio(event, "crash") >= 1.0
        and value(event, "crash", "transient") >= 1.50
        and value(event, "crash", "onset") >= 2.5
        and value(event, "crash", "high") >= 0.020
        and crash_seg >= 0.45
        and crash_seg >= cymbal_max * 0.32
    )


RULES = (
    CandidateRule("supported-low-snare", "snare", supported_low_snare),
    CandidateRule("kick-backed-snare", "snare", kick_backed_snare),
    CandidateRule("embedded-ride", "ride", embedded_ride),
    CandidateRule("strong-embedded-ride", "ride", strong_embedded_ride),
    CandidateRule("embedded-crash", "crash", embedded_crash),
)


def event_label(event: DrumEvent) -> str:
    expected = ",".join(sorted(event.expected))
    return f"{event.recording}@{event.sample} expected={expected}"


def summarize_rule(events: list[DrumEvent], rule: CandidateRule, example_count: int) -> str:
    tp: list[DrumEvent] = []
    fp: list[DrumEvent] = []
    already_active = 0
    matched = 0
    for event in events:
        if not rule.matches(event):
            continue
        matched += 1
        if active(event, rule.category):
            already_active += 1
            continue
        if rule.category in event.expected:
            tp.append(event)
        else:
            fp.append(event)

    by_expected: dict[str, int] = defaultdict(int)
    for event in tp:
        by_expected[",".join(sorted(event.expected))] += 1
    expected_summary = " ".join(f"{key}:{count}" for key, count in sorted(by_expected.items()))
    if not expected_summary:
        expected_summary = "--"

    lines = [
        f"rule={rule.name} category={rule.category} matched={matched} already_active={already_active} "
        f"tp_gain={len(tp)} fp_gain={len(fp)} net={len(tp) - len(fp)} expected={expected_summary}"
    ]
    for event in tp[:example_count]:
        lines.append(f"  tp {event_label(event)}")
    for event in fp[:example_count]:
        lines.append(f"  fp {event_label(event)}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--rule", action="append", default=[])
    args = parser.parse_args()

    events = read_events(args.logs)
    print(f"evaluate_egmd_drum_recovery: events={len(events)}")
    selected = [rule for rule in RULES if not args.rule or rule.name in args.rule]
    for rule in selected:
        print(summarize_rule(events, rule, args.examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
