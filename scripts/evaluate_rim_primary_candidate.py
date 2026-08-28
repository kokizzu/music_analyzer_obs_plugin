#!/usr/bin/env python3
"""Screen one source-neutral Rim primary candidate before runtime deployment.

The candidate comes from independent 0x808 and Virtuosity Rim misses.  This
script applies the same final-arbitration effect as ``promote_drum_primary`` to
cached debug TSV rows and reports every corrected and regressed sample.  It is
an offline veto: a nonzero regression count means the runtime rule must remain
disabled.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


CANDIDATE_NAME = "rim_from_snare_cross_source_v1"
ONE_SHOT_RULE_FLAG = 1 << 1
CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def value(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def rule_flags(row: dict[str, str]) -> int:
    try:
        return int(row.get("rule_flags", "0"), 0)
    except ValueError:
        return 0


def candidate_matches(row: dict[str, str], conditions: tuple[tuple[str, str, float], ...] = ()) -> bool:
    crash_hihat_band_ratio = value(row, "crash_band") / (value(row, "hihat_band") + 1.0e-6)
    tom_snare_band_ratio = value(row, "tom_band") / (value(row, "snare_band") + 1.0e-6)
    matches = (
        bool(rule_flags(row) & ONE_SHOT_RULE_FLAG)
        and value(row, "rim_level") > 0.30
        and crash_hihat_band_ratio <= 0.792
        and tom_snare_band_ratio <= 0.860
    )
    for field, operator, threshold in conditions:
        if field == "snare_kick_body_ratio":
            current = value(row, "snare_body") / (value(row, "kick_body") + 1.0e-6)
        else:
            current = value(row, field)
        matches = matches and (current >= threshold if operator == ">=" else current <= threshold)
    return matches


def parse_condition(text: str) -> tuple[str, str, float]:
    for operator in (">=", "<="):
        if operator in text:
            field, threshold = text.split(operator, 1)
            try:
                return field.strip(), operator, float(threshold)
            except ValueError as exc:
                raise argparse.ArgumentTypeError(f"invalid condition: {text}") from exc
    raise argparse.ArgumentTypeError(f"condition must use >= or <=: {text}")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    return [row for row in rows if row.get("sample") and row.get("expected") and row.get("got")]


def sample_key(path: Path, row: dict[str, str]) -> str:
    return f"{path.name}:{row['sample']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", type=Path)
    parser.add_argument("--examples", type=int, default=12)
    parser.add_argument("--condition", action="append", type=parse_condition, default=[],
                        help="additional static selector condition, e.g. crash_band>=1.033")
    parser.add_argument("--candidate-name", default=CANDIDATE_NAME)
    args = parser.parse_args()

    totals = Counter()
    selected = Counter()
    corrected: list[str] = []
    regressed: list[str] = []
    false_promotions: list[str] = []
    selected_by_source = Counter()

    for path in args.rows:
        if not path.is_file():
            raise SystemExit(f"missing rows: {path}")
        for row in load_rows(path):
            totals[row["expected"]] += 1
            if not candidate_matches(row, tuple(args.condition)):
                continue
            expected = row["expected"]
            before = row["got"]
            selected[expected] += 1
            selected_by_source[path.stem] += 1
            key = sample_key(path, row)
            if expected == "rim" and before != "rim":
                corrected.append(f"{key} {before}->rim")
            elif expected != "rim" and before == expected:
                regressed.append(f"{key} {before}->rim")
            elif expected != "rim":
                false_promotions.append(f"{key} {before}->rim expected={expected}")

    print(
        f"rim_primary_candidate: name={args.candidate_name} selected={sum(selected.values())} "
        f"corrected={len(corrected)} regressions={len(regressed)} "
        f"foreign_promotions={len(false_promotions)}"
    )
    print(
        "rim_primary_candidate: selected_by_expected="
        + " ".join(f"{category}={selected[category]}" for category in CATEGORIES)
    )
    print(
        "rim_primary_candidate: selected_by_source="
        + " ".join(f"{source}={count}" for source, count in sorted(selected_by_source.items()))
    )
    decision = "eligible_for_runtime_trial" if not regressed and not false_promotions and corrected else "reject"
    print(f"rim_primary_candidate: decision={decision}")
    for label, rows in (
        ("corrected", corrected),
        ("regression", regressed),
        ("foreign", false_promotions),
    ):
        for row in rows[: max(0, args.examples)]:
            print(f"rim_primary_candidate: {label} {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
