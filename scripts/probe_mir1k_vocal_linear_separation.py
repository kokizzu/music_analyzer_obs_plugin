#!/usr/bin/env python3
"""Evaluate whether compact per-note features separate MIR-1K vocals from protected rows."""

from __future__ import annotations

import csv
import hashlib
import math
import pathlib
import statistics


MIR_PATH = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")
REFERENCE_PATH = pathlib.Path("build/real_note_full_mix_attributes.tsv")
FEATURES = (
    "debug_midi", "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope",
    "noise", "partial2", "partial3", "partial4", "partial5",
)


def load(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def float_row(row: dict[str, str]) -> list[float] | None:
    if row.get("debug_midi", "") != row.get("expected_midi", ""):
        return None
    try:
        return [float(row[feature]) for feature in FEATURES]
    except (KeyError, ValueError):
        return None


def held_out(sample_id: str) -> bool:
    return int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[:8], 16) % 5 == 0


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, value))))


def main() -> int:
    positives = [(float_row(row), row["sample_id"]) for row in load(MIR_PATH)]
    positives = [(values, sample_id) for values, sample_id in positives if values is not None]
    negatives = []
    for row in load(REFERENCE_PATH):
        if row.get("family") == "vocals":
            continue
        values = float_row(row)
        if values is not None:
            negatives.append((values, row["sample_id"]))
    training = [(values, 1.0) for values, sample_id in positives if not held_out(sample_id)]
    training += [(values, 0.0) for values, sample_id in negatives if not held_out(sample_id)]
    testing = [(values, 1) for values, sample_id in positives if held_out(sample_id)]
    testing += [(values, 0) for values, sample_id in negatives if held_out(sample_id)]
    means = [statistics.fmean(values[index] for values, _ in training) for index in range(len(FEATURES))]
    scales = [max(1.0e-5, statistics.pstdev(values[index] for values, _ in training))
              for index in range(len(FEATURES))]
    weights = [0.0] * len(FEATURES)
    bias = 0.0
    positives_count = sum(label for _, label in training)
    negatives_count = len(training) - positives_count
    for _ in range(900):
        gradient = [0.0] * len(FEATURES)
        bias_gradient = 0.0
        for values, label in training:
            normalized = [(values[index] - means[index]) / scales[index] for index in range(len(FEATURES))]
            probability = sigmoid(bias + sum(weight * value for weight, value in zip(weights, normalized)))
            class_weight = 0.5 / (positives_count if label else negatives_count)
            error = (probability - label) * class_weight
            bias_gradient += error
            for index, feature in enumerate(normalized):
                gradient[index] += error * feature
        rate = 0.75
        bias -= rate * bias_gradient
        for index in range(len(weights)):
            weights[index] -= rate * (gradient[index] + 0.002 * weights[index])
    scored = []
    for values, label in testing:
        normalized = [(values[index] - means[index]) / scales[index] for index in range(len(FEATURES))]
        scored.append((sigmoid(bias + sum(weight * value for weight, value in zip(weights, normalized))), label))
    print(f"train positives={int(positives_count)} negatives={int(negatives_count)}")
    print(f"test positives={sum(label for _, label in scored)} negatives={sum(1 - label for _, label in scored)}")
    for threshold in (.50, .60, .70, .80, .90):
        true_positive = sum(score >= threshold and label for score, label in scored)
        false_positive = sum(score >= threshold and not label for score, label in scored)
        false_negative = sum(score < threshold and label for score, label in scored)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        print(f"threshold={threshold:.2f} precision={precision:.3f} recall={recall:.3f} "
              f"tp={true_positive} fp={false_positive} fn={false_negative}")
    print("weights (standardized):")
    for feature, weight, mean, scale in zip(FEATURES, weights, means, scales):
        print(f"{feature} weight={weight:.5f} mean={mean:.5f} scale={scale:.5f}")
    print(f"bias={bias:.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
