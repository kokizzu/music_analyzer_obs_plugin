#!/usr/bin/env python3
"""Measure whether a higher global-chord confidence floor is safe to display.

The analyzer's note rows deliberately retain their current-note state.  This
audit concerns the separate global chord label only: it counts correct labels
that a proposed confidence floor would hide, and incorrect labels it would
hide, for each labelled corpus.
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FLOORS = (0.00, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95)


@dataclass(frozen=True)
class Corpus:
    name: str
    rows: int
    displayed_correct: int
    displayed_wrong: int
    observations: tuple[tuple[float, bool], ...]


def read_corpus(path: Path) -> Corpus:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"global_chord", "global_chord_confidence", "chord_hit"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")

    observations = []
    for row in rows:
        label = (row["global_chord"] or "").strip()
        if not label or label == "--":
            continue
        try:
            confidence = float(row["global_chord_confidence"] or 0.0)
        except ValueError as error:
            raise ValueError(f"{path}: invalid confidence {row['global_chord_confidence']!r}") from error
        observations.append((confidence, row["chord_hit"] == "1"))
    return Corpus(
        path.stem,
        len(rows),
        sum(correct for _, correct in observations),
        sum(not correct for _, correct in observations),
        tuple(observations),
    )


def suppressed(corpus: Corpus, floor: float) -> tuple[int, int]:
    correct = sum(correct for confidence, correct in corpus.observations if confidence < floor)
    wrong = sum(not correct for confidence, correct in corpus.observations if confidence < floor)
    return correct, wrong


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", type=Path, nargs="+")
    parser.add_argument("--floors", type=float, nargs="*", default=DEFAULT_FLOORS)
    args = parser.parse_args()
    if any(floor < 0.0 or floor > 1.0 for floor in args.floors):
        parser.error("confidence floors must be in [0, 1]")

    corpora = [read_corpus(path) for path in args.attributes]
    print("global-chord confidence display audit")
    print("corpus\trows\tdisplayed correct\tdisplayed wrong\tdisplay precision")
    for corpus in corpora:
        displayed = corpus.displayed_correct + corpus.displayed_wrong
        precision = corpus.displayed_correct / displayed if displayed else 0.0
        print(
            f"{corpus.name}\t{corpus.rows}\t{corpus.displayed_correct}\t"
            f"{corpus.displayed_wrong}\t{precision:.1%}"
        )

    print("confidence floor\tcorrect hidden\twrong hidden\tcorrect retained\twrong retained\tretained precision\tzero-regression corpora")
    best_floor = 0.0
    best_supported = -1
    common_zero_regression = 0
    for floor in args.floors:
        hidden = [suppressed(corpus, floor) for corpus in corpora]
        correct_hidden = sum(item[0] for item in hidden)
        wrong_hidden = sum(item[1] for item in hidden)
        correct_total = sum(corpus.displayed_correct for corpus in corpora)
        wrong_total = sum(corpus.displayed_wrong for corpus in corpora)
        correct_retained = correct_total - correct_hidden
        wrong_retained = wrong_total - wrong_hidden
        retained = correct_retained + wrong_retained
        precision = correct_retained / retained if retained else 0.0
        zero_regression = sum(correct == 0 and wrong > 0 for correct, wrong in hidden)
        if zero_regression > best_supported:
            best_floor = floor
            best_supported = zero_regression
        if zero_regression == len(corpora):
            common_zero_regression += 1
        print(
            f"{floor:.2f}\t{correct_hidden}\t{wrong_hidden}\t{correct_retained}\t{wrong_retained}\t"
            f"{precision:.1%}\t{zero_regression}/{len(corpora)}"
        )
    print(
        "global_chord_confidence: "
        f"best_floor={best_floor:.2f} supported_corpora={best_supported}/{len(corpora)} "
        f"common_zero_regression_floors={common_zero_regression}"
    )


if __name__ == "__main__":
    main()
