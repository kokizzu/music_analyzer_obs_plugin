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
    dim7_primary_hit: int
    dim7_promotions: int
    dim7_regressions: int


def dim7_first(predicted: list[str]) -> str:
    """Prefer a same-root dim7 alias only over its ambiguous dim triad."""
    primary = predicted[0]
    if primary.endswith("dim") and primary + "7" in predicted[1:]:
        return primary + "7"
    return primary


def runtime_dim7_promotion(predicted: list[str]) -> bool:
    """Recognize the label order emitted by the narrow runtime promotion."""
    if len(predicted) < 2 or not predicted[0].endswith("dim7"):
        return False
    return predicted[0][:-1] in predicted[1:]


def measure(path: Path) -> Result:
    rows = displayed = any_hit = primary_hit = alias_rescued = 0
    dim7_primary_hit = dim7_promotions = dim7_regressions = 0
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
            dim7_selected = dim7_first(predicted)
            dim7_match = dim7_selected in expected
            promoted_at_runtime = runtime_dim7_promotion(predicted)
            any_hit += int(any_match)
            primary_hit += int(primary_match)
            alias_rescued += int(any_match and not primary_match)
            dim7_primary_hit += int(dim7_match)
            dim7_promotions += int(promoted_at_runtime)
            dim7_regressions += int(
                promoted_at_runtime and predicted[0][:-1] in expected and not primary_match
            )
    return Result(rows, displayed, any_hit, primary_hit, alias_rescued, dim7_primary_hit,
                  dim7_promotions, dim7_regressions)


def rescue_examples(path: Path, limit: int) -> list[str]:
    examples: list[str] = []
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            expected = labels(row.get("expected_chords", ""), "/")
            predicted = [item for item in row.get("keyboard_chord", "").split("=") if item and item != "--"]
            if not expected or len(predicted) < 2:
                continue
            if predicted[0] in expected or not any(item in expected for item in predicted[1:]):
                continue
            examples.append(
                f"  rescued recording={row.get('recording', '--')} sample={row.get('center_sample', '--')} "
                f"expected={'/'.join(sorted(expected))} primary={predicted[0]} aliases={'='.join(predicted)}"
            )
            if len(examples) >= limit:
                break
    return examples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--examples", type=int, default=0)
    args = parser.parse_args()
    results = [(path, measure(path)) for path in args.inputs]
    print("chord_primary_component_audit: corpora=" + str(len(results)))
    total = Result(0, 0, 0, 0, 0, 0, 0, 0)
    for path, result in results:
        print(
            f"corpus {path.stem}: rows={result.rows} displayed={result.displayed} "
            f"any_hit={result.any_hit}/{result.rows} primary_hit={result.primary_hit}/{result.rows} "
            f"alias_rescued={result.alias_rescued} dim7_primary_hit={result.dim7_primary_hit}/{result.rows} "
            f"dim7_promotions={result.dim7_promotions} dim7_regressions={result.dim7_regressions}"
        )
        for example in rescue_examples(path, max(0, args.examples)):
            print(example)
        total = Result(
            total.rows + result.rows,
            total.displayed + result.displayed,
            total.any_hit + result.any_hit,
            total.primary_hit + result.primary_hit,
            total.alias_rescued + result.alias_rescued,
            total.dim7_primary_hit + result.dim7_primary_hit,
            total.dim7_promotions + result.dim7_promotions,
            total.dim7_regressions + result.dim7_regressions,
        )
    print(
        f"chord_primary_component_audit: any_hit={total.any_hit}/{total.rows} "
        f"primary_hit={total.primary_hit}/{total.rows} alias_rescued={total.alias_rescued} "
        f"dim7_primary_hit={total.dim7_primary_hit}/{total.rows} "
        f"dim7_promotions={total.dim7_promotions} dim7_regressions={total.dim7_regressions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
