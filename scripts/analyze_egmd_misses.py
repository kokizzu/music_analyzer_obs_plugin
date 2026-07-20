#!/usr/bin/env python3
"""Summarize verbose E-GMD/MDB/STAR drum miss logs."""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path


LABEL_TO_CATEGORY = {
    "BASS DRUM": "kick",
    "SNARE": "snare",
    "HIHAT": "hihat",
    "CRASH": "crash",
    "TOMS": "tom",
    "RIDE": "ride",
    "RIM": "rim",
}

MISS_RE = re.compile(
    r"^E-GMD miss (?P<recording>\S+) sample (?P<sample>\d+) expected "
    r"(?P<expected>[^ ]+) missing (?P<missing>[^:]+): (?P<details>.*)$"
)
FALSE_POSITIVE_RE = re.compile(
    r"^E-GMD false-positive (?P<recording>\S+) sample (?P<sample>\d+) expected "
    r"(?P<expected>[^:]+): (?P<details>.*)$"
)
DEBUG_SEGMENT_RE = re.compile(r"^\s*(BASS DRUM|SNARE|HIHAT|CRASH|TOMS|RIDE|RIM)\s+band=.*\blevel=[0-9.]+\*")
LEVEL_LABEL_RE = re.compile(r"\b(BASS DRUM|SNARE|HIHAT|CRASH|TOMS|RIDE|RIM)=([0-9.]+)\*")


def split_categories(text: str) -> set[str]:
    return {part.strip() for part in text.split(",") if part.strip()}


def active_categories(details: str) -> set[str]:
    active = {
        LABEL_TO_CATEGORY[match.group(1)]
        for part in details.split("|")
        if (match := DEBUG_SEGMENT_RE.match(part))
    }
    active.update(LABEL_TO_CATEGORY[label] for label, _ in LEVEL_LABEL_RE.findall(details))
    return active


def add_examples(examples: dict[str, list[str]], key: str, value: str, limit: int) -> None:
    bucket = examples[key]
    if len(bucket) < limit:
        bucket.append(value)


def summarize(path: Path, example_limit: int = 5) -> str:
    miss_count = 0
    false_positive_count = 0
    missing_by_category: collections.Counter[str] = collections.Counter()
    false_positive_by_category: collections.Counter[str] = collections.Counter()
    miss_recordings: collections.Counter[str] = collections.Counter()
    false_positive_recordings: collections.Counter[str] = collections.Counter()
    missed_with_active: collections.Counter[str] = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        miss = MISS_RE.match(line)
        if miss:
            miss_count += 1
            recording = miss.group("recording")
            sample = miss.group("sample")
            expected = split_categories(miss.group("expected"))
            missing = split_categories(miss.group("missing"))
            active = active_categories(miss.group("details"))
            miss_recordings[recording] += 1
            for category in sorted(missing):
                missing_by_category[category] += 1
                if category in active:
                    missed_with_active[category] += 1
                add_examples(examples, f"miss {category}", f"{recording}@{sample} expected {','.join(sorted(expected))}", example_limit)
            continue

        false_positive = FALSE_POSITIVE_RE.match(line)
        if false_positive:
            false_positive_count += 1
            recording = false_positive.group("recording")
            sample = false_positive.group("sample")
            expected = split_categories(false_positive.group("expected"))
            active = active_categories(false_positive.group("details"))
            extras = active - expected
            false_positive_recordings[recording] += 1
            for category in sorted(extras):
                false_positive_by_category[category] += 1
                add_examples(examples, f"false {category}", f"{recording}@{sample} expected {','.join(sorted(expected))}", example_limit)

    lines: list[str] = []
    lines.append(f"egmd_misses {miss_count}")
    lines.append(f"egmd_false_positive_windows {false_positive_count}")
    if missing_by_category:
        lines.append("missing by category " + " ".join(f"{key}:{value}" for key, value in missing_by_category.most_common()))
    if missed_with_active:
        lines.append(
            "missing but active/dim "
            + " ".join(f"{key}:{value}" for key, value in missed_with_active.most_common())
        )
    if false_positive_by_category:
        lines.append(
            "false positives by category "
            + " ".join(f"{key}:{value}" for key, value in false_positive_by_category.most_common())
        )
    if miss_recordings:
        lines.append("top miss recordings " + " ".join(f"{key}:{value}" for key, value in miss_recordings.most_common(8)))
    if false_positive_recordings:
        lines.append(
            "top false-positive recordings "
            + " ".join(f"{key}:{value}" for key, value in false_positive_recordings.most_common(8))
        )
    for key in sorted(examples):
        lines.append(f"{key} examples " + " | ".join(examples[key]))
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: analyze_egmd_misses.py <verbose-log>", file=sys.stderr)
        return 2
    print(summarize(Path(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
