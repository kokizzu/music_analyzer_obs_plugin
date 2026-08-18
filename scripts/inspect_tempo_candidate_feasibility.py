#!/usr/bin/env python3
"""Measure whether a simple meter or bass-grid selector can recover labelled BPM.

This is diagnostic-only.  It deliberately never changes the analyzer: a source
feature is eligible for implementation only when it can promote labelled
candidates in both the rhythm-heavy and bass-led validation logs.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
from dataclasses import dataclass


CANDIDATE_RE = re.compile(
    r"(?P<bpm>\d+)\(s=(?P<score>[0-9.]+).*?m=(?P<meter>[0-9.]+)"
    r"(?:,rep=(?P<recurrence>[0-9.]+)/[0-9.]+/[0-9.]+)?.*?"
    r"align=(?P<kick>[0-9.]+)/(?P<bass>[0-9.]+)/(?P<snare>[0-9.]+)/(?P<tonal>[0-9.]+)"
    r"(?:,kb=(?P<kick_bass>[0-9.]+))?\)"
)


@dataclass(frozen=True)
class Candidate:
    bpm: int
    score: float
    meter: float
    recurrence: float
    kick_alignment: float
    bass_alignment: float
    kick_bass_alignment: float


@dataclass(frozen=True)
class Row:
    expected: float
    candidates: tuple[Candidate, ...]


def near(value: float, target: float, tolerance: float) -> bool:
    return math.isfinite(value) and abs(value - target) <= tolerance


def parse_rows(path: pathlib.Path, prefix: str) -> list[Row]:
    rows: list[Row] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        fields = dict(field.split("=", 1) for field in line[len(prefix) :].split("\t") if "=" in field)
        candidates = tuple(
            Candidate(
                bpm=int(match.group("bpm")),
                score=float(match.group("score")),
                meter=float(match.group("meter")),
                recurrence=float(match.group("recurrence") or 0.0),
                kick_alignment=float(match.group("kick")) / 100.0,
                bass_alignment=float(match.group("bass")) / 100.0,
                kick_bass_alignment=float(match.group("kick_bass") or 0.0) / 100.0,
            )
            for match in CANDIDATE_RE.finditer(fields.get("candidates", ""))
        )
        if candidates:
            rows.append(Row(expected=float(fields.get("expected", "0") or 0.0), candidates=candidates))
    return rows


def select(candidates: tuple[Candidate, ...], feature: str, weight: float) -> Candidate:
    return max(candidates, key=lambda candidate: candidate.score * (1.0 + weight * getattr(candidate, feature)))


def select_pair(
    candidates: tuple[Candidate, ...], first_feature: str, first_weight: float,
    second_feature: str, second_weight: float,
) -> Candidate:
    """Apply two bounded diagnostic signals without inventing a new score scale."""
    return max(
        candidates,
        key=lambda candidate: candidate.score
        * (1.0 + first_weight * getattr(candidate, first_feature))
        * (1.0 + second_weight * getattr(candidate, second_feature)),
    )


def labelled(rows: list[Row], tolerance: float) -> list[tuple[Row, Candidate]]:
    return [
        (row, expected)
        for row in rows
        if (expected := next((candidate for candidate in row.candidates if near(candidate.bpm, row.expected, tolerance)), None))
        is not None
    ]


def hits(rows: list[tuple[Row, Candidate]], tolerance: float, selector) -> int:
    return sum(near(selector(row.candidates).bpm, row.expected, tolerance) for row, _ in rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=pathlib.Path)
    parser.add_argument("--comparison-log", type=pathlib.Path)
    parser.add_argument("--prefix", default="MAESTRO tempo diag\t")
    parser.add_argument("--tolerance", type=float, default=8.0)
    args = parser.parse_args()

    rows = parse_rows(args.log, args.prefix)
    eligible = labelled(rows, args.tolerance)
    if not eligible:
        print("tempo candidate feasibility: no labelled candidates")
        return 0

    baseline = sum(near(select(row.candidates, "meter", 0.0).bpm, row.expected, args.tolerance) for row, _ in eligible)
    meter_advantage = sum(
        expected.meter > select(row.candidates, "meter", 0.0).meter + 0.01
        for row, expected in eligible
    )
    bass_advantage = sum(
        expected.bass_alignment > select(row.candidates, "meter", 0.0).bass_alignment + 0.01
        for row, expected in eligible
    )
    print(
        "tempo candidate feasibility: "
        f"labelled {len(eligible)}/{len(rows)}, score-only {baseline}/{len(eligible)}, "
        f"expected meter>score-best {meter_advantage}/{len(eligible)}, "
        f"expected bass-align>score-best {bass_advantage}/{len(eligible)}"
    )
    for feature, label in (("meter", "meter"), ("bass_alignment", "bass alignment"),
                           ("kick_alignment", "kick alignment"),
                           ("kick_bass_alignment", "kick+bass alignment"),
                           ("recurrence", "recurrence")):
        parts = []
        for weight in (0.25, 0.5, 1.0, 2.0, 4.0):
            hit_count = sum(near(select(row.candidates, feature, weight).bpm, row.expected, args.tolerance) for row, _ in eligible)
            parts.append(f"w={weight:g}:{hit_count}/{len(eligible)}")
        print(f"tempo candidate feasibility: {label} selector " + " ".join(parts))

    if args.comparison_log is not None:
        comparison = labelled(parse_rows(args.comparison_log, args.prefix), args.tolerance)
        if not comparison:
            print("tempo candidate feasibility: combined shared selector has no comparison labels")
            return 0
        comparison_baseline = hits(comparison, args.tolerance, lambda candidates: select(candidates, "meter", 0.0))
        features = ("meter", "bass_alignment", "kick_alignment", "kick_bass_alignment", "recurrence")
        weights = (0.25, 0.5, 1.0, 2.0, 4.0)
        choices = []
        for first_index, first_feature in enumerate(features):
            for second_feature in features[first_index + 1 :]:
                for first_weight in weights:
                    for second_weight in weights:
                        selector = lambda candidates, a=first_feature, aw=first_weight, b=second_feature, bw=second_weight: select_pair(candidates, a, aw, b, bw)
                        primary_hits = hits(eligible, args.tolerance, selector)
                        comparison_hits = hits(comparison, args.tolerance, selector)
                        choices.append((primary_hits, comparison_hits, first_feature, first_weight, second_feature, second_weight))
        best = max(
            choices,
            key=lambda item: (
                min(item[0] - baseline, item[1] - comparison_baseline),
                item[0] + item[1],
            ),
        )
        primary_hits, comparison_hits, first_feature, first_weight, second_feature, second_weight = best
        print(
            "tempo candidate feasibility: combined shared selector "
            f"{first_feature}@{first_weight:g}+{second_feature}@{second_weight:g} "
            f"primary {primary_hits}/{len(eligible)} comparison {comparison_hits}/{len(comparison)} "
            f"baseline {baseline}/{len(eligible)} and {comparison_baseline}/{len(comparison)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
