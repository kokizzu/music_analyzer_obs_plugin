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
    pitch_confidence: float
    periodicity: float
    fit_error: float
    noise: float


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
        # Fields 8/9/15/18 are existing pitch-quality features; 27 and 28 are
        # harmonic_product_score and lower_subharmonic_product_ratio.
        try:
            midi = int(fields[0])
            lower_ratio = float(fields[28])
            pitch_confidence = float(fields[8])
            periodicity = float(fields[9])
            fit_error = float(fields[15])
            noise = float(fields[18])
        except (IndexError, ValueError):
            continue
        result[midi] = Candidate(
            midi=midi,
            lower_ratio=lower_ratio,
            pitch_confidence=pitch_confidence,
            periodicity=periodicity,
            fit_error=fit_error,
            noise=noise,
        )
    return result


def audit(path: Path) -> tuple[int, list[tuple[bool, Candidate]]]:
    windows = 0
    values: list[tuple[bool, Candidate]] = []
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
                    values.append((True, upper))
                # A candidate already aligned to the annotation is protected.
                elif direct is not None:
                    values.append((False, direct))
    return windows, values


def threshold_counts(values: list[tuple[bool, Candidate]], threshold: float, predicate: object) -> tuple[int, int]:
    recoveries = sum(
        is_positive and candidate.lower_ratio >= threshold and predicate(candidate)
        for is_positive, candidate in values
    )
    protected = sum(
        not is_positive and candidate.lower_ratio >= threshold and predicate(candidate)
        for is_positive, candidate in values
    )
    return recoveries, protected


def quality_predicates() -> list[tuple[str, object]]:
    result: list[tuple[str, object]] = [("all", lambda candidate: True)]
    for maximum in (0.25, 0.50, 0.75):
        result.append((f"pitch_confidence<={maximum:.2f}", lambda candidate, m=maximum: candidate.pitch_confidence <= m))
    for maximum in (0.50, 0.65, 0.80):
        result.append((f"periodicity<={maximum:.2f}", lambda candidate, m=maximum: candidate.periodicity <= m))
    for minimum in (0.10, 0.20, 0.30):
        result.append((f"fit_error>={minimum:.2f}", lambda candidate, m=minimum: candidate.fit_error >= m))
    for minimum in (0.10, 0.20, 0.30):
        result.append((f"noise>={minimum:.2f}", lambda candidate, m=minimum: candidate.noise >= m))
    return result


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
    corpus_values = [(label, *audit(path)) for label, path in inputs]
    common = 0
    for threshold in THRESHOLDS:
        eligible = True
        for _label, _windows, values in corpus_values:
            recoveries, protected = threshold_counts(values, threshold, lambda candidate: True)
            eligible = eligible and recoveries > 0 and protected == 0
        common += int(eligible)
    for label, windows, values in corpus_values:
        lines.append(f"{label}: active_notes={windows}")
        for threshold in THRESHOLDS:
            recoveries, protected = threshold_counts(values, threshold, lambda candidate: True)
            lines.append(
                f"  threshold={threshold:.2f} recoveries={recoveries} protected={protected} "
                f"zero_regression={int(recoveries > 0 and protected == 0)}"
            )
    lines.append(
        f"harmonic_product_octave: common_zero_regression_thresholds={common}/{len(THRESHOLDS)} "
        f"corpora={len(inputs)}"
    )
    safe_selectors: list[tuple[int, str, float]] = []
    for condition, predicate in quality_predicates()[1:]:
        for threshold in THRESHOLDS:
            counts = [threshold_counts(values, threshold, predicate) for _label, _windows, values in corpus_values]
            if all(recoveries > 0 and protected == 0 for recoveries, protected in counts):
                safe_selectors.append((sum(recoveries for recoveries, _protected in counts), condition, threshold))
    lines.append("harmonic_product_octave: quality_filtered_zero_regression_selectors=")
    for recoveries, condition, threshold in sorted(safe_selectors, reverse=True)[:8]:
        lines.append(f"  recoveries={recoveries} ratio>={threshold:.2f} AND {condition}")
    if not safe_selectors:
        lines.append("  none")
    text = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
