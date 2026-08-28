#!/usr/bin/env python3
"""Train a shallow held-out decision tree to test real-vocal timbre separability."""

from __future__ import annotations

import csv
import hashlib
import pathlib


MIR_PATH = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")
REFERENCE_PATH = pathlib.Path("build/real_note_full_mix_attributes.tsv")
FEATURES = (
    "debug_midi", "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope",
    "noise", "partial2", "partial3", "partial4", "partial5",
)
MAX_DEPTH = 4
MIN_LEAF = 60


def load(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse(row: dict[str, str], label: int) -> tuple[list[float], int, str] | None:
    if row.get("debug_midi", "") != row.get("expected_midi", ""):
        return None
    try:
        return [float(row[feature]) for feature in FEATURES], label, row["sample_id"]
    except (KeyError, ValueError):
        return None


def held_out(sample_id: str) -> bool:
    return int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[:8], 16) % 5 == 0


def gini(rows: list[tuple[list[float], int, str]], positive_weight: float, negative_weight: float) -> float:
    positive = sum(positive_weight for _, label, _ in rows if label)
    negative = sum(negative_weight for _, label, _ in rows if not label)
    total = positive + negative
    if total == 0.0:
        return 0.0
    return 1.0 - (positive / total) ** 2 - (negative / total) ** 2


def weighted_count(rows: list[tuple[list[float], int, str]], positive_weight: float, negative_weight: float) -> float:
    return sum(positive_weight if label else negative_weight for _, label, _ in rows)


def best_split(rows: list[tuple[list[float], int, str]], positive_weight: float, negative_weight: float):
    parent = gini(rows, positive_weight, negative_weight)
    total = weighted_count(rows, positive_weight, negative_weight)
    best = None
    for index, _ in enumerate(FEATURES):
        values = sorted(row[0][index] for row in rows)
        thresholds = {values[int((len(values) - 1) * fraction / 32)] for fraction in range(1, 32)}
        for threshold in thresholds:
            left = [row for row in rows if row[0][index] <= threshold]
            right = [row for row in rows if row[0][index] > threshold]
            if len(left) < MIN_LEAF or len(right) < MIN_LEAF:
                continue
            impurity = (weighted_count(left, positive_weight, negative_weight) * gini(left, positive_weight, negative_weight) +
                        weighted_count(right, positive_weight, negative_weight) * gini(right, positive_weight, negative_weight)) / total
            gain = parent - impurity
            if best is None or gain > best[0]:
                best = gain, index, threshold, left, right
    return best


def build(rows, depth, positive_weight, negative_weight):
    positive = sum(1 for _, label, _ in rows if label)
    probability = (positive * positive_weight) / weighted_count(rows, positive_weight, negative_weight)
    node = {"probability": probability, "rows": len(rows), "positive": positive}
    if depth >= MAX_DEPTH or len(rows) < MIN_LEAF * 2:
        return node
    split = best_split(rows, positive_weight, negative_weight)
    if split is None or split[0] < 0.010:
        return node
    _, index, threshold, left, right = split
    node.update({"feature": index, "threshold": threshold,
                 "left": build(left, depth + 1, positive_weight, negative_weight),
                 "right": build(right, depth + 1, positive_weight, negative_weight)})
    return node


def predict(node, values):
    while "feature" in node:
        node = node["left"] if values[node["feature"]] <= node["threshold"] else node["right"]
    return node["probability"]


def print_tree(node, indent=""):
    if "feature" not in node:
        print(f"{indent}leaf p={node['probability']:.3f} positives={node['positive']}/{node['rows']}")
        return
    feature = FEATURES[node["feature"]]
    print(f"{indent}if {feature} <= {node['threshold']:.5f}:")
    print_tree(node["left"], indent + "  ")
    print(f"{indent}else:")
    print_tree(node["right"], indent + "  ")


def main() -> int:
    positive = [parse(row, 1) for row in load(MIR_PATH)]
    negative = [parse(row, 0) for row in load(REFERENCE_PATH) if row.get("family") != "vocals"]
    rows = [row for row in positive + negative if row is not None]
    train = [row for row in rows if not held_out(row[2])]
    test = [row for row in rows if held_out(row[2])]
    positive_train = sum(label for _, label, _ in train)
    negative_train = len(train) - positive_train
    tree = build(train, 0, 0.5 / positive_train, 0.5 / negative_train)
    print_tree(tree)
    for threshold in (.50, .60, .70, .80, .90):
        true_positive = false_positive = false_negative = 0
        for values, label, _ in test:
            predicted = predict(tree, values) >= threshold
            true_positive += int(predicted and label)
            false_positive += int(predicted and not label)
            false_negative += int(not predicted and label)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        print(f"threshold={threshold:.2f} precision={precision:.3f} recall={recall:.3f} "
              f"tp={true_positive} fp={false_positive} fn={false_negative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
