#!/usr/bin/env python3
"""Audit whether displaying only the first chord-label component is safe."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


def labels(value: str, separator: str) -> set[str]:
    return {item.strip() for item in value.split(separator) if item.strip() and item.strip() != "--"}


@dataclass(frozen=True)
class Result:
    rows: int
    displayed: int
    any_hit: int
    primary_hit: int
    alias_rescued: int


def measure(path: Path) -> Result:
    rows = displayed = any_hit = primary_hit = alias_rescued = 0
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"expected_chords", "keyboard_chord"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
        for row in reader:
            expected = labels(row["expected_chords"], "/")
            if not expected:
                continue
            rows += 1
            predicted = [item for item in row["keyboard_chord"].split("=") if item and item != "--"]
            if not predicted:
                continue
            displayed += 1
            any_match = any(item in expected for item in predicted)
            primary_match = predicted[0] in expected
            any_hit += int(any_match)
            primary_hit += int(primary_match)
            alias_rescued += int(any_match and not primary_match)
    return Result(rows, displayed, any_hit, primary_hit, alias_rescued)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    results = [(path, measure(path)) for path in args.inputs]
    print("chord_primary_component_audit: corpora=" + str(len(results)))
    total = Result(0, 0, 0, 0, 0)
    for path, result in results:
        print(
            f"corpus {path.stem}: rows={result.rows} displayed={result.displayed} "
            f"any_hit={result.any_hit}/{result.rows} primary_hit={result.primary_hit}/{result.rows} "
            f"alias_rescued={result.alias_rescued}"
        )
        total = Result(
            total.rows + result.rows,
            total.displayed + result.displayed,
            total.any_hit + result.any_hit,
            total.primary_hit + result.primary_hit,
            total.alias_rescued + result.alias_rescued,
        )
    print(
        f"chord_primary_component_audit: any_hit={total.any_hit}/{total.rows} "
        f"primary_hit={total.primary_hit}/{total.rows} alias_rescued={total.alias_rescued}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
