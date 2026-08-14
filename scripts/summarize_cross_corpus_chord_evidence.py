#!/usr/bin/env python3
"""Summarize compatible chord outcomes from independent labelled TSV corpora."""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path


def labels(value: str) -> set[str]:
    return {item for item in value.replace("=", ",").split(",") if item and item != "--"}


def instrument_column(fieldnames: set[str]) -> str:
    if "keyboard_chord" in fieldnames:
        return "keyboard_chord"
    if "guitar_chord" in fieldnames:
        return "guitar_chord"
    raise ValueError("missing keyboard_chord or guitar_chord")


def load(path: Path) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = set(reader.fieldnames or ())
        if not {"expected_chords", "chord_hit"}.issubset(fields):
            raise ValueError(f"{path}: missing expected_chords or chord_hit")
        predicted_column = instrument_column(fields)
        for row in reader:
            if not labels(row.get("expected_chords", "")):
                continue
            counts["eligible"] += 1
            if row.get("chord_hit", "") == "1":
                counts["hit"] += 1
                continue
            if not labels(row.get(predicted_column, "")):
                counts["miss_no_label"] += 1
            else:
                counts["miss_wrong_label"] += 1
    if not counts["eligible"]:
        raise ValueError(f"{path}: no eligible chord rows")
    return counts


def fraction(value: int, total: int) -> str:
    return f"{value}/{total} ({value * 100.0 / total:.1f}%)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    if len(args.inputs) < 2:
        raise SystemExit("provide at least two independent corpus TSVs")
    per_corpus = [(path, load(path)) for path in args.inputs]
    print(f"cross_corpus_chord_evidence: corpora={len(per_corpus)}")
    for path, counts in per_corpus:
        total = counts["eligible"]
        print(
            f"  {path.name}: hit={fraction(counts['hit'], total)} "
            f"no_label={fraction(counts['miss_no_label'], total)} "
            f"wrong_label={fraction(counts['miss_wrong_label'], total)}"
        )
    for outcome in ("miss_no_label", "miss_wrong_label"):
        replicated = sum(counts[outcome] > 0 for _, counts in per_corpus)
        print(f"  replicated_{outcome}: {replicated}/{len(per_corpus)} ({replicated * 100.0 / len(per_corpus):.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
