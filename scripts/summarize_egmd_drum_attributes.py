#!/usr/bin/env python3
"""Print attribute distributions for verbose E-GMD/MDB/STAR drum miss logs."""

from __future__ import annotations

import argparse
import collections
import math
import re
from pathlib import Path
from typing import Iterable


LABEL_TO_CATEGORY = {
    "BASS DRUM": "kick",
    "SNARE": "snare",
    "HIHAT": "hihat",
    "CRASH": "crash",
    "TOMS": "tom",
    "RIDE": "ride",
    "RIM": "rim",
}

EVENT_RE = re.compile(
    r"^E-GMD (?P<kind>miss|false-positive) (?P<recording>\S+) sample (?P<sample>\d+) "
    r"expected (?P<expected>[^: ]+)(?: missing (?P<missing>[^:]+))?: (?P<details>.*)$"
)
CATEGORY_RE = re.compile(
    r"\b(?P<label>BASS DRUM|SNARE|HIHAT|CRASH|TOMS|RIDE|RIM) "
    r"band=(?P<band>[-+0-9.eE]+) "
    r"seg=(?P<seg>[-+0-9.eE]+) "
    r"shape=(?P<shape>[-+0-9.eE]+) "
    r"trig=(?P<trigger>[-+0-9.eE]+)/(?P<threshold>[-+0-9.eE]+) "
    r"supported=(?P<supported>[01]) "
    r"level=(?P<level>[-+0-9.eE]+)(?P<active>\*)?"
)
TAIL_RE = re.compile(
    r"\brms=(?P<rms>[-+0-9.eE]+) "
    r"energy=(?P<low>[-+0-9.eE]+)/(?P<mid>[-+0-9.eE]+)/(?P<high>[-+0-9.eE]+) "
    r"transient=(?P<transient>[-+0-9.eE]+) "
    r"onset=(?P<onset>[-+0-9.eE]+) "
    r"body=(?P<kick_body>[-+0-9.eE]+)/(?P<snare_body>[-+0-9.eE]+)/(?P<tom_body>[-+0-9.eE]+) "
    r"crack=(?P<snare_crack>[-+0-9.eE]+) "
    r"upperTom=(?P<upper_tom>[-+0-9.eE]+) "
    r"bodyShape=(?P<body_shape>\d+)"
)

NUMERIC_FIELDS = (
    "level",
    "band",
    "seg",
    "shape",
    "trigger",
    "threshold",
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


def split_categories(text: str | None) -> set[str]:
    if not text:
        return set()
    return {part.strip() for part in text.split(",") if part.strip()}


def safe_float(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        return 0.0


def parse_details(details: str) -> dict[str, dict[str, float]]:
    tail_values: dict[str, float] = {}
    tail = TAIL_RE.search(details)
    if tail:
        tail_values = {key: safe_float(value) for key, value in tail.groupdict().items()}

    category_values: dict[str, dict[str, float]] = {}
    for match in CATEGORY_RE.finditer(details):
        category = LABEL_TO_CATEGORY[match.group("label")]
        trigger = safe_float(match.group("trigger"))
        threshold = safe_float(match.group("threshold"))
        values = {
            "band": safe_float(match.group("band")),
            "seg": safe_float(match.group("seg")),
            "shape": safe_float(match.group("shape")),
            "trigger": trigger,
            "threshold": threshold,
            "trigger_ratio": trigger / threshold if threshold > 0.0 else 0.0,
            "supported": safe_float(match.group("supported")),
            "level": safe_float(match.group("level")),
            "active": 1.0 if match.group("active") else 0.0,
        }
        values.update(tail_values)
        category_values[category] = values
    return category_values


def parse_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        event = EVENT_RE.match(line)
        if not event:
            continue

        kind = event.group("kind")
        recording = event.group("recording")
        sample = int(event.group("sample"))
        expected = split_categories(event.group("expected"))
        missing = split_categories(event.group("missing"))
        categories = parse_details(event.group("details"))

        if kind == "miss":
            row_categories = missing
            status = "miss"
        else:
            row_categories = {
                category
                for category, values in categories.items()
                if category not in expected and values.get("active", 0.0) > 0.0
            }
            status = "false_positive"

        for category in sorted(row_categories):
            rows.append(
                {
                    "status": status,
                    "category": category,
                    "recording": recording,
                    "sample": sample,
                    "expected": ",".join(sorted(expected)),
                    "values": categories.get(category, {}),
                }
            )
    return rows


def percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def compact_counter(counter: collections.Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def row_key(row: dict[str, object]) -> str:
    return f"{row['status']}:{row['category']}"


def format_distribution(rows: Iterable[dict[str, object]], field: str) -> str:
    values: list[float] = []
    for row in rows:
        row_values = row["values"]
        if isinstance(row_values, dict) and field in row_values:
            values.append(float(row_values[field]))
    values.sort()
    if not values:
        return f"{field}=--"
    return (
        f"{field}=min{values[0]:.2f}/q25{percentile(values, 0.25):.2f}/"
        f"med{percentile(values, 0.50):.2f}/q75{percentile(values, 0.75):.2f}/max{values[-1]:.2f}"
    )


def event_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if EVENT_RE.match(line))


def summarize(
    path: Path,
    top: int = 10,
    examples: int = 3,
    recording: str = "",
    status: str = "",
    category: str = "",
) -> str:
    rows = parse_rows(path)
    if recording:
        rows = [row for row in rows if row["recording"] == recording]
    if status:
        rows = [row for row in rows if row["status"] == status]
    if category:
        rows = [row for row in rows if row["category"] == category]
    groups: dict[str, list[dict[str, object]]] = collections.defaultdict(list)
    for row in rows:
        groups[row_key(row)].append(row)

    lines = [f"summarize_egmd_drum_attributes: events {event_count(path)} rows {len(rows)}"]
    lines.append("status/category " + compact_counter(collections.Counter(row_key(row) for row in rows), top))

    for key, group_rows in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))[:top]:
        lines.append(f"{key} count {len(group_rows)}")
        for field in NUMERIC_FIELDS:
            lines.append("  " + format_distribution(group_rows, field))
        for row in group_rows[:examples]:
            values = row["values"] if isinstance(row["values"], dict) else {}
            lines.append(
                "  example "
                f"{row['recording']}@{row['sample']} expected={row['expected']} "
                f"level={values.get('level', 0.0):.2f} trigger={values.get('trigger', 0.0):.2f} "
                f"threshold={values.get('threshold', 0.0):.2f} supported={values.get('supported', 0.0):.0f}"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--recording", default="")
    parser.add_argument("--status", choices=("", "miss", "false_positive"), default="")
    parser.add_argument("--category", choices=("", *LABEL_TO_CATEGORY.values()), default="")
    args = parser.parse_args()
    print(
        summarize(
            args.log,
            top=args.top,
            examples=args.examples,
            recording=args.recording,
            status=args.status,
            category=args.category,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
