#!/usr/bin/env python3
"""Aggregate analyzer_musicnet shard summaries and validate global gates."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


SUMMARY_RE = re.compile(
    r"^analyzer_musicnet: \d+ checks passed "
    r"\(recordings (?P<recordings>\d+)/(?P<total_recordings>\d+), windows (?P<windows>\d+), "
    r"read failures (?P<read_failures>\d+), no-candidate recordings (?P<no_candidate>\d+), "
    r"unusable (?P<unusable>\d+), note hits (?P<note_hits>\d+)/(?P<note_expected>\d+), "
    r"chord hits (?P<chord_hits>\d+)/(?P<chord_checks>\d+), (?P<body>.+)\)$"
)
SIMPLE_CHORD_HITS_RE = re.compile(r"\bsimple chord hits (?P<hits>\d+)/(?P<checks>\d+)")
TP_FP_FN_RE = re.compile(r"\btp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)")


def percent_floor(numerator: int, denominator: int) -> int:
    return numerator * 100 // denominator if denominator > 0 else 0


def fail(message: str) -> None:
    print(f"check_musicnet_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_shard(path: pathlib.Path) -> dict[str, int]:
    summary_match: re.Match[str] | None = None
    for line in path.read_text(errors="replace").splitlines():
        match = SUMMARY_RE.match(line)
        if match:
            summary_match = match
    if summary_match is None:
        fail(f"{path}: missing analyzer_musicnet pass summary line")

    body = summary_match.group("body")
    simple_chord_hits = SIMPLE_CHORD_HITS_RE.search(body)
    if simple_chord_hits is None:
        fail(f"{path}: missing simple chord hit summary")

    counts = list(TP_FP_FN_RE.finditer(body))
    if len(counts) < 3:
        fail(f"{path}: missing pitch/simplified/global tp/fp/fn summaries")
    pitch_counts = counts[0]
    simplified_chord_counts = counts[1]
    global_chord_counts = counts[2]

    return {
        "recordings": int(summary_match.group("recordings")),
        "total_recordings": int(summary_match.group("total_recordings")),
        "windows": int(summary_match.group("windows")),
        "read_failures": int(summary_match.group("read_failures")),
        "no_candidate": int(summary_match.group("no_candidate")),
        "unusable": int(summary_match.group("unusable")),
        "note_hits": int(summary_match.group("note_hits")),
        "note_expected": int(summary_match.group("note_expected")),
        "chord_hits": int(summary_match.group("chord_hits")),
        "chord_checks": int(summary_match.group("chord_checks")),
        "simple_chord_hits": int(simple_chord_hits.group("hits")),
        "simple_chord_checks": int(simple_chord_hits.group("checks")),
        "pitch_tp": int(pitch_counts.group("tp")),
        "pitch_fp": int(pitch_counts.group("fp")),
        "pitch_fn": int(pitch_counts.group("fn")),
        "simplified_chord_tp": int(simplified_chord_counts.group("tp")),
        "simplified_chord_fp": int(simplified_chord_counts.group("fp")),
        "simplified_chord_fn": int(simplified_chord_counts.group("fn")),
        "global_chord_tp": int(global_chord_counts.group("tp")),
        "global_chord_fp": int(global_chord_counts.group("fp")),
        "global_chord_fn": int(global_chord_counts.group("fn")),
    }


def add_summary(total: dict[str, int], part: dict[str, int]) -> None:
    for key, value in part.items():
        if key == "total_recordings":
            total[key] = max(total.get(key, 0), value)
        else:
            total[key] = total.get(key, 0) + value


def require_min_pair(label: str, hit: int, total: int, min_percent: int) -> None:
    actual = percent_floor(hit, total)
    if actual < min_percent:
        fail(f"expected {label} >= {min_percent}%, got {actual}% ({hit}/{total})")


def validate(args: argparse.Namespace, totals: dict[str, int]) -> None:
    if totals.get("recordings", 0) < args.min_recordings:
        fail(f"expected at least {args.min_recordings} recordings, got {totals.get('recordings', 0)}")
    if totals.get("windows", 0) < args.min_windows:
        fail(f"expected at least {args.min_windows} windows, got {totals.get('windows', 0)}")
    if totals.get("note_expected", 0) <= 0:
        fail("expected at least one pitch-class check")

    require_min_pair(
        "pitch-class recall",
        totals["note_hits"],
        totals["note_expected"],
        args.min_recall_percent,
    )

    pitch_precision_total = totals["pitch_tp"] + totals["pitch_fp"]
    if pitch_precision_total <= 0:
        fail("expected at least one predicted pitch class")
    require_min_pair(
        "pitch precision",
        totals["pitch_tp"],
        pitch_precision_total,
        args.min_precision_percent,
    )

    if totals["simple_chord_checks"] != totals["chord_checks"]:
        fail(
            "simple chord denominator mismatch "
            f"{totals['simple_chord_checks']}/{totals['chord_checks']}"
        )

    if totals["chord_checks"] >= args.min_chord_checks:
        require_min_pair(
            "chord recall",
            totals["chord_hits"],
            totals["chord_checks"],
            args.min_chord_recall_percent,
        )
        if args.min_simple_chord_recall_percent > 0:
            require_min_pair(
                "simplified chord recall",
                totals["simple_chord_hits"],
                totals["chord_checks"],
                args.min_simple_chord_recall_percent,
            )
        if args.min_global_simple_chord_precision_percent > 0:
            require_min_pair(
                "simplified global chord precision",
                totals["simplified_chord_tp"],
                totals["simplified_chord_tp"] + totals["simplified_chord_fp"],
                args.min_global_simple_chord_precision_percent,
            )
        if args.min_global_simple_chord_recall_percent > 0:
            require_min_pair(
                "simplified global chord recall",
                totals["simplified_chord_tp"],
                totals["simplified_chord_tp"] + totals["simplified_chord_fn"],
                args.min_global_simple_chord_recall_percent,
            )
        require_min_pair(
            "global chord precision",
            totals["global_chord_tp"],
            totals["global_chord_tp"] + totals["global_chord_fp"],
            args.min_global_chord_precision_percent,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-recordings", type=int, required=True)
    parser.add_argument("--min-windows", type=int, required=True)
    parser.add_argument("--min-recall-percent", type=int, required=True)
    parser.add_argument("--min-precision-percent", type=int, required=True)
    parser.add_argument("--min-chord-recall-percent", type=int, required=True)
    parser.add_argument("--min-simple-chord-recall-percent", type=int, required=True)
    parser.add_argument("--min-global-chord-precision-percent", type=int, required=True)
    parser.add_argument("--min-global-simple-chord-precision-percent", type=int, required=True)
    parser.add_argument("--min-global-simple-chord-recall-percent", type=int, required=True)
    parser.add_argument("--min-chord-checks", type=int, required=True)
    args = parser.parse_args()

    totals: dict[str, int] = {}
    for path in args.logs:
        add_summary(totals, parse_shard(path))

    validate(args, totals)
    print(
        "check_musicnet_shards: ok "
        f"(recordings {totals['recordings']}/{totals['total_recordings']}, "
        f"windows {totals['windows']}, note hits {totals['note_hits']}/{totals['note_expected']}, "
        f"pitch precision {totals['pitch_tp']}/{totals['pitch_tp'] + totals['pitch_fp']}, "
        f"chord hits {totals['chord_hits']}/{totals['chord_checks']}, "
        f"simple chord hits {totals['simple_chord_hits']}/{totals['chord_checks']}, "
        f"simplified chord precision {totals['simplified_chord_tp']}/"
        f"{totals['simplified_chord_tp'] + totals['simplified_chord_fp']}, "
        f"global chord precision {totals['global_chord_tp']}/"
        f"{totals['global_chord_tp'] + totals['global_chord_fp']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
