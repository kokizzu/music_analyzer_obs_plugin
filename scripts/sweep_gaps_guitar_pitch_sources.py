#!/usr/bin/env python3
"""Compare GAPS guitar pitch recall/precision for persisted candidate level sources."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/gaps_guitar_attributes.tsv"
SOURCES = (
    "raw_pitch_class_levels",
    "guitar_probe_pitch_class_levels",
    "guitar_detection_pitch_class_levels",
)
FLOORS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60)


def parse_pitch_classes(value: str) -> set[str]:
    return {item for item in value.split(",") if item and item != "--"}


def parse_levels(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in value.split(","):
        if not item or ":" not in item:
            continue
        name, level = item.split(":", 1)
        result[name] = float(level)
    return result


@dataclass
class Score:
    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0
    exact_rows: int = 0
    covered_rows: int = 0
    rows: int = 0

    def add(self, expected: set[str], predicted: set[str]) -> None:
        self.true_positive += len(expected & predicted)
        self.false_positive += len(predicted - expected)
        self.false_negative += len(expected - predicted)
        self.exact_rows += predicted == expected
        self.covered_rows += expected <= predicted
        self.rows += 1

    def render(self) -> str:
        precision = self.true_positive / max(1, self.true_positive + self.false_positive)
        recall = self.true_positive / max(1, self.true_positive + self.false_negative)
        f1 = 2.0 * precision * recall / max(1.0e-9, precision + recall)
        return (f"precision={precision:.3f} recall={recall:.3f} f1={f1:.3f} "
                f"exact={self.exact_rows}/{self.rows} covered={self.covered_rows}/{self.rows}")


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = [row for row in rows if row.get("instrument") == "guitar"]
    print(f"guitar_rows={len(rows)}")

    displayed = Score()
    for row in rows:
        displayed.add(parse_pitch_classes(row["expected_pitch_classes"]),
                      parse_pitch_classes(row["guitar_pitch_classes"]))
    print("displayed " + displayed.render())

    for source in SOURCES:
        print(f"## {source}")
        for floor in FLOORS:
            score = Score()
            for row in rows:
                expected = parse_pitch_classes(row["expected_pitch_classes"])
                levels = parse_levels(row[source])
                strongest = max(levels.values(), default=0.0)
                predicted = {name for name, level in levels.items() if level >= strongest * floor}
                score.add(expected, predicted)
            print(f"floor={floor:.2f} {score.render()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
