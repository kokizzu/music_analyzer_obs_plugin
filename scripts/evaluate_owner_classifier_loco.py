#!/usr/bin/env python3
"""Evaluate a small owner classifier with leave-one-corpus-out validation."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


CLASSES = ("bass", "keyboard", "guitar", "vocal", "other")
FAMILY_TO_CLASS = {
    "bass": "bass",
    "piano": "keyboard",
    "guitar": "guitar",
    "vocals": "vocal",
    "other": "other",
}
OWNER_TO_CLASS = {
    "bass": "bass",
    "piano": "keyboard",
    "guitar": "guitar",
    "vocals": "vocal",
    "other": "other",
}
FEATURES = (
    "bass_score", "keyboard_score", "guitar_score", "vocal_score", "other_score",
)


def number(row: dict[str, str], field: str) -> float | None:
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def load(path: Path) -> list[tuple[str, str, tuple[float, ...]]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"family", "debug_owner", *FEATURES}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing owner-classifier columns: {', '.join(sorted(missing))}")
    samples = []
    for row in rows:
        target = FAMILY_TO_CLASS.get((row.get("family") or "").strip())
        if target is None:
            continue
        values = tuple(number(row, field) for field in FEATURES)
        if any(value is None or not math.isfinite(value) for value in values):
            continue
        samples.append((target, OWNER_TO_CLASS.get((row.get("debug_owner") or "").strip(), ""), values))
    return samples


def means(samples: list[tuple[str, str, tuple[float, ...]]]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    count = len(samples)
    center = tuple(sum(sample[2][index] for sample in samples) / count for index in range(len(FEATURES)))
    scale = tuple(
        max(math.sqrt(sum((sample[2][index] - center[index]) ** 2 for sample in samples) / count), 0.02)
        for index in range(len(FEATURES))
    )
    return center, scale


def classify(values: tuple[float, ...], center: tuple[float, ...], scale: tuple[float, ...],
             prototypes: dict[str, tuple[float, ...]]) -> str:
    normal = tuple((value - center[index]) / scale[index] for index, value in enumerate(values))
    return min(
        prototypes,
        key=lambda label: sum((normal[index] - prototypes[label][index]) ** 2 for index in range(len(FEATURES))),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", nargs="+", type=Path)
    args = parser.parse_args()
    loaded = [(path, load(path)) for path in args.attributes]
    for path, samples in loaded:
        if not samples:
            print(f"{path.name}: unavailable (no populated owner-score evidence)")
    corpora = [(path, samples) for path, samples in loaded if samples]
    if len(corpora) < 2:
        raise ValueError("need at least two corpora with populated owner-score evidence")
    print("owner classifier LOCO audit")
    total_current = total_model = total = 0
    supported = 0
    for held_path, held_samples in corpora:
        training = [sample for path, samples in corpora if path != held_path for sample in samples]
        center, scale = means(training)
        grouped: dict[str, list[tuple[float, ...]]] = defaultdict(list)
        for target, _, values in training:
            grouped[target].append(tuple((values[index] - center[index]) / scale[index] for index in range(len(FEATURES))))
        prototypes = {
            label: tuple(sum(value[index] for value in values) / len(values) for index in range(len(FEATURES)))
            for label, values in grouped.items()
        }
        current = model = 0
        for target, owner, values in held_samples:
            current += int(owner == target)
            model += int(classify(values, center, scale, prototypes) == target)
        total_current += current
        total_model += model
        total += len(held_samples)
        improved = model > current
        supported += int(improved)
        print(
            f"{held_path.name}: current={current}/{len(held_samples)} model={model}/{len(held_samples)} "
            f"delta={model - current:+d} improved={int(improved)}"
        )
    print(
        "owner_classifier_loco: "
        f"improved_corpora={supported}/{len(corpora)} current={total_current}/{total} "
        f"model={total_model}/{total}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
