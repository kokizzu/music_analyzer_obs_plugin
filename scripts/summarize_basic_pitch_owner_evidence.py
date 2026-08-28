#!/usr/bin/env python3
"""Find zero-false Vocal-mirror rules in native+Basic-Pitch replay evidence."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


NUMERIC_FIELDS = (
    "native_confidence",
    "vocal_score",
    "keyboard_score",
    "guitar_score",
    "other_score",
    "pitch_confidence",
    "periodicity",
    "noise",
    "onnx_confidence",
)


def number(row: dict[str, str], field: str) -> float:
    return float(row[field])


def counts(rows: list[dict[str, str]]) -> tuple[int, int, set[str]]:
    correct = sum(row["vocal_truth"] == "1" for row in rows)
    false = sum(row["protected_false"] == "1" for row in rows)
    corpora = {row["corpus"] for row in rows if row["vocal_truth"] == "1"}
    return correct, false, corpora


def describe(rows: list[dict[str, str]]) -> list[str]:
    total_correct, total_false, _ = counts(rows)
    lines = [
        f"native+onnx owner evidence: rows={len(rows)} correct_vocal={total_correct} protected_false={total_false}",
        "by native owner:",
    ]
    by_owner: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_owner[row["native_owner"]].append(row)
    for owner in sorted(by_owner):
        correct, false, corpora = counts(by_owner[owner])
        lines.append(
            f"  {owner}: correct={correct} protected_false={false} vocal_corpora={','.join(sorted(corpora)) or '--'}"
        )

    exact_gate = [row for row in rows if row["candidate_gate"] == "1"]
    gate_correct, gate_false, gate_corpora = counts(exact_gate)
    lines.append(
        "validated shared candidate gate: "
        f"correct={gate_correct} protected_false={gate_false} vocal_corpora={','.join(sorted(gate_corpora)) or '--'}"
    )

    candidates: list[tuple[int, int, str, set[str]]] = []
    for owner, owner_rows in by_owner.items():
        if owner == "vocal":
            continue  # It is already a Vocal-owned native candidate, not a recovery.
        for field in NUMERIC_FIELDS:
            values = sorted({number(row, field) for row in owner_rows})
            for threshold in values:
                for operator in (">=", "<="):
                    selected = [
                        row
                        for row in owner_rows
                        if (number(row, field) >= threshold if operator == ">=" else number(row, field) <= threshold)
                    ]
                    correct, false, corpora = counts(selected)
                    if correct and false == 0:
                        candidates.append((correct, len(corpora), f"owner={owner} AND {field}{operator}{threshold:.6f}", corpora))

    # Remove rules which have the same recovery/corpus coverage as a simpler
    # prior rule; the report needs evidence, not a long threshold dump.
    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    unique: list[tuple[int, int, str, set[str]]] = []
    seen: set[tuple[int, int]] = set()
    for candidate in candidates:
        key = candidate[:2]
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
        if len(unique) == 8:
            break

    lines.append("zero-false candidate mirrors (native owner must not already be Vocal):")
    if not unique:
        lines.append("  --")
    for correct, corpus_count, rule, corpora in unique:
        eligibility = "eligible" if corpus_count >= 2 else "single-corpus only"
        lines.append(
            f"  +{correct} correct / 0 false, vocal_corpora={','.join(sorted(corpora))}: {eligibility} :: {rule}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    with args.input.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"corpus", "vocal_truth", "protected_false", "native_owner", "candidate_gate", *NUMERIC_FIELDS}
    if not rows or required - rows[0].keys():
        raise SystemExit("owner evidence TSV is missing required columns")
    rendered = "\n".join(describe(rows)) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
