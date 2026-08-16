#!/usr/bin/env python3
"""Find a common conservative override margin for the quality owner model."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from evaluate_owner_classifier_loco import FEATURE_PROFILES, classify_with_margin, load, means


MARGINS = (0.00, 0.05, 0.10, 0.20, 0.40, 0.80, 1.60, 3.20, 6.40, 12.80, 25.60)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", nargs="+", type=Path)
    args = parser.parse_args()
    features = FEATURE_PROFILES["quality"]
    corpora = [(path, load(path, features)) for path in args.attributes]
    corpora = [(path, samples) for path, samples in corpora if samples]
    if len(corpora) < 2:
        raise ValueError("need at least two corpora with quality evidence")

    results: dict[float, list[tuple[int, int, int]]] = {margin: [] for margin in MARGINS}
    for held_path, held_samples in corpora:
        training = [sample for path, samples in corpora if path != held_path for sample in samples]
        center, scale = means(training)
        grouped: dict[str, list[tuple[float, ...]]] = defaultdict(list)
        for target, _owner, values in training:
            grouped[target].append(tuple((values[index] - center[index]) / scale[index] for index in range(len(features))))
        prototypes = {
            label: tuple(sum(value[index] for value in values) / len(values) for index in range(len(features)))
            for label, values in grouped.items()
        }
        current = sum(owner == target for target, owner, _values in held_samples)
        predictions = [
            (target, owner, *classify_with_margin(values, center, scale, prototypes))
            for target, owner, values in held_samples
        ]
        for margin in MARGINS:
            model = sum((prediction if prediction != owner and confidence >= margin else owner) == target
                        for target, owner, prediction, confidence in predictions)
            overrides = sum(prediction != owner and confidence >= margin for _target, owner, prediction, confidence in predictions)
            results[margin].append((current, model, overrides))

    print("owner_quality_override_margin: margin improved_corpora total_corpora current model overrides eligible")
    for margin in MARGINS:
        rows = results[margin]
        improved = sum(model > current for current, model, _overrides in rows)
        preserved = all(model >= current for current, model, _overrides in rows)
        current = sum(current for current, _model, _overrides in rows)
        model = sum(model for _current, model, _overrides in rows)
        overrides = sum(overrides for _current, _model, overrides in rows)
        eligible = int(preserved and model > current)
        print(f"  margin={margin:.2f} improved_corpora={improved}/{len(rows)} current={current} model={model} overrides={overrides} eligible={eligible}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
