#!/usr/bin/env python3
"""Evaluate drum-primary features with leave-one-corpus-out validation.

This is intentionally an offline diagnostic.  A candidate classifier is only
worth considering for runtime if it improves every held-out corpus over the
analyzer's current primary decision.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
PER_CATEGORY_FIELDS = ("level", "shape_score", "band", "seg")


def number(row: dict[str, str], field: str) -> float | None:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def feature_values(row: dict[str, str]) -> tuple[float, ...] | None:
    """Return scale-independent detector features for a single 100 ms row."""
    values: list[float] = []
    for field in PER_CATEGORY_FIELDS:
        category_values = [number(row, f"{category}_{field}") for category in CATEGORIES]
        if any(value is None for value in category_values):
            return None
        maximum = max(float(value) for value in category_values)
        scale = max(abs(maximum), 1.0e-6)
        values.extend(float(value) / scale for value in category_values)
    trigger_ratios = []
    for category in CATEGORIES:
        trigger = number(row, f"{category}_trigger")
        threshold = number(row, f"{category}_threshold")
        if trigger is None or threshold is None:
            return None
        trigger_ratios.append(math.log1p(trigger / max(threshold, 1.0e-6)))
    max_trigger = max(trigger_ratios)
    values.extend(value / max(max_trigger, 1.0e-6) for value in trigger_ratios)
    for field in ("energy_low", "energy_mid", "energy_high", "kick_body", "snare_body",
                  "tom_body", "snare_crack", "upper_tom_body"):
        value = number(row, field)
        if value is None:
            return None
        values.append(value)
    return tuple(values)


def load(path: Path) -> list[tuple[str, str, tuple[float, ...]]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected", "got", "energy_low", "energy_mid", "energy_high", "kick_body",
                "snare_body", "tom_body", "snare_crack", "upper_tom_body"}
    required.update(f"{category}_{field}" for category in CATEGORIES for field in PER_CATEGORY_FIELDS)
    required.update(f"{category}_{field}" for category in CATEGORIES for field in ("trigger", "threshold"))
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing drum-primary columns: {', '.join(sorted(missing))}")
    samples = []
    for row in rows:
        expected = (row.get("expected") or "").strip()
        if expected not in CATEGORIES:
            continue
        values = feature_values(row)
        if values is not None:
            samples.append((expected, (row.get("got") or "").strip(), values))
    return samples


def center_scale(samples: list[tuple[str, str, tuple[float, ...]]]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    dimensions = len(samples[0][2])
    center = tuple(sum(sample[2][index] for sample in samples) / len(samples) for index in range(dimensions))
    scale = tuple(max(math.sqrt(sum((sample[2][index] - center[index]) ** 2 for sample in samples) / len(samples)), 0.02)
                  for index in range(dimensions))
    return center, scale


def classify(values: tuple[float, ...], center: tuple[float, ...], scale: tuple[float, ...],
             prototypes: dict[str, tuple[float, ...]]) -> str:
    normal = tuple((value - center[index]) / scale[index] for index, value in enumerate(values))
    return min(
        (sum((normal[index] - prototype[index]) ** 2 for index in range(len(values))), label)
        for label, prototype in prototypes.items()
    )[1]


def fraction(count: int, total: int) -> str:
    return f"{count}/{total}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", nargs="+", type=Path)
    args = parser.parse_args()
    loaded = [(path, load(path)) for path in args.attributes]
    corpora = [(path, samples) for path, samples in loaded if samples]
    if len(corpora) < 2:
        raise ValueError("need at least two corpora with populated drum-primary evidence")

    print("drum primary LOCO audit feature_profile=normalized_detector_evidence")
    total_current = total_model = total = supported = 0
    all_current: Counter[str] = Counter()
    all_model: Counter[str] = Counter()
    all_expected: Counter[str] = Counter()
    for held_path, held_samples in corpora:
        training = [sample for path, samples in corpora if path != held_path for sample in samples]
        center, scale = center_scale(training)
        grouped: dict[str, list[tuple[float, ...]]] = defaultdict(list)
        for expected, _, values in training:
            grouped[expected].append(tuple((values[index] - center[index]) / scale[index]
                                             for index in range(len(values))))
        prototypes = {label: tuple(sum(values[index] for values in group) / len(group)
                                    for index in range(len(group[0])))
                      for label, group in grouped.items()}
        current = model = 0
        current_by_class: Counter[str] = Counter()
        model_by_class: Counter[str] = Counter()
        expected_by_class: Counter[str] = Counter()
        for expected, got, values in held_samples:
            candidate = classify(values, center, scale, prototypes)
            current_hit = got == expected
            model_hit = candidate == expected
            current += int(current_hit)
            model += int(model_hit)
            expected_by_class[expected] += 1
            current_by_class[expected] += int(current_hit)
            model_by_class[expected] += int(model_hit)
        total_current += current
        total_model += model
        total += len(held_samples)
        supported += int(model > current)
        all_current.update(current_by_class)
        all_model.update(model_by_class)
        all_expected.update(expected_by_class)
        deltas = " ".join(f"{category}={model_by_class[category] - current_by_class[category]:+d}"
                           for category in CATEGORIES if expected_by_class[category])
        print(f"{held_path.name}: current={fraction(current, len(held_samples))} "
              f"model={fraction(model, len(held_samples))} delta={model - current:+d} "
              f"improved={int(model > current)} {deltas}")
    target_deltas = " ".join(f"{category}={all_model[category] - all_current[category]:+d}"
                             for category in ("tom", "ride", "rim") if all_expected[category])
    print("drum_primary_loco: "
          f"improved_corpora={fraction(supported, len(corpora))} current={fraction(total_current, total)} "
          f"model={fraction(total_model, total)} target_delta={target_deltas or 'n/a'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
