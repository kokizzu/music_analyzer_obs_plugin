#!/usr/bin/env python3
"""Screen keyboard-chord display-confidence floors on continuous piano replay."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FLOORS = (0.00, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95)


@dataclass(frozen=True)
class Corpus:
    name: str
    observations: tuple[tuple[float, bool], ...]


def read_corpus(path: Path) -> Corpus:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"keyboard_chord", "keyboard_chord_confidence", "chord_hit"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
    observations = []
    for row in rows:
        label = (row["keyboard_chord"] or "").strip()
        if not label or label == "--":
            continue
        try:
            confidence = float(row["keyboard_chord_confidence"])
        except ValueError as error:
            raise ValueError(
                f"{path}: invalid keyboard_chord_confidence {row['keyboard_chord_confidence']!r}"
            ) from error
        observations.append((confidence, row["chord_hit"] == "1"))
    return Corpus(path.stem, tuple(observations))


def suppressed(corpus: Corpus, floor: float) -> tuple[int, int]:
    correct = sum(correct for confidence, correct in corpus.observations if confidence < floor)
    wrong = sum(not correct for confidence, correct in corpus.observations if confidence < floor)
    return correct, wrong


def render(paths: list[Path], floors: tuple[float, ...] = DEFAULT_FLOORS) -> str:
    corpora = [read_corpus(path) for path in paths]
    lines = [
        "piano chord display-confidence audit",
        "floor\tcorrect hidden\twrong hidden\tzero-regression corpora",
    ]
    best_floor = 0.0
    best_supported = 0
    common = 0
    for floor in floors:
        hidden = [suppressed(corpus, floor) for corpus in corpora]
        correct_hidden = sum(correct for correct, _ in hidden)
        wrong_hidden = sum(wrong for _, wrong in hidden)
        supported = sum(correct == 0 and wrong > 0 for correct, wrong in hidden)
        if supported > best_supported:
            best_floor = floor
            best_supported = supported
        if supported == len(corpora):
            common += 1
        lines.append(f"{floor:.2f}\t{correct_hidden}\t{wrong_hidden}\t{supported}/{len(corpora)}")
    lines.append(
        "piano_chord_display_confidence: "
        f"best_floor={best_floor:.2f} supported_corpora={best_supported}/{len(corpora)} "
        f"common_zero_regression_floors={common}"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audits", nargs=2, type=Path)
    parser.add_argument("--floors", nargs="*", type=float, default=DEFAULT_FLOORS)
    args = parser.parse_args()
    if any(floor < 0.0 or floor > 1.0 for floor in args.floors):
        parser.error("floors must be in [0, 1]")
    print(render(args.audits, tuple(args.floors)))


if __name__ == "__main__":
    main()
