#!/usr/bin/env python3
"""Find safe exact-pitch-class chord fallbacks across piano corpora.

Only no-label rows are considered. A proposed fallback must have an exact,
unambiguous major/minor triad or seventh pitch-class set and be correct for
every observed example in every independent corpus. This mines evidence; it
does not add a detector rule on its own.
"""

from __future__ import annotations

import argparse
import collections
import csv
from dataclasses import dataclass
from pathlib import Path


NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
PATTERNS = (("", (0, 4, 7)), ("m", (0, 3, 7)), ("maj7", (0, 4, 7, 11)),
            ("7", (0, 4, 7, 10)), ("m7", (0, 3, 7, 10)),
            ("m7b5", (0, 3, 6, 10)))


def labels(value: str) -> set[str]:
    return {item for item in value.split("/") if item and item != "--"}


def exact_fallback(value: str) -> str | None:
    try:
        pitch_classes = frozenset(NAMES.index(item) for item in value.split(",") if item)
    except ValueError:
        return None
    for suffix, intervals in PATTERNS:
        for root in range(12):
            if pitch_classes == frozenset((root + interval) % 12 for interval in intervals):
                return NAMES[root] + suffix
    return None


@dataclass
class Counts:
    total: int = 0
    correct: int = 0
    wrong: int = 0


def load(path: Path) -> dict[str, Counts]:
    result: dict[str, Counts] = collections.defaultdict(Counts)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"expected_chords", "keyboard_chord", "detected_chord_pcs"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
        for row in reader:
            if row["keyboard_chord"] not in {"", "--"}:
                continue
            candidate = exact_fallback(row["detected_chord_pcs"])
            if candidate is None or not labels(row["expected_chords"]):
                continue
            counts = result[candidate]
            counts.total += 1
            if candidate in labels(row["expected_chords"]):
                counts.correct += 1
            else:
                counts.wrong += 1
    return result


def render(paths: list[Path], min_per_corpus: int) -> list[str]:
    loaded = [(path, load(path)) for path in paths]
    shared = set.intersection(*(set(counts) for _, counts in loaded))
    safe = [candidate for candidate in shared if all(
        counts[candidate].total >= min_per_corpus and counts[candidate].wrong == 0
        for _, counts in loaded
    )]
    safe.sort()
    lines = [
        "independent_piano_exact_chord_fallback: "
        f"corpora={len(loaded)} shared_runtime_safe={len(safe)}"
    ]
    for candidate in safe:
        evidence = " ".join(
            f"{path.name}:{counts[candidate].correct}/{counts[candidate].total}"
            for path, counts in loaded
        )
        lines.append(f"  candidate={candidate} {evidence}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--min-per-corpus", type=int, default=2)
    args = parser.parse_args(argv)
    if len(args.inputs) < 2:
        parser.error("provide at least two independent corpus TSVs")
    try:
        print("\n".join(render(args.inputs, max(1, args.min_per_corpus))))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
