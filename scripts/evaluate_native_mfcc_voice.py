#!/usr/bin/env python3
"""Verify old timbre proposals with richer native spectral features."""
import csv
import hashlib
import json
import math
from pathlib import Path

from evaluate_next_detection import fit_forest

ROOT = Path(__file__).resolve().parents[1]
BASE_FEATURES = ["onset", "decay", "pitch_stability", "simultaneous_onset", "pitch", "periodicity",
                 "fit", "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transformed(row, features):
    values = [float(row[key]) for key in features]
    assert all(math.isfinite(value) for value in values)
    return [math.copysign(math.log1p(abs(value)), value) if i < 14 else value for i, value in enumerate(values)]


def tree_score(tree, values):
    if isinstance(tree, list):
        return tree[0]
    feature = tree["feature"]
    value = values[feature]
    epsilon = abs(value) * 1e-5 if feature < 14 else (1 + abs(value)) * 1e-7
    if value + epsilon <= tree["threshold"]:
        return tree_score(tree["left"], values)
    if value - epsilon > tree["threshold"]:
        return tree_score(tree["right"], values)
    return min(tree_score(tree["left"], values), tree_score(tree["right"], values))


def lower_probability(model, values):
    return sum(tree_score(tree, values) for tree in model["trees"]) / len(model["trees"])


def main():
    import numpy as np
    matches = []
    for path in (ROOT / "build/next_piano_timbre").glob("*/checkpoint.json"):
        state = json.loads(path.read_text())
        if state.get("spectral_features") and any(row.get("incomplete_pitch_labels") for row in state["selection"]):
            if all(digest(ROOT / p) == expected for p, expected in state["signatures"].items()):
                matches.append((path, state))
    assert len(matches) == 1, "Need one current spectral timbre capture"
    checkpoint, capture = matches[0]
    source = checkpoint.parent / "candidates.tsv"
    assert digest(source) == capture["candidates_sha256"]
    selected = {row["id"]: row for row in capture["selection"]}
    parent_path = ROOT / "models/keyboard_voice_classifier.json"
    parent = json.loads(parent_path.read_text())
    features = BASE_FEATURES + ["mfcc" + str(i) for i in range(24)]
    data = []
    with source.open() as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if not (row["mfcc_valid"] == row["visible_voice"] == row["visible_keyboard"] == "1" and row["owner"] == "2" and row["profile"] == "0" and
                    float(row["keyboard_score"]) >= .9 and float(row["guitar_score"]) <= .05 and float(row["vocal_score"]) <= .05 and
                    float(row["pitch"]) >= .7 and float(row["periodicity"]) >= .5):
                continue
            sample = selected[row["sample_id"]]
            expected = sample["family"] == "vocals" and int(row["midi"]) == sample["midi"]
            scored = True
            if sample.get("valid_end_seconds") is not None:
                scored = round(int(row["end_sample"]) / int(row["sample_rate"]), 3) in sample["valid_end_seconds"]
            if sample.get("incomplete_pitch_labels") and not expected:
                scored = False
            row.update(correct=expected, scored=scored, cohort=sample["family"] + "-" + sample["cohort"],
                       training=sample["cohort"].endswith("training"))
            data.append(row)
    training = [row for row in data if row["training"] and row["scored"]]
    assert sum(row["correct"] for row in training) >= 10 and sum(not row["correct"] for row in training) >= 10
    x = np.array([transformed(row, features) for row in training])
    y = np.array([int(row["correct"]) for row in training])
    predict, model = fit_forest(x, y, 2)
    probabilities = predict(x)[:, 0]
    threshold = max(.9, min(1., float(probabilities[y == 1].max()) + .01))
    metrics = {}
    for row in data:
        result = metrics.setdefault(row["cohort"], dict(eligible_cells=0, protected_correct=0, old_correct_losses=0,
                           correct_losses=0, wrong_removed=0, unscored_removals=0))
        old_probability = lower_probability(parent["model"], transformed(row, BASE_FEATURES))
        proposal = old_probability >= parent["threshold"]
        remove = proposal and lower_probability(model, transformed(row, features)) >= threshold
        result["eligible_cells"] += 1
        result["protected_correct"] += row["scored"] and row["correct"]
        result["old_correct_losses"] += proposal and row["scored"] and row["correct"]
        result["correct_losses"] += remove and row["scored"] and row["correct"]
        result["wrong_removed"] += remove and row["scored"] and not row["correct"]
        result["unscored_removals"] += remove and not row["scored"]
    passed = any(row["wrong_removed"] for name, row in metrics.items() if "heldout" in name) and not any(row["correct_losses"] for row in metrics.values())
    report = dict(model=model, features=features, threshold=threshold, parent_model_sha256=digest(parent_path),
                  metrics=metrics, training_rows=len(training), decision="candidate" if passed else "reject",
                  inputs={str(p.relative_to(ROOT)): digest(p) for p in (checkpoint, source, parent_path, Path(__file__), ROOT / "scripts/evaluate_next_detection.py")},
                  scope="Frozen old native proposals plus 100ms cepstral verification; pitch-disjoint NSynth regressions, singer-heldout human voices, recording-heldout mixtures/piano; incomplete mixture pitches explicitly unscored")
    output = ROOT / "build/next_detection/native_mfcc_voice.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key not in ("model", "features")}, indent=2))


if __name__ == "__main__":
    main()
