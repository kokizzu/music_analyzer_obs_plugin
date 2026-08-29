#!/usr/bin/env python3
"""Evaluate a compact source-held-out timbre classifier before production use."""

from __future__ import annotations

import csv
import math
import random
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORIC_PATHS = tuple(ROOT / "build" / f"real_note_full_mix_attributes_{index}.tsv" for index in range(8))
EXPANSION_PATHS = tuple(
    ROOT / "build" / f"real_instrument_expansion_{family}_attributes_{index}.tsv"
    for family in ("guitar", "piano", "other") for index in range(4)
)
CLASSES = ("guitar", "piano", "vocals", "other")
FEATURES = (
    "pitch_confidence", "periodicity", "fit_error", "centroid", "slope", "noise",
    "partial2", "partial3", "partial4", "partial5", "harmonicity",
)


def value(row: dict[str, str], field: str) -> float:
    try:
        result = float(row[field])
    except (KeyError, ValueError):
        return math.nan
    return result if math.isfinite(result) else math.nan


def label(row: dict[str, str]) -> str | None:
    family = row.get("family")
    return family if family in CLASSES else None


def usable(row: dict[str, str]) -> bool:
    try:
        return int(row["debug_midi"]) == int(row["expected_midi"])
    except (KeyError, ValueError):
        return False


def read(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for path in paths:
        if not path.is_file():
            continue
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                rows.setdefault(row["sample_id"], row)
    return [row for row in rows.values() if label(row) and usable(row) and all(
        math.isfinite(value(row, feature)) for feature in FEATURES
    )]


def normalizer(rows: list[dict[str, str]]) -> tuple[list[float], list[float]]:
    means = [sum(value(row, feature) for row in rows) / len(rows) for feature in FEATURES]
    deviations = []
    for index, feature in enumerate(FEATURES):
        variance = sum((value(row, feature) - means[index]) ** 2 for row in rows) / len(rows)
        deviations.append(max(math.sqrt(variance), 1.0e-4))
    return means, deviations


def vector(row: dict[str, str], means: list[float], deviations: list[float]) -> list[float]:
    return [
        max(-6.0, min(6.0, (value(row, feature) - means[index]) / deviations[index]))
        for index, feature in enumerate(FEATURES)
    ]


def train(rows: list[dict[str, str]], means: list[float], deviations: list[float]) -> list[list[float]]:
    weights = [[0.0] * (len(FEATURES) + 1) for _ in CLASSES]
    counts = Counter(label(row) for row in rows)
    class_weight = {name: len(rows) / (len(CLASSES) * counts[name]) for name in CLASSES}
    order = list(range(len(rows)))
    random.Random(1337).shuffle(order)
    for epoch in range(300):
        learning_rate = 0.12 / (1.0 + epoch * 0.012)
        for position in order:
            row = rows[position]
            target = label(row)
            assert target is not None
            features = vector(row, means, deviations) + [1.0]
            logits = [sum(weight * feature for weight, feature in zip(group, features)) for group in weights]
            maximum = max(logits)
            exponentials = [math.exp(logit - maximum) for logit in logits]
            total = sum(exponentials)
            probabilities = [item / total for item in exponentials]
            scale = learning_rate * class_weight[target]
            for class_index, class_name in enumerate(CLASSES):
                error = (1.0 if class_name == target else 0.0) - probabilities[class_index]
                for feature_index, feature in enumerate(features):
                    weights[class_index][feature_index] += scale * error * feature
    return weights


def predict(row: dict[str, str], means: list[float], deviations: list[float], weights: list[list[float]]) -> str:
    features = vector(row, means, deviations) + [1.0]
    logits = [sum(weight * feature for weight, feature in zip(group, features)) for group in weights]
    return CLASSES[max(range(len(CLASSES)), key=lambda index: logits[index])]


def report(name: str, rows: list[dict[str, str]], means: list[float], deviations: list[float], weights: list[list[float]]) -> None:
    correct = 0
    total_by_class = Counter()
    correct_by_class = Counter()
    predicted = Counter()
    for row in rows:
        expected = label(row)
        assert expected is not None
        actual = predict(row, means, deviations, weights)
        total_by_class[expected] += 1
        predicted[f"{expected}->{actual}"] += 1
        if expected == actual:
            correct += 1
            correct_by_class[expected] += 1
    print(f"{name}=accuracy:{correct}/{len(rows)} ({100 * correct // len(rows)}%)")
    print("  recall=" + " ".join(
        f"{class_name}={correct_by_class[class_name]}/{total_by_class[class_name]}"
        for class_name in CLASSES if total_by_class[class_name]
    ))
    print("  routes=" + " ".join(f"{route}={count}" for route, count in predicted.most_common(12)))


def main() -> None:
    historic = read(HISTORIC_PATHS)
    if not historic:
        raise SystemExit("missing historic attributes; run make report-real-note-full-mix-attributes first")
    expansion = read(EXPANSION_PATHS)
    means, deviations = normalizer(historic)
    weights = train(historic, means, deviations)
    print(f"historic-fixtures={len(historic)} external-fixtures={len(expansion)}")
    report("historic-train", historic, means, deviations, weights)
    if expansion:
        report("external-held-out", expansion, means, deviations, weights)
    else:
        print("external-held-out=unavailable; run the physical family attribute reports first")


if __name__ == "__main__":
    main()
