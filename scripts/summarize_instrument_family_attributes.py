#!/usr/bin/env python3
"""Summarize per-buffer instrument-family ownership evidence."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FAMILIES = ("guitar", "piano", "vocals", "other")


def ratio(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return f"{numerator}/{denominator} (--%)"
    return f"{numerator}/{denominator} ({numerator * 100.0 / denominator:.1f}%)"


def required(row: dict[str, str], field: str) -> str:
    value = row.get(field, "")
    if value == "":
        raise ValueError(f"missing required field `{field}`")
    return value


def summarize(path: Path, limit: int = 12) -> list[str]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        return ["instrument_family_attribute_summary: windows=0"]

    samples: dict[str, dict[str, object]] = {}
    for row in rows:
        sample_id = required(row, "sample_id")
        family = required(row, "family")
        if family not in FAMILIES:
            raise ValueError(f"unknown expected family `{family}`")
        instrument = required(row, "instrument")
        sample = samples.setdefault(sample_id, {
            "family": family,
            "instrument": instrument,
            "hit": False,
            "active": set(),
        })
        if sample["family"] != family or sample["instrument"] != instrument:
            raise ValueError(f"inconsistent family or instrument for sample `{sample_id}`")
        sample["hit"] = bool(sample["hit"]) or required(row, "expected_row_hit") == "1"
        active = sample["active"]
        assert isinstance(active, set)
        for actual in FAMILIES:
            if required(row, f"{actual}_active") == "1":
                active.add(actual)

    expected_total: Counter[str] = Counter()
    expected_hits: Counter[str] = Counter()
    routes: Counter[tuple[str, str]] = Counter()
    instruments: Counter[tuple[str, str]] = Counter()
    instrument_hits: Counter[tuple[str, str]] = Counter()
    for sample in samples.values():
        family = sample["family"]
        instrument = sample["instrument"]
        hit = bool(sample["hit"])
        active = sample["active"]
        assert isinstance(family, str) and isinstance(instrument, str) and isinstance(active, set)
        expected_total[family] += 1
        instruments[(family, instrument)] += 1
        if hit:
            expected_hits[family] += 1
            instrument_hits[(family, instrument)] += 1
            continue
        for actual in FAMILIES:
            if actual != family and actual in active:
                routes[(family, actual)] += 1

    output = [
        f"instrument_family_attribute_summary: samples={len(samples)} windows={len(rows)}",
        "expected family active "
        + " ".join(f"{family}={ratio(expected_hits[family], expected_total[family])}" for family in FAMILIES),
    ]
    if routes:
        output.append(
            "top expected-to-active wrong-row routes "
            + " ".join(
                f"{expected}->{actual}={count}"
                for (expected, actual), count in routes.most_common(limit)
            )
        )
    if instruments:
        output.append(
            "instrument expected-row recall "
            + " ".join(
                f"{family}/{instrument}={ratio(instrument_hits[(family, instrument)], total)}"
                for (family, instrument), total in instruments.most_common(limit)
            )
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attributes", type=Path)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    try:
        for line in summarize(args.attributes, max(0, args.limit)):
            print(line)
    except (OSError, ValueError, csv.Error) as error:
        raise SystemExit(f"summarize_instrument_family_attributes: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
