#!/usr/bin/env python3
"""Compare general drum-primary scoring models against labeled debug TSV rows."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def value(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, ""))
    except ValueError:
        return 0.0


def score(row: dict[str, str], category: str, trigger_weight: float) -> float:
    level = value(row, f"{category}_level")
    if level <= 0.30:
        return -math.inf
    trigger_ratio = value(row, f"{category}_trigger") / max(
        value(row, f"{category}_threshold"), 1.0e-6)
    return level + trigger_weight * math.log1p(trigger_ratio)


def predicted(row: dict[str, str], trigger_weight: float) -> str:
    best = "none"
    best_score = -math.inf
    for category in CATEGORIES:
        candidate = score(row, category, trigger_weight)
        if candidate > best_score:
            best = category
            best_score = candidate
    return best


def summarize(rows: list[dict[str, str]], trigger_weight: float) -> tuple[int, Counter[tuple[str, str]]]:
    correct = 0
    confusion: Counter[tuple[str, str]] = Counter()
    for row in rows:
        expected = row["expected"]
        got = predicted(row, trigger_weight)
        confusion[(expected, got)] += 1
        correct += got == expected
    return correct, confusion


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--weights", default="0,0.002,0.005,0.01,0.02,0.04,0.08")
    args = parser.parse_args()

    with args.path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t")
                if row.get("expected") in CATEGORIES]
    if not rows:
        raise SystemExit("no labeled drum rows")

    baseline = sum(row.get("got") == row.get("expected") for row in rows)
    print(f"rows={len(rows)} baseline={baseline}/{len(rows)} {baseline / len(rows) * 100:.2f}%")
    for raw_weight in args.weights.split(","):
        trigger_weight = float(raw_weight)
        correct, confusion = summarize(rows, trigger_weight)
        differences = []
        for expected in CATEGORIES:
            baseline_hits = sum(
                row.get("expected") == expected and row.get("got") == expected for row in rows)
            candidate_hits = confusion[(expected, expected)]
            differences.append(f"{expected}={candidate_hits - baseline_hits:+d}")
        print(
            f"trigger_weight={trigger_weight:g} correct={correct}/{len(rows)} "
            f"{correct / len(rows) * 100:.2f}% delta={correct - baseline:+d} "
            + " ".join(differences))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
