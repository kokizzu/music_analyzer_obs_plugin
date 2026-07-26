#!/usr/bin/env python3
"""Summarize analyzer_drum_samples active/primary matrices."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import Counter


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
MATRIX_RE = re.compile(r"^analyzer_drum_samples: (?P<kind>active|primary) matrix$")
ROW_RE = re.compile(r"^\s*expected\s+(?P<expected>\w+)\s+(?P<counts>.+)$")


def parse_matrix_text(text: str) -> dict[str, dict[str, dict[str, int]]]:
    matrices: dict[str, dict[str, dict[str, int]]] = {"active": {}, "primary": {}}
    current: str | None = None
    for line in text.splitlines():
        matrix_match = MATRIX_RE.match(line)
        if matrix_match:
            current = matrix_match.group("kind")
            continue
        row_match = ROW_RE.match(line)
        if current is None or not row_match:
            continue
        counts: dict[str, int] = {}
        for token in row_match.group("counts").split():
            if "=" not in token:
                continue
            label, value = token.split("=", 1)
            try:
                counts[label] = int(value)
            except ValueError:
                continue
        matrices[current][row_match.group("expected")] = counts
    return matrices


def top_misses(expected: str, counts: dict[str, int]) -> str:
    misses = [
        (label, value)
        for label, value in counts.items()
        if label != expected and value > 0
    ]
    if not misses:
        return "--"
    return " ".join(
        f"{label}={value}"
        for label, value in sorted(misses, key=lambda item: (-item[1], item[0]))[:4]
    )


def print_kind_summary(kind: str, matrix: dict[str, dict[str, int]]) -> None:
    total_rows = sum(sum(counts.values()) for counts in matrix.values())
    print(f"{kind} matrix rows={len(matrix)} events={total_rows}")
    detected_totals: Counter[str] = Counter()
    for counts in matrix.values():
        detected_totals.update(counts)
    if detected_totals:
        totals = " ".join(
            f"{label}={detected_totals[label]}"
            for label in sorted(detected_totals)
            if detected_totals[label] > 0
        )
        print(f"{kind} totals {totals}")
    for expected in CATEGORIES:
        counts = matrix.get(expected)
        if not counts:
            continue
        total = sum(counts.values())
        hit = counts.get(expected, 0)
        off_target = total - hit
        hit_share = 100.0 * hit / total if total else 0.0
        print(
            f"{kind} expected {expected}: hit={hit}/{total} "
            f"hit_share={hit_share:.2f}% off_target={off_target} "
            f"top_off_target={top_misses(expected, counts)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=pathlib.Path)
    args = parser.parse_args()

    matrices = parse_matrix_text(args.log.read_text(errors="replace"))
    print(f"drum gate matrix log: {args.log}")
    for kind in ("active", "primary"):
        print_kind_summary(kind, matrices[kind])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
