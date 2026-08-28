#!/usr/bin/env python3
"""Mine bounded tom-from-snare recovery selectors from measured drum rows."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "build/drum_primary_miss_attribute_rows.tsv"
MAX_SINGLE = 48
MAX_RESULTS = 20


@dataclass(frozen=True)
class Rule:
    column: str
    operator: str
    threshold: float

    def matches(self, row: dict[str, float]) -> bool:
        value = row[self.column]
        return value >= self.threshold if self.operator == ">=" else value <= self.threshold

    def text(self) -> str:
        return f"{self.column}{self.operator}{self.threshold:.6g}"


def numeric_rows(expected_target: str, current_primary: str) -> tuple[list[dict[str, float]], list[str]]:
    with INPUT.open(encoding="utf-8", newline="") as handle:
        raw_rows = list(csv.DictReader(handle, delimiter="\t"))
    excluded = {"expected", "got", "sample", "category", "source"}
    columns = [column for column in raw_rows[0] if column not in excluded]
    rows: list[dict[str, float]] = []
    valid_columns: list[str] = []
    for column in columns:
        try:
            [float(row.get(column, "")) for row in raw_rows]
        except ValueError:
            continue
        valid_columns.append(column)
    for raw in raw_rows:
        row = {column: float(raw[column]) for column in valid_columns}
        row["__positive"] = 1.0 if raw.get("expected") == expected_target and raw.get("got") == current_primary else 0.0
        row["__negative"] = 1.0 if raw.get("expected") != expected_target and raw.get("got") == current_primary else 0.0
        rows.append(row)
    return rows, valid_columns


def thresholds(values: list[float]) -> list[float]:
    ordered = sorted(set(values))
    if len(ordered) <= 24:
        return ordered
    indexes = {round((len(ordered) - 1) * fraction / 24) for fraction in range(25)}
    return [ordered[index] for index in sorted(indexes)]


def score(rule: tuple[Rule, ...], rows: list[dict[str, float]]) -> tuple[int, int]:
    positives = 0
    negatives = 0
    for row in rows:
        if not all(item.matches(row) for item in rule):
            continue
        positives += int(row["__positive"])
        negatives += int(row["__negative"])
    return positives, negatives


def report_direction(expected_target: str, current_primary: str) -> None:
    rows, columns = numeric_rows(expected_target, current_primary)
    positives = sum(int(row["__positive"]) for row in rows)
    negatives = sum(int(row["__negative"]) for row in rows)
    print(f"## expected_{expected_target}_got_{current_primary}")
    print(f"rows={len(rows)} target_errors={positives} non_target_as_{current_primary}={negatives} numeric_columns={len(columns)}")

    singles: list[tuple[int, int, Rule]] = []
    for column in columns:
        for threshold in thresholds([row[column] for row in rows]):
            for operator in (">=", "<="):
                rule = Rule(column, operator, threshold)
                true_positives, false_positives = score((rule,), rows)
                if true_positives:
                    singles.append((true_positives, false_positives, rule))
    singles.sort(key=lambda item: (item[1] != 0, -item[0], item[1], item[2].text()))
    print("zero_false_single_rules")
    for true_positives, false_positives, rule in [item for item in singles if item[1] == 0 and item[0] >= 3][:20]:
        print(f"tp={true_positives} fp={false_positives} {rule.text()}")
    print("top_single_rules")
    for true_positives, false_positives, rule in singles[:20]:
        print(f"tp={true_positives} fp={false_positives} {rule.text()}")

    candidates = singles[:MAX_SINGLE]
    pairs: list[tuple[int, int, Rule, Rule]] = []
    for first_index, (_, _, first) in enumerate(candidates):
        for _, _, second in candidates[first_index + 1:]:
            if first.column == second.column:
                continue
            true_positives, false_positives = score((first, second), rows)
            if true_positives >= 2:
                pairs.append((true_positives, false_positives, first, second))
    pairs.sort(key=lambda item: (item[1] != 0, -item[0], item[1], item[2].text(), item[3].text()))
    print("zero_false_pair_rules")
    for true_positives, false_positives, first, second in [item for item in pairs if item[1] == 0 and item[0] >= 3][:MAX_RESULTS]:
        print(f"tp={true_positives} fp={false_positives} {first.text()} AND {second.text()}")
    print("top_pair_rules")
    for true_positives, false_positives, first, second in pairs[:MAX_RESULTS]:
        print(f"tp={true_positives} fp={false_positives} {first.text()} AND {second.text()}")


def main() -> int:
    if not INPUT.exists():
        print(f"missing {INPUT.relative_to(ROOT)}")
        return 1
    report_direction("tom", "snare")
    report_direction("snare", "tom")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
