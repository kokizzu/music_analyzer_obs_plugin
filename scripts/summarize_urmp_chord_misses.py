#!/usr/bin/env python3
"""Summarize captured provided-mix URMP chord misses for offline rule mining."""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path


CHORD_MISS_RE = re.compile(
    r"^URMP (?P<piece>.+?) at (?P<time>[0-9.]+)s provided mix: chord opportunity "
    r"`(?P<expected>[^`]+)`, detected global `(?P<detected>[^`]+)`, key `(?P<key>[^`]+)`, "
    r"guitar `(?P<guitar>[^`]+)`, other `(?P<other>[^`]+)`, chroma (?P<chroma>.+)$"
)
ROOT_RE = re.compile(r"^[A-G](?:#|b)?(?P<quality>.*)$")


def components(label: str) -> tuple[str, ...]:
    return tuple(part for part in label.split("=") if part and part != "--")


def quality(label: str) -> str:
    match = ROOT_RE.match(label)
    if match is None:
        return label or "--"
    return match["quality"] or "major"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} URMP_TRAIT_OUTPUT", file=sys.stderr)
        return 2

    path = Path(argv[1])
    expected_quality = collections.Counter()
    detected_quality = collections.Counter()
    route_counts = collections.Counter()
    chroma_counts = collections.Counter()
    examples: dict[tuple[str, str], str] = {}
    misses = 0

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = CHORD_MISS_RE.match(line)
        if match is None:
            continue
        expected = components(match["expected"])
        detected = components(match["detected"])
        if set(expected).intersection(detected):
            continue
        misses += 1
        expected_key = "/".join(quality(part) for part in expected) or "--"
        detected_key = quality(detected[0]) if detected else "--"
        expected_quality[expected_key] += 1
        detected_quality[detected_key] += 1
        route = (expected_key, detected_key)
        route_counts[route] += 1
        examples.setdefault(route, line)
        chroma_counts[match["chroma"]] += 1

    print(f"URMP provided-mix chord misses: {misses}")
    print("count\texpected-quality")
    for label, count in expected_quality.most_common():
        print(f"{count}\t{label}")
    print("count\tdetected-primary-quality")
    for label, count in detected_quality.most_common():
        print(f"{count}\t{label}")
    print("count\texpected->detected")
    for route, count in route_counts.most_common(20):
        print(f"{count}\t{route[0]}->{route[1]}")
        print(f"  {examples[route]}")
    print("count\tchroma")
    for chroma, count in chroma_counts.most_common(12):
        print(f"{count}\t{chroma}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
