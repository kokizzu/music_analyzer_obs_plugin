#!/usr/bin/env python3
"""Audit a relative raw-chroma recovery gate for missed SATB pitch classes.

An absolute raw-chroma floor is unsafe when the whole frame is quiet or loud.
This diagnostic instead measures every missing/extra pitch class relative to the
strongest raw-chroma class in the same labelled frame.  It is actionable only
when a single threshold recovers one or more missing classes while adding zero
extras in every independently prepared SATB corpus.
"""

from __future__ import annotations

import argparse
import csv
from collections.abc import Iterable
from pathlib import Path


THRESHOLDS = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90)


def parse_pitch_classes(value: str) -> set[str]:
    return {item for item in value.split() if item}


def parse_chroma(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for token in value.split():
        try:
            name, level = token.split(":", 1)
            result[name] = float(level)
        except ValueError:
            continue
    return result


def relative_levels(path: Path) -> tuple[list[float], list[float]]:
    missing_levels: list[float] = []
    extra_levels: list[float] = []
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"missing_pcs", "extra_pcs", "raw_chroma"}
        absent = required - set(reader.fieldnames or ())
        if absent:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(absent))}")
        for row in reader:
            chroma = parse_chroma(row["raw_chroma"])
            peak = max(chroma.values(), default=0.0)
            if peak <= 0.0:
                continue
            missing_levels.extend(chroma.get(pc, 0.0) / peak for pc in parse_pitch_classes(row["missing_pcs"]))
            extra_levels.extend(chroma.get(pc, 0.0) / peak for pc in parse_pitch_classes(row["extra_pcs"]))
    return missing_levels, extra_levels


def format_counts(levels: Iterable[float], threshold: float) -> int:
    return sum(level >= threshold for level in levels)


def audit(inputs: list[tuple[str, Path]]) -> list[str]:
    parsed = [(label, *relative_levels(path)) for label, path in inputs]
    lines = ["satb_relative_chroma_selector: threshold missing extra per_corpus_safe"]
    common_safe = 0
    for threshold in THRESHOLDS:
        recoveries = sum(format_counts(missing, threshold) for _, missing, _ in parsed)
        extras = sum(format_counts(extra, threshold) for _, _, extra in parsed)
        safe = recoveries > 0 and all(format_counts(extra, threshold) == 0 for _, _, extra in parsed)
        common_safe += int(safe)
        per_corpus = " ".join(
            f"{label}={format_counts(missing, threshold)}/{format_counts(extra, threshold)}"
            for label, missing, extra in parsed
        )
        lines.append(
            f"threshold={threshold:.2f} missing={recoveries} extra={extras} safe={int(safe)} {per_corpus}"
        )
    lines.append(
        f"satb_relative_chroma_selector: common_zero_extra_thresholds={common_safe}/{len(THRESHOLDS)} corpora={len(parsed)}"
    )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="LABEL=PATH")
    args = parser.parse_args()
    inputs: list[tuple[str, Path]] = []
    for item in args.input:
        try:
            label, raw_path = item.split("=", 1)
        except ValueError:
            parser.error(f"expected LABEL=PATH, got {item!r}")
        inputs.append((label, Path(raw_path)))
    print("\n".join(audit(inputs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
