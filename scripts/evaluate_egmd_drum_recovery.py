#!/usr/bin/env python3
"""Score candidate real-track drum recovery rules from verbose E-GMD logs."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from summarize_egmd_drum_attributes import EVENT_RE
from summarize_egmd_drum_attributes import parse_details
from summarize_egmd_drum_attributes import split_categories


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
WINDOW_RE = re.compile(
    r"^E-GMD window (?P<recording>\S+) sample (?P<sample>\d+) "
    r"expected (?P<expected>[^: ]+): (?P<details>.*)$"
)


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
            window = WINDOW_RE.match(line)
            if not match and not window:
                continue
            source = match or window
            if source is None:
                continue
            expected = split_categories(source.group("expected"))
            metrics = parse_details(source.group("details"))
            missing = (
                split_categories(match.group("missing"))
                if match
                else {category for category in expected if not active_metrics(metrics, category)}
            )
            key = (source.group("recording"), int(source.group("sample")), tuple(sorted(expected)))
            previous = events.get(key)
            if previous:
                missing = set(previous.missing) | missing
            events[key] = DrumEvent(
                recording=source.group("recording"),
                sample=int(source.group("sample")),
                expected=expected,
                missing=missing,
                metrics=metrics,
            )
    return list(events.values())


def active_metrics(metrics: dict[str, dict[str, float]], category: str) -> bool:
    return float(metrics.get(category, {}).get("active", 0.0)) > 0.0


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


def low_crack_kick_backed_snare(event: DrumEvent) -> bool:
    """Real-track kick/snare overlaps whose low crack is still corroborated."""
    snare_body = value(event, "snare", "snare_body")
    crack = value(event, "snare", "snare_crack")
    kick_body = value(event, "snare", "kick_body")
    return (
        low_kick_body(event)
        and trigger_ratio(event, "snare") >= 7.5
        and value(event, "snare", "transient") >= 1.55
        and value(event, "snare", "onset") >= 15.0
        and snare_body >= 18.0
        and snare_body <= 34.0
        and snare_body >= kick_body * 0.26
        and crack >= 3.5
        and crack < 6.0
        and crack >= snare_body * 0.055
        and crack >= kick_body * 0.018
        and value(event, "snare", "mid") >= value(event, "snare", "low") * 0.08
        and value(event, "snare", "high") <= 0.22
    )


def low_treble_kick_backed_tom(event: DrumEvent) -> bool:
    """Low-treble real-kit kick/tom overlaps that remain distinctly tom-shaped."""
    tom_body = value(event, "tom", "tom_body")
    snare_body = value(event, "tom", "snare_body")
    kick_body = value(event, "tom", "kick_body")
    return (
        low_kick_body(event)
        and trigger_ratio(event, "tom") >= 20.0
        and value(event, "tom", "transient") >= 1.75
        and value(event, "tom", "onset") >= 15.0
        and 0.84 <= value(event, "tom", "low") <= 0.90
        and 0.08 <= value(event, "tom", "mid") <= 0.14
        and value(event, "tom", "high") <= 0.04
        and value(event, "tom", "seg") >= 50.0
        and 48.0 <= tom_body <= 56.0
        and 40.0 <= kick_body <= 52.0
        and 17.0 <= snare_body <= 22.0
        and 10.0 <= value(event, "tom", "upper_tom") <= 13.0
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


def mid_dominant_embedded_ride(event: DrumEvent) -> bool:
    return (
        strong_embedded_ride(event)
        and value(event, "ride", "low") <= 0.10
        and value(event, "ride", "mid") >= 0.70
        and value(event, "ride", "high") <= 0.20
    )


def low_rms_embedded_ride(event: DrumEvent) -> bool:
    return (
        strong_embedded_ride(event)
        and 0.84 <= value(event, "ride", "low") <= 0.88
        and 0.10 <= value(event, "ride", "mid") <= 0.14
        and 0.01 <= value(event, "ride", "high") <= 0.03
        and 0.035 <= value(event, "ride", "rms") <= 0.06
        and 20.0 <= value(event, "ride", "onset") <= 40.0
    )


def embedded_hihat(event: DrumEvent) -> bool:
    hihat_seg = value(event, "hihat", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        trigger_ratio(event, "hihat") >= 3.0
        and value(event, "hihat", "transient") >= 1.75
        and value(event, "hihat", "onset") >= 2.5
        and value(event, "hihat", "high") >= 0.02
        and hihat_seg >= 0.30
        and hihat_seg >= cymbal_max * 0.38
    )


def compact_embedded_hihat(event: DrumEvent) -> bool:
    return (
        embedded_hihat(event)
        and value(event, "hihat", "seg") <= 1.50
        and value(event, "hihat", "rms") <= 0.08
    )


def threshold_low_band_hihat(event: DrumEvent) -> bool:
    hihat_seg = value(event, "hihat", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.0 <= trigger_ratio(event, "hihat") <= 1.10
        and 1.40 <= value(event, "hihat", "transient") <= 1.60
        and 2.5 <= value(event, "hihat", "onset") <= 3.0
        and 0.020 <= value(event, "hihat", "rms") <= 0.050
        and 0.85 <= value(event, "hihat", "low") <= 0.92
        and 0.08 <= value(event, "hihat", "mid") <= 0.14
        and 0.01 <= value(event, "hihat", "high") <= 0.03
        and 0.35 <= hihat_seg <= 0.60
        and hihat_seg >= cymbal_max * 0.70
    )


def dense_low_high_hihat(event: DrumEvent) -> bool:
    hihat_seg = value(event, "hihat", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        trigger_ratio(event, "hihat") >= 10.0
        and value(event, "hihat", "transient") >= 1.90
        and value(event, "hihat", "onset") >= 40.0
        and 0.30 <= value(event, "hihat", "rms") <= 0.36
        and value(event, "hihat", "low") >= 0.85
        and value(event, "hihat", "mid") <= 0.10
        and value(event, "hihat", "high") <= 0.015
        and 3.0 <= hihat_seg <= 3.5
        and hihat_seg >= cymbal_max * 0.90
    )


def long_onset_low_rms_crash(event: DrumEvent) -> bool:
    return (
        embedded_crash(event)
        and value(event, "crash", "onset") >= 800.0
        and value(event, "crash", "rms") <= 0.06
        and value(event, "crash", "low") >= 0.84
        and value(event, "crash", "mid") <= 0.14
        and value(event, "crash", "high") <= 0.03
        and value(event, "crash", "seg") >= 1.50
    )


def mid_onset_low_rms_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        embedded_crash(event)
        and 20.0 <= value(event, "crash", "onset") <= 40.0
        and 0.04 <= value(event, "crash", "rms") <= 0.06
        and 0.82 <= value(event, "crash", "low") <= 0.86
        and 0.11 <= value(event, "crash", "mid") <= 0.15
        and 0.02 <= value(event, "crash", "high") <= 0.04
        and 1.0 <= crash_seg <= 1.5
        and crash_seg >= cymbal_max * 0.65
    )


def short_balanced_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.0 <= trigger_ratio(event, "crash") <= 1.10
        and 1.60 <= value(event, "crash", "transient") <= 1.70
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.065 <= value(event, "crash", "rms") <= 0.080
        and 0.65 <= value(event, "crash", "low") <= 0.73
        and 0.22 <= value(event, "crash", "mid") <= 0.28
        and 0.04 <= value(event, "crash", "high") <= 0.08
        and 1.0 <= crash_seg <= 1.2
        and crash_seg >= cymbal_max * 0.70
    )


def short_low_dominant_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.0 <= trigger_ratio(event, "crash") <= 1.10
        and 1.60 <= value(event, "crash", "transient") <= 1.70
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.080 <= value(event, "crash", "rms") <= 0.090
        and 0.85 <= value(event, "crash", "low") <= 0.90
        and 0.08 <= value(event, "crash", "mid") <= 0.12
        and 0.02 <= value(event, "crash", "high") <= 0.04
        and 0.50 <= crash_seg <= 0.65
        and crash_seg >= cymbal_max * 0.50
    )


def short_mid_heavy_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.0 <= trigger_ratio(event, "crash") <= 1.10
        and 1.90 <= value(event, "crash", "transient") <= 2.0
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.050 <= value(event, "crash", "rms") <= 0.060
        and 0.60 <= value(event, "crash", "low") <= 0.66
        and 0.30 <= value(event, "crash", "mid") <= 0.34
        and 0.04 <= value(event, "crash", "high") <= 0.06
        and 0.45 <= crash_seg <= 0.55
        and crash_seg >= cymbal_max * 0.40
    )


def broad_low_ratio_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.0 <= trigger_ratio(event, "crash") <= 1.10
        and 1.50 <= value(event, "crash", "transient") <= 1.65
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.12 <= value(event, "crash", "rms") <= 0.15
        and 0.80 <= value(event, "crash", "low") <= 0.86
        and 0.08 <= value(event, "crash", "mid") <= 0.12
        and 0.05 <= value(event, "crash", "high") <= 0.09
        and 2.0 <= crash_seg <= 2.5
        and crash_seg >= cymbal_max * 0.24
    )


def quiet_threshold_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        0.85 <= trigger_ratio(event, "crash") <= 0.90
        and 2.0 <= value(event, "crash", "transient") <= 2.2
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.015 <= value(event, "crash", "rms") <= 0.025
        and 0.84 <= value(event, "crash", "low") <= 0.88
        and 0.11 <= value(event, "crash", "mid") <= 0.15
        and 0.005 <= value(event, "crash", "high") <= 0.015
        and 0.15 <= crash_seg <= 0.25
        and crash_seg >= cymbal_max * 0.65
    )


def treble_dense_crash(event: DrumEvent) -> bool:
    crash_seg = value(event, "crash", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        1.10 <= trigger_ratio(event, "crash") <= 1.15
        and 2.0 <= value(event, "crash", "transient") <= 2.2
        and 2.5 <= value(event, "crash", "onset") <= 3.0
        and 0.065 <= value(event, "crash", "rms") <= 0.080
        and 0.60 <= value(event, "crash", "low") <= 0.68
        and 0.14 <= value(event, "crash", "mid") <= 0.18
        and 0.18 <= value(event, "crash", "high") <= 0.22
        and 1.0 <= crash_seg <= 1.2
        and crash_seg >= cymbal_max * 0.24
    )


def compact_low_rms_ride(event: DrumEvent) -> bool:
    ride_seg = value(event, "ride", "seg")
    cymbal_max = strongest(event, ("hihat", "crash", "ride"), "seg")
    return (
        3.0 <= trigger_ratio(event, "ride") <= 4.0
        and 2.0 <= value(event, "ride", "transient") <= 2.1
        and 3.0 <= value(event, "ride", "onset") <= 3.5
        and 0.035 <= value(event, "ride", "rms") <= 0.045
        and 0.84 <= value(event, "ride", "low") <= 0.86
        and 0.11 <= value(event, "ride", "mid") <= 0.13
        and 0.02 <= value(event, "ride", "high") <= 0.04
        and 1.4 <= ride_seg <= 1.7
        and ride_seg >= cymbal_max * 0.95
    )


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
    CandidateRule("low-crack-kick-backed-snare", "snare", low_crack_kick_backed_snare),
    CandidateRule("low-treble-kick-backed-tom", "tom", low_treble_kick_backed_tom),
    CandidateRule("embedded-ride", "ride", embedded_ride),
    CandidateRule("strong-embedded-ride", "ride", strong_embedded_ride),
    CandidateRule("mid-dominant-embedded-ride", "ride", mid_dominant_embedded_ride),
    CandidateRule("low-rms-embedded-ride", "ride", low_rms_embedded_ride),
    CandidateRule("embedded-hihat", "hihat", embedded_hihat),
    CandidateRule("compact-embedded-hihat", "hihat", compact_embedded_hihat),
    CandidateRule("threshold-low-band-hihat", "hihat", threshold_low_band_hihat),
    CandidateRule("dense-low-high-hihat", "hihat", dense_low_high_hihat),
    CandidateRule("embedded-crash", "crash", embedded_crash),
    CandidateRule("long-onset-low-rms-crash", "crash", long_onset_low_rms_crash),
    CandidateRule("mid-onset-low-rms-crash", "crash", mid_onset_low_rms_crash),
    CandidateRule("short-balanced-crash", "crash", short_balanced_crash),
    CandidateRule("short-low-dominant-crash", "crash", short_low_dominant_crash),
    CandidateRule("short-mid-heavy-crash", "crash", short_mid_heavy_crash),
    CandidateRule("broad-low-ratio-crash", "crash", broad_low_ratio_crash),
    CandidateRule("quiet-threshold-crash", "crash", quiet_threshold_crash),
    CandidateRule("treble-dense-crash", "crash", treble_dense_crash),
    CandidateRule("compact-low-rms-ride", "ride", compact_low_rms_ride),
)


def event_label(event: DrumEvent) -> str:
    expected = ",".join(sorted(event.expected))
    return f"{event.recording}@{event.sample} expected={expected}"


def event_traits(event: DrumEvent, category: str) -> str:
    return (
        f"level={value(event, category, 'level'):.2f} seg={value(event, category, 'seg'):.2f} "
        f"ratio={trigger_ratio(event, category):.2f} rms={value(event, category, 'rms'):.3f} "
        f"energy={value(event, category, 'low'):.2f}/{value(event, category, 'mid'):.2f}/"
        f"{value(event, category, 'high'):.2f} transient={value(event, category, 'transient'):.2f} "
        f"onset={value(event, category, 'onset'):.2f} body={value(event, category, 'kick_body'):.2f}/"
        f"{value(event, category, 'snare_body'):.2f}/{value(event, category, 'tom_body'):.2f} "
        f"crack={value(event, category, 'snare_crack'):.2f} upper_tom={value(event, category, 'upper_tom'):.2f}"
    )


def summarize_rule(events: list[DrumEvent], rule: CandidateRule, example_count: int, details: bool) -> str:
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
        suffix = f" {event_traits(event, rule.category)}" if details else ""
        lines.append(f"  tp {event_label(event)}{suffix}")
    for event in fp[:example_count]:
        suffix = f" {event_traits(event, rule.category)}" if details else ""
        lines.append(f"  fp {event_label(event)}{suffix}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--rule", action="append", default=[])
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    events = read_events(args.logs)
    print(f"evaluate_egmd_drum_recovery: events={len(events)}")
    selected = [rule for rule in RULES if not args.rule or rule.name in args.rule]
    for rule in selected:
        print(summarize_rule(events, rule, args.examples, args.details))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
