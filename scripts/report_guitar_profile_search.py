#!/usr/bin/env python3
"""Find auditable high-precision guitar regions in historic full-mix attributes."""

from __future__ import annotations

import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE_PATHS = tuple(
    ROOT / "build" / f"real_note_full_mix_attributes_{index}.tsv" for index in range(8)
)
FEATURES = (
    "pitch_confidence", "periodicity", "fit_error", "centroid", "slope", "noise",
    "partial2", "partial3", "partial4", "partial5", "harmonicity",
)
VISUAL_COLUMNS = {
    "bass": "bass_visual_level",
    "guitar": "guitar_visual_level",
    "piano": "piano_visual_level",
    "vocals": "vocal_visual_level",
    "other": "other_visual_level",
}
MAX_DEPTH = 3
MIN_LEAF_ROWS = 12
MIN_LEAF_POSITIVES = 4


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, ValueError):
        return math.nan


@dataclass(frozen=True)
class Example:
    row: dict[str, str]
    label: bool


@dataclass
class Leaf:
    conditions: tuple[str, ...]
    examples: list[Example]

    @property
    def positives(self) -> int:
        return sum(example.label for example in self.examples)

    @property
    def precision(self) -> float:
        return self.positives / len(self.examples) if self.examples else 0.0


def read_examples(family: str) -> list[Example]:
    visual_column = VISUAL_COLUMNS[family]
    rows: dict[str, list[dict[str, str]]] = {}
    for path in ATTRIBUTE_PATHS:
        if not path.is_file():
            raise SystemExit("missing historic attribute exports; run make report-real-note-full-mix-attributes first")
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                rows.setdefault(row["sample_id"], []).append(row)
    examples: list[Example] = []
    for sample_rows in rows.values():
        sample_visible = any(number(row, visual_column) >= 0.25 for row in sample_rows)
        matching_rows: list[dict[str, str]] = []
        for row in sample_rows:
            try:
                expected_midi = int(row["expected_midi"])
                debug_midi = int(row["debug_midi"])
            except (KeyError, ValueError):
                continue
            if debug_midi == expected_midi and (family != "guitar" or 40 <= debug_midi <= 76):
                matching_rows.append(row)
        if not matching_rows:
            continue
        row = max(matching_rows, key=lambda candidate: number(candidate, visual_column))
        try:
            expected_midi = int(row["expected_midi"])
            debug_midi = int(row["debug_midi"])
        except (KeyError, ValueError):
            continue
        if not 40 <= debug_midi <= 76 or debug_midi != expected_midi:
            continue
        if any(not math.isfinite(number(row, feature)) for feature in FEATURES):
            continue
        # The profile targets only notes never bright enough to render in their row.
        positive = row["family"] == family and not sample_visible
        examples.append(Example(row, positive))
    return examples


def gini(examples: list[Example]) -> float:
    if not examples:
        return 0.0
    positive_fraction = sum(example.label for example in examples) / len(examples)
    return 2.0 * positive_fraction * (1.0 - positive_fraction)


def thresholds(examples: list[Example], feature: str) -> list[float]:
    values = sorted(number(example.row, feature) for example in examples)
    if not values:
        return []
    indexes = {int((len(values) - 1) * fraction / 24.0) for fraction in range(1, 24)}
    return sorted({values[index] for index in indexes})


def best_split(examples: list[Example]):
    baseline = gini(examples)
    best = None
    for feature in FEATURES:
        for threshold in thresholds(examples, feature):
            lower = [example for example in examples if number(example.row, feature) <= threshold]
            upper = [example for example in examples if number(example.row, feature) > threshold]
            if len(lower) < MIN_LEAF_ROWS or len(upper) < MIN_LEAF_ROWS:
                continue
            weighted = (len(lower) * gini(lower) + len(upper) * gini(upper)) / len(examples)
            gain = baseline - weighted
            candidate = (gain, feature, threshold, lower, upper)
            if best is None or candidate[:3] > best[:3]:
                best = candidate
    return best


def split_tree(examples: list[Example], conditions: tuple[str, ...], depth: int) -> list[Leaf]:
    if depth >= MAX_DEPTH:
        return [Leaf(conditions, examples)]
    split = best_split(examples)
    if split is None or split[0] <= 0.0:
        return [Leaf(conditions, examples)]
    _, feature, threshold, lower, upper = split
    return (
        split_tree(lower, conditions + (f"{feature}<={threshold:.3f}",), depth + 1) +
        split_tree(upper, conditions + (f"{feature}>{threshold:.3f}",), depth + 1)
    )


def main() -> None:
    details = "--details" in sys.argv
    family = "guitar"
    if "--family" in sys.argv:
        index = sys.argv.index("--family")
        if index + 1 >= len(sys.argv):
            raise SystemExit("--family requires bass, guitar, piano, vocals, or other")
        family = sys.argv[index + 1]
    if family not in VISUAL_COLUMNS:
        raise SystemExit("--family requires bass, guitar, piano, vocals, or other")
    examples = read_examples(family)
    positives = sum(example.label for example in examples)
    print(f"eligible={len(examples)} missed-{family}={positives}")
    leaves = split_tree(examples, (), 0)
    candidates = [leaf for leaf in leaves if leaf.positives >= MIN_LEAF_POSITIVES]
    candidates.sort(key=lambda leaf: (leaf.precision * leaf.positives, leaf.precision, leaf.positives), reverse=True)
    for leaf in candidates:
        routes = {}
        for example in leaf.examples:
            route = example.row["visual_first_row"]
            routes[route] = routes.get(route, 0) + 1
        print(
            f"leaf positives={leaf.positives}/{len(leaf.examples)} "
            f"precision={leaf.precision:.0%} conditions={' '.join(leaf.conditions)} "
            + "routes=" + ",".join(f"{route}:{count}" for route, count in sorted(routes.items()))
        )
        if details:
            positives = [example.row for example in leaf.examples if example.label]
            positive_routes: dict[str, int] = {}
            positive_sources: dict[str, int] = {}
            for row in positives:
                route = row["visual_first_row"]
                source = row["source"]
                positive_routes[route] = positive_routes.get(route, 0) + 1
                positive_sources[source] = positive_sources.get(source, 0) + 1
            print("  positive-routes=" + ",".join(
                f"{route}:{count}" for route, count in sorted(positive_routes.items())
            ))
            print("  positive-sources=" + ",".join(
                f"{source}:{count}" for source, count in sorted(positive_sources.items())
            ))
if __name__ == "__main__":
    main()
