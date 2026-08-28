#!/usr/bin/env python3
"""Mine simple zero-false-positive MDB recovery selectors per drum category."""

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "mdb_drums_windows.log"
CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
LABELS = {
    "kick": "BASS DRUM",
    "snare": "SNARE",
    "hihat": "HIHAT",
    "crash": "CRASH",
    "tom": "TOMS",
    "ride": "RIDE",
    "rim": "RIM",
}
EXPECTED = re.compile(r"E-GMD window (.+?) sample (\d+) expected (.+?):")
LEVEL = re.compile(r"([A-Z ]+)=(\d+\.\d+)(\*)?")
DEBUG = re.compile(
    r"([A-Z ]+) band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d)"
)
TAIL = re.compile(
    r"rms=([0-9.]+) energy=([0-9.]+)/([0-9.]+)/([0-9.]+) "
    r"transient=([0-9.]+) onset=([0-9.]+) body=([0-9.]+)/([0-9.]+)/([0-9.]+) "
    r"crack=([0-9.]+) upperTom=([0-9.]+) bodyShape=(\d+)"
)


@dataclass
class Event:
    recording: str
    sample: str
    expected: set[str]
    levels: dict[str, float]
    active: dict[str, bool]
    values: dict[str, float]


def normalized_category(text: str) -> str | None:
    lowered = text.lower().strip()
    return next((category for category, label in LABELS.items() if label.lower() == lowered), None)


def read_events() -> list[Event]:
    events: list[Event] = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        expected = EXPECTED.search(line)
        tail = TAIL.search(line)
        if expected is None or tail is None:
            continue
        levels: dict[str, float] = {}
        active: dict[str, bool] = {}
        for match in LEVEL.finditer(line):
            category = normalized_category(match.group(1))
            if category is not None:
                levels[category] = float(match.group(2))
                active[category] = match.group(3) == "*"
        debug: dict[str, tuple[float, float, float, float, float]] = {}
        for match in DEBUG.finditer(line):
            category = normalized_category(match.group(1))
            if category is not None:
                debug[category] = tuple(float(match.group(index)) for index in range(2, 7))
        if len(levels) != len(CATEGORIES) or len(debug) != len(CATEGORIES):
            continue
        values = {
            "rms": float(tail.group(1)),
            "low": float(tail.group(2)),
            "mid": float(tail.group(3)),
            "high": float(tail.group(4)),
            "transient": float(tail.group(5)),
            "onset": float(tail.group(6)),
            "kick_body": float(tail.group(7)),
            "snare_body": float(tail.group(8)),
            "tom_body": float(tail.group(9)),
            "snare_crack": float(tail.group(10)),
            "upper_tom": float(tail.group(11)),
        }
        for category, (band, segment, shape, trigger, threshold) in debug.items():
            values[f"{category}_band"] = band
            values[f"{category}_seg"] = segment
            values[f"{category}_shape"] = shape
            values[f"{category}_trigger_ratio"] = trigger / max(threshold, 1.0e-6)
        events.append(Event(
            recording=expected.group(1),
            sample=expected.group(2),
            expected={part.strip().lower() for part in expected.group(3).split(",")},
            levels=levels,
            active=active,
            values=values,
        ))
    return events


def candidates(events: list[Event], category: str) -> list[tuple[int, str, str, float, int]]:
    positives = [event for event in events if category in event.expected and not event.active[category]
                 and event.levels[category] <= 0.30]
    negatives = [event for event in events if category not in event.expected and not event.active[category]
                 and event.levels[category] <= 0.30]
    found: list[tuple[int, str, str, float, int]] = []
    for feature in positives[0].values:
        thresholds = sorted({event.values[feature] for event in positives + negatives})
        for direction in ("<=", ">="):
            for threshold in thresholds:
                matches_positive = sum(
                    (event.values[feature] <= threshold if direction == "<=" else event.values[feature] >= threshold)
                    for event in positives
                )
                if matches_positive < 2:
                    continue
                matches_negative = sum(
                    (event.values[feature] <= threshold if direction == "<=" else event.values[feature] >= threshold)
                    for event in negatives
                )
                if matches_negative == 0:
                    found.append((matches_positive, feature, direction, threshold, len(negatives)))
    found.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
    return found


def main() -> int:
    events = read_events()
    print(f"mdb_drum_selector_events={len(events)}")
    for category in CATEGORIES:
        positive_count = sum(category in event.expected and not event.active[category] for event in events)
        print(f"{category}_missed={positive_count}")
        selected = candidates(events, category)
        for matched, feature, direction, threshold, negatives in selected[:8]:
            print(
                f"selector category={category} {feature}{direction}{threshold:.4g} "
                f"tp={matched} fp=0 protected={negatives}"
            )
        if selected:
            _, feature, direction, threshold, _ = selected[0]
            matches = [
                event for event in events
                if category in event.expected and not event.active[category]
                and event.levels[category] <= 0.30
                and (event.values[feature] <= threshold if direction == "<="
                     else event.values[feature] >= threshold)
            ]
            examples = ",".join(f"{event.recording}@{event.sample}" for event in matches)
            print(f"selector_examples category={category} {examples}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
