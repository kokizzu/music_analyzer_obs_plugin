#!/usr/bin/env python3
"""Summarize analyzer_egmd tempo diagnostics.

The input is stderr from analyzer_egmd with MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
from collections import Counter
from dataclasses import dataclass


DEFAULT_DIAG_PREFIX = "E-GMD tempo diag\t"
CANDIDATE_RE = re.compile(r"(?P<bpm>\d+)\(s=(?P<score>[0-9.]+)")
CANDIDATE_ALIGNMENT_RE = re.compile(
    r"(?P<bpm>\d+)\([^)]*?align="
    r"(?P<kick>[0-9.]+)/(?P<bass>[0-9.]+)/(?P<snare>[0-9.]+)/(?P<tonal>[0-9.]+)\)"
)


@dataclass(frozen=True)
class TempoRow:
    source: pathlib.Path
    recording_id: str
    expected: float
    got: float
    confidence: float
    error: float
    status: str
    candidates: str


@dataclass(frozen=True)
class CandidatePhaseAlignment:
    bpm: int
    kick: float
    bass: float
    snare: float
    tonal: float


def parse_key_values(line: str, prefix: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in line[len(prefix) :].split("\t"):
        key, separator, value = field.partition("=")
        if separator:
            values[key] = value
    return values


def parse_rows(path: pathlib.Path, prefix: str) -> list[TempoRow]:
    rows: list[TempoRow] = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        values = parse_key_values(line, prefix)
        rows.append(
            TempoRow(
                source=path,
                recording_id=values.get("id", "-"),
                expected=float(values.get("expected", "0") or 0.0),
                got=float(values.get("got", "0") or 0.0),
                confidence=float(values.get("confidence", "0") or 0.0),
                error=float(values.get("error", "0") or 0.0),
                status=values.get("status", "-"),
                candidates=values.get("candidates", "-"),
            )
        )
    return rows


def candidate_bpms(row: TempoRow) -> list[int]:
    return [int(match.group("bpm")) for match in CANDIDATE_RE.finditer(row.candidates)]


def candidate_phase_alignments(row: TempoRow) -> list[CandidatePhaseAlignment]:
    return [
        CandidatePhaseAlignment(
            bpm=int(match.group("bpm")),
            kick=float(match.group("kick")) / 100.0,
            bass=float(match.group("bass")) / 100.0,
            snare=float(match.group("snare")) / 100.0,
            tonal=float(match.group("tonal")) / 100.0,
        )
        for match in CANDIDATE_ALIGNMENT_RE.finditer(row.candidates)
    ]


def near(value: float, target: float, tolerance: float) -> bool:
    return value > 0.0 and math.isfinite(value) and abs(value - target) <= tolerance


def miss_class(row: TempoRow, tolerance: float) -> str:
    if row.got <= 0.0:
        return "no-estimate"
    if near(row.got, row.expected, tolerance):
        return "hit"
    ratios = (
        ("half-time", 0.5),
        ("double-time", 2.0),
        ("two-thirds", 2.0 / 3.0),
        ("three-halves", 1.5),
        ("three-quarters", 0.75),
        ("four-thirds", 4.0 / 3.0),
    )
    for label, ratio in ratios:
        if near(row.got, row.expected * ratio, tolerance):
            return label
    return "other"


def expected_candidate_rank(row: TempoRow, tolerance: float) -> int:
    for index, bpm in enumerate(candidate_bpms(row), start=1):
        if near(float(bpm), row.expected, tolerance):
            return index
    return 0


def percent(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{numerator * 100.0 / denominator:.1f}%"


def print_phase_alignment_summary(rows: list[TempoRow], tolerance: float) -> None:
    """Compare source-grid energy for a labelled candidate versus the selected one.

    This is intentionally diagnostic-only. It reports whether a source-energy
    selector would have evidence to replace the current top candidate; it does
    not alter the BPM estimate merely because an alternative happens to align
    more energy in one corpus row.
    """
    sources = ("kick", "bass", "snare", "tonal")
    outcomes = {source: Counter() for source in sources}
    eligible = 0
    aligned_rows = 0
    for row in rows:
        candidates = candidate_phase_alignments(row)
        if not candidates:
            continue
        aligned_rows += 1
        expected = next((candidate for candidate in candidates if near(candidate.bpm, row.expected, tolerance)), None)
        if expected is None:
            continue
        eligible += 1
        selected = candidates[0]
        for source in sources:
            difference = getattr(expected, source) - getattr(selected, source)
            outcomes[source]["higher" if difference > 0.01 else "lower" if difference < -0.01 else "equal"] += 1

    if not aligned_rows:
        return
    parts = []
    for source in sources:
        parts.append(
            f"{source} expected>selected {outcomes[source]['higher']}/{eligible}, "
            f"equal {outcomes[source]['equal']}/{eligible}, lower {outcomes[source]['lower']}/{eligible}"
        )
    print(
        "tempo phase-energy alignment: "
        f"candidate diagnostics {aligned_rows}/{len(rows)}, expected candidate available {eligible}/{len(rows)}; "
        + "; ".join(parts)
    )


def print_summary(rows: list[TempoRow], tolerance: float, worst: int) -> None:
    if not rows:
        print("tempo diagnostics: no rows found")
        return

    classes = Counter(miss_class(row, tolerance) for row in rows)
    ranks = Counter(expected_candidate_rank(row, tolerance) for row in rows)
    errors = [row.error for row in rows]
    hits = classes["hit"]
    no_estimate = classes["no-estimate"]
    mean_error = sum(errors) / len(errors)
    max_error = max(errors)
    expected_values = {round(row.expected, 2) for row in rows}

    print(
        "tempo diagnostics: "
        f"rows {len(rows)}, hits {hits}/{len(rows)} ({percent(hits, len(rows))}), "
        f"no-estimate {no_estimate}, mean abs error {mean_error:.2f}, max abs error {max_error:.2f}"
    )
    if expected_values == {120.0}:
        print(
            "tempo diagnostics warning: every expected BPM is 120.00; for generated "
            "annotation MIDI this can be a timestamp encoding value rather than real tempo ground truth"
        )
    print(
        "tempo miss classes: "
        + ", ".join(f"{name} {count}" for name, count in classes.most_common())
    )

    rank_parts = []
    for rank in range(1, 6):
        rank_parts.append(f"rank{rank} {ranks[rank]}")
    rank_parts.append(f"missing {ranks[0]}")
    print("expected BPM in top candidates: " + ", ".join(rank_parts))
    print_phase_alignment_summary(rows, tolerance)

    misses = [row for row in rows if miss_class(row, tolerance) != "hit"]
    misses.sort(key=lambda row: (row.error, -row.confidence), reverse=True)
    if misses:
        print("worst tempo misses:")
        for row in misses[:worst]:
            rank = expected_candidate_rank(row, tolerance)
            rank_text = f"rank{rank}" if rank > 0 else "missing"
            print(
                f"  {row.recording_id}: expected {row.expected:.2f}, got {row.got:.2f}, "
                f"conf {row.confidence:.3f}, error {row.error:.2f}, "
                f"class {miss_class(row, tolerance)}, expected-candidate {rank_text}, "
                f"candidates {row.candidates}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--worst", type=int, default=12)
    parser.add_argument("--prefix", default=DEFAULT_DIAG_PREFIX)
    args = parser.parse_args()

    rows: list[TempoRow] = []
    for path in args.logs:
        rows.extend(parse_rows(path, args.prefix))
    print_summary(rows, args.tolerance, args.worst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
