#!/usr/bin/env python3
"""Print reproducible, sample-level traits for missed instrument-family routes."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FAMILIES = ("guitar", "piano", "vocals", "other")


def required(row: dict[str, str], field: str) -> str:
    value = row.get(field, "")
    if value == "":
        raise ValueError(f"missing required field `{field}`")
    return value


def compact_counts(counts: Counter[str]) -> str:
    return ",".join(f"{name}:{count}" for name, count in counts.most_common()) or "--"


def compact_labels(labels: Counter[str]) -> str:
    return ",".join(f"{label}:{count}" for label, count in labels.most_common(4)) or "--"


def summarize(path: Path, limit: int = 20) -> list[str]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required_fields = {"sample_id", "family", "instrument", "expected_row_hit"}
        required_fields.update(f"{family}_{suffix}" for family in FAMILIES for suffix in ("active", "confidence", "label"))
        missing = required_fields - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}")
        samples: dict[str, dict[str, object]] = {}
        for row in reader:
            sample_id = required(row, "sample_id")
            family = required(row, "family")
            instrument = required(row, "instrument")
            if family not in FAMILIES:
                raise ValueError(f"{path}: unknown expected family `{family}`")
            sample = samples.setdefault(sample_id, {"family": family, "instrument": instrument, "rows": []})
            if sample["family"] != family or sample["instrument"] != instrument:
                raise ValueError(f"{path}: inconsistent family or instrument for `{sample_id}`")
            rows = sample["rows"]
            assert isinstance(rows, list)
            rows.append(row)
    if not samples:
        raise ValueError(f"{path}: no attribute rows")

    missed = [sample for sample in samples.values() if not any(required(row, "expected_row_hit") == "1" for row in sample["rows"])]
    missed_ids = {
        sample_id for sample_id, sample in samples.items()
        if not any(required(row, "expected_row_hit") == "1" for row in sample["rows"])
    }
    by_route: Counter[str] = Counter(f"{sample['family']}/{sample['instrument']}" for sample in missed)
    output = [
        f"instrument_family_miss_summary: misses={len(missed)}/{len(samples)}",
        "miss routes " + compact_counts(by_route),
    ]
    for sample_id, sample in ((key, value) for key, value in samples.items() if key in missed_ids):
        if len(output) - 2 >= max(0, limit):
            break
        rows = sample["rows"]
        assert isinstance(rows, list)
        active: Counter[str] = Counter()
        maxima = {family: 0.0 for family in FAMILIES}
        labels = {family: Counter() for family in FAMILIES}
        for row in rows:
            for family in FAMILIES:
                if required(row, f"{family}_active") == "1":
                    active[family] += 1
                try:
                    maxima[family] = max(maxima[family], float(required(row, f"{family}_confidence")))
                except ValueError as error:
                    raise ValueError(f"{path}: invalid {family}_confidence") from error
                label = required(row, f"{family}_label")
                if label != "--":
                    labels[family][label] += 1
        traits = " ".join(
            f"{family}[active={active[family]}/{len(rows)} max={maxima[family]:.3f} labels={compact_labels(labels[family])}]"
            for family in FAMILIES
        )
        output.append(
            f"miss sample={sample['family']}/{sample['instrument']} id={sample_id} buffers={len(rows)} {traits}"
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attributes", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    try:
        for line in summarize(args.attributes, args.limit):
            print(line)
    except (OSError, ValueError, csv.Error) as error:
        raise SystemExit(f"inspect_instrument_family_misses: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
