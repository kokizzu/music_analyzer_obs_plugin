#!/usr/bin/env python3
"""Summarize wrong monophonic-note selections from the bounded URMP trait run."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys


MISS = re.compile(
    r"^URMP track .* #\d+ (?P<instrument>[a-z]+) at .* expected "
    r"(?P<expected>[A-G]#?\d+), detected .* other `(?P<detected>[^`]*)`$"
)
NOTE = re.compile(r"^(?P<pitch_class>[A-G]#?)(?P<octave>\d+)$")


def first_note(label: str) -> str | None:
    for token in label.split():
        if NOTE.fullmatch(token):
            return token
    return None


def route(expected: str, detected: str) -> str:
    actual = first_note(detected)
    if actual is None:
        return "empty"
    expected_match = NOTE.fullmatch(expected)
    actual_match = NOTE.fullmatch(actual)
    assert expected_match is not None and actual_match is not None
    if expected_match["pitch_class"] == actual_match["pitch_class"]:
        return "same-pitch-class octave"
    return "different pitch class"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} TRAIT_OUTPUT", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    if not source.is_file():
        print(f"missing URMP trait output: {source}", file=sys.stderr)
        return 2

    route_counts: Counter[str] = Counter()
    wrong_routes: Counter[tuple[str, str, str]] = Counter()
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        match = MISS.match(line)
        if match is None:
            continue
        detected = match["detected"]
        route_name = route(match["expected"], detected)
        route_counts[route_name] += 1
        if route_name != "empty":
            wrong_routes[(match["instrument"], match["expected"], first_note(detected) or "--")] += 1

    total = sum(route_counts.values())
    print(f"URMP bounded isolated misses: {total}")
    print("count\tpercent\troute")
    for name, count in route_counts.most_common():
        percent = count * 100.0 / total if total else 0.0
        print(f"{count}\t{percent:.1f}%\t{name}")
    print("count\tinstrument\texpected\tpredicted")
    for (instrument, expected, predicted), count in wrong_routes.most_common(40):
        print(f"{count}\t{instrument}\t{expected}\t{predicted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
