#!/usr/bin/env python3
"""Audit a lower-octave harmonic-product correction on labelled choir windows.

The analyzer exports a geometric harmonic-product score for every full-mix
candidate.  This script keeps that diagnostic separate from routing: it asks
whether an upper-octave-only candidate would recover a labelled lower note,
and whether the same threshold would move a labelled correct candidate down.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


THRESHOLDS = (1.00, 1.25, 1.50, 2.00, 3.00, 4.00)


@dataclass(frozen=True)
class Candidate:
    midi: int
    lower_ratio: float


def parse_active_notes(value: str) -> list[int]:
    result: list[int] = []
    for item in value.split(","):
        try:
            _program, midi = item.split(":", 1)
            result.append(int(midi))
        except ValueError:
            continue
    return result


def parse_candidates(value: str) -> dict[int, Candidate]:
    result: dict[int, Candidate] = {}
    for item in value.split(";"):
        fields = item.split(",")
        # Fields 27 and 28 are harmonic_product_score and lower_subharmonic_product_ratio.
        try:
            midi = int(fields[0])
            lower_ratio = float(fields[28])
        except (IndexError, ValueError):
            continue
        result[midi] = Candidate(midi=midi, lower_ratio=lower_ratio)
    return result


def audit(path: Path) -> tuple[int, dict[float, tuple[int, int]]]:
    windows = 0
    values: list[tuple[bool, float]] = []
    with path.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"active_notes", "candidate_evidence"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
        for row in rows:
            candidates = parse_candidates(row["candidate_evidence"])
            for midi in parse_active_notes(row["active_notes"]):
                windows += 1
                direct = candidates.get(midi)
                upper = candidates.get(midi + 12)
                # A recovery must start from a genuine upward octave omission.
                if direct is None and upper is not None:
                    values.append((True, upper.lower_ratio))
                # A candidate already aligned to the annotation is protected.
                elif direct is not None:
                    values.append((False, direct.lower_ratio))
    result: dict[float, tuple[int, int]] = {}
    for threshold in THRESHOLDS:
        recoveries = sum(is_positive and ratio >= threshold for is_positive, ratio in values)
        protected = sum(not is_positive and ratio >= threshold for is_positive, ratio in values)
        result[threshold] = recoveries, protected
    return windows, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    inputs: list[tuple[str, Path]] = []
    for item in args.input:
        try:
            label, path_text = item.split("=", 1)
        except ValueError:
            parser.error(f"invalid --input {item!r}; use LABEL=PATH")
        inputs.append((label, Path(path_text)))

    lines = ["harmonic_product_octave: threshold recoveries protected zero_regression"]
    common = 0
    for threshold in THRESHOLDS:
        eligible = True
        for _label, path in inputs:
            _windows, result = audit(path)
            recoveries, protected = result[threshold]
            eligible = eligible and recoveries > 0 and protected == 0
        common += int(eligible)
    for label, path in inputs:
        windows, result = audit(path)
        lines.append(f"{label}: active_notes={windows}")
        for threshold, (recoveries, protected) in result.items():
            lines.append(
                f"  threshold={threshold:.2f} recoveries={recoveries} protected={protected} "
                f"zero_regression={int(recoveries > 0 and protected == 0)}"
            )
    lines.append(
        f"harmonic_product_octave: common_zero_regression_thresholds={common}/{len(THRESHOLDS)} "
        f"corpora={len(inputs)}"
    )
    text = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
