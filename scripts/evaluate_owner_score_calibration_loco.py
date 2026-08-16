#!/usr/bin/env python3
"""Evaluate score-bias owner calibration with leave-one-corpus-out validation."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


CLASSES = ("bass", "keyboard", "guitar", "vocal", "other")
FAMILY_TO_CLASS = {
    "bass": "bass",
    "piano": "keyboard",
    "guitar": "guitar",
    "vocals": "vocal",
    "other": "other",
}
OWNER_TO_CLASS = FAMILY_TO_CLASS
FEATURES = (
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
)
BIAS_CANDIDATES = tuple(step / 100.0 for step in range(-40, 41, 10))
MAX_TRAINING_SAMPLES = 12000


def number(row: dict[str, str], field: str) -> float | None:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def load(path: Path) -> list[tuple[str, str, tuple[float, ...]]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"family", "debug_owner", *FEATURES}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing owner-calibration columns: {', '.join(sorted(missing))}")
    samples = []
    for row in rows:
        target = FAMILY_TO_CLASS.get((row.get("family") or "").strip())
        values = tuple(number(row, field) for field in FEATURES)
        if target is None or any(value is None for value in values):
            continue
        samples.append((target, OWNER_TO_CLASS.get((row.get("debug_owner") or "").strip(), ""), values))
    return samples


def classify(values: tuple[float, ...], biases: tuple[float, ...]) -> str:
    best_index = max(
        range(len(CLASSES)),
        key=lambda index: (values[index] + biases[index], -index),
    )
    return CLASSES[best_index]


def accuracy(samples: list[tuple[str, str, tuple[float, ...]]], biases: tuple[float, ...]) -> int:
    return sum(classify(values, biases) == target for target, _owner, values in samples)


def fit_biases(samples: list[tuple[str, str, tuple[float, ...]]]) -> tuple[float, ...]:
    stride = max(1, math.ceil(len(samples) / MAX_TRAINING_SAMPLES))
    samples = samples[::stride]
    biases = [0.0] * len(CLASSES)
    for _round in range(2):
        changed = False
        for index in range(len(CLASSES)):
            best_bias = biases[index]
            best_correct = -1
            for candidate in BIAS_CANDIDATES:
                trial = biases.copy()
                trial[index] = candidate
                correct = accuracy(samples, tuple(trial))
                if correct > best_correct or (correct == best_correct and abs(candidate) < abs(best_bias)):
                    best_correct = correct
                    best_bias = candidate
            changed |= best_bias != biases[index]
            biases[index] = best_bias
        if not changed:
            break
    return tuple(biases)


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

    print("owner score-calibration LOCO audit")
    total_current = total_model = total = supported = 0
    for held_path, held_samples in corpora:
        training = [sample for path, samples in corpora if path != held_path for sample in samples]
        biases = fit_biases(training)
        current = sum(owner == target for target, owner, _values in held_samples)
        model = accuracy(held_samples, biases)
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
        "owner_score_calibration_loco: "
        f"improved_corpora={supported}/{len(corpora)} current={total_current}/{total} "
        f"model={total_model}/{total}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
