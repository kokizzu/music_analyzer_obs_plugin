#!/usr/bin/env python3
"""Aggregate analyzer_guitarset shards and validate full-population thresholds."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


SUMMARY_RE = re.compile(
    r"^analyzer_guitarset: \d+ checks passed "
    r"\(excerpts (?P<excerpts>\d+)/(?:\d+), windows (?P<windows>\d+)(?:/\d+)?, "
    r"read failures (?P<read_failures>\d+), .*?note hits (?P<note_hits>\d+)/(?P<note_total>\d+), "
    r"chord hits (?P<chord_hits>\d+)/(?P<chord_total>\d+), (?P<body>.+)\)$"
)
PAIR_PATTERNS = {
    "primary": re.compile(r"\bprimary chord hits (?P<hit>\d+)/(?P<total>\d+)"),
    "major_minor": re.compile(r"\bmajor/minor chord hits (?P<hit>\d+)/(?P<total>\d+)"),
    "other": re.compile(r"\bother chord hits (?P<hit>\d+)/(?P<total>\d+)"),
    "simple": re.compile(r"\bsimple chord hits (?P<hit>\d+)/(?P<total>\d+)"),
    "simple_major_minor": re.compile(r"\bsimple major/minor hits (?P<hit>\d+)/(?P<total>\d+)"),
    "simple_other": re.compile(r"\bsimple other hits (?P<hit>\d+)/(?P<total>\d+)"),
}
GUITAR_PRECISION_RE = re.compile(
    r"\bguitar precision [^,]+, guitar recall [^,]+, F1 [^,]+, "
    r"contamination (?P<contamination>[0-9.]+)%, "
    r"false vocal windows (?P<false_vocal>[0-9.]+)%, "
    r"ambiguous (?P<ambiguous>\d+)/(?P<expected_pitch_classes>\d+), "
    r"row leaks bass/keys/vocal/other (?P<leaks>[0-9/]+), "
    r"tp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)"
)
CHORD_PRECISION_RE = re.compile(
    r"\bguitar chord precision [^,]+, guitar chord recall [^,]+, F1 [^,]+, "
    r"tp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)"
)


def percent(hit: int, total: int) -> int:
    return hit * 100 // total if total > 0 else 0


def fail(message: str) -> None:
    print(f"check_guitarset_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_pair(body: str, name: str) -> tuple[int, int]:
    match = PAIR_PATTERNS[name].search(body)
    if not match:
        return 0, 0
    return int(match.group("hit")), int(match.group("total"))


def empty_summary() -> dict[str, float]:
    return {
        "excerpts": 0,
        "windows": 0,
        "read_failures": 0,
        "note_hits": 0,
        "note_total": 0,
        "chord_hits": 0,
        "chord_total": 0,
        "primary_hits": 0,
        "primary_total": 0,
        "major_minor_hits": 0,
        "major_minor_total": 0,
        "other_hits": 0,
        "other_total": 0,
        "simple_hits": 0,
        "simple_total": 0,
        "simple_major_minor_hits": 0,
        "simple_major_minor_total": 0,
        "simple_other_hits": 0,
        "simple_other_total": 0,
        "guitar_tp": 0,
        "guitar_fp": 0,
        "guitar_fn": 0,
        "chord_tp": 0,
        "chord_fp": 0,
        "chord_fn": 0,
        "max_contamination_percent": 0.0,
        "max_false_vocal_percent": 0.0,
    }


def parse_shard(path: pathlib.Path) -> dict[str, float]:
    summary = empty_summary()
    saw_summary = False
    for line in path.read_text(errors="replace").splitlines():
        match = SUMMARY_RE.match(line)
        if not match:
            continue
        saw_summary = True
        body = match.group("body")
        for key in ("excerpts", "windows", "read_failures", "note_hits", "note_total",
                    "chord_hits", "chord_total"):
            summary[key] += int(match.group(key))

        for name, prefix in (
            ("primary", "primary"),
            ("major_minor", "major_minor"),
            ("other", "other"),
            ("simple", "simple"),
            ("simple_major_minor", "simple_major_minor"),
            ("simple_other", "simple_other"),
        ):
            hit, total = parse_pair(body, name)
            summary[f"{prefix}_hits"] += hit
            summary[f"{prefix}_total"] += total

        guitar_match = GUITAR_PRECISION_RE.search(body)
        if not guitar_match:
            fail(f"missing guitar precision summary in {path}: {line}")
        summary["guitar_tp"] += int(guitar_match.group("tp"))
        summary["guitar_fp"] += int(guitar_match.group("fp"))
        summary["guitar_fn"] += int(guitar_match.group("fn"))
        summary["max_contamination_percent"] = max(
            summary["max_contamination_percent"], float(guitar_match.group("contamination"))
        )
        summary["max_false_vocal_percent"] = max(
            summary["max_false_vocal_percent"], float(guitar_match.group("false_vocal"))
        )

        chord_match = CHORD_PRECISION_RE.search(body)
        if not chord_match:
            fail(f"missing guitar chord precision summary in {path}: {line}")
        summary["chord_tp"] += int(chord_match.group("tp"))
        summary["chord_fp"] += int(chord_match.group("fp"))
        summary["chord_fn"] += int(chord_match.group("fn"))

    if not saw_summary:
        fail(f"missing analyzer_guitarset pass summary in {path}")
    return summary


def add_summary(total: dict[str, float], part: dict[str, float]) -> None:
    for key, value in part.items():
        if key in {"max_contamination_percent", "max_false_vocal_percent"}:
            continue
        total[key] = total.get(key, 0) + value
    total["max_contamination_percent"] = max(
        total.get("max_contamination_percent", 0.0),
        part.get("max_contamination_percent", 0.0),
    )
    total["max_false_vocal_percent"] = max(
        total.get("max_false_vocal_percent", 0.0),
        part.get("max_false_vocal_percent", 0.0),
    )


def require_min_pair(label: str, hit: int, total: int, min_percent: int) -> None:
    if min_percent <= 0:
        return
    actual = percent(hit, total)
    if actual < min_percent:
        fail(f"expected {label} >= {min_percent}%, got {actual}% ({hit}/{total})")


def validate(args: argparse.Namespace, summary: dict[str, float]) -> None:
    excerpts = int(summary["excerpts"])
    windows = int(summary["windows"])
    if excerpts < args.required_excerpts:
        fail(f"expected at least {args.required_excerpts} excerpts, got {excerpts}")
    if windows < args.required_windows:
        fail(f"expected at least {args.required_windows} windows, got {windows}")
    if int(summary["read_failures"]) != 0:
        fail(f"expected 0 read failures, got {int(summary['read_failures'])}")

    require_min_pair("pitch-class recall", int(summary["note_hits"]), int(summary["note_total"]),
                     args.min_recall_percent)
    require_min_pair("guitar row recall", int(summary["guitar_tp"]),
                     int(summary["guitar_tp"] + summary["guitar_fn"]),
                     args.min_guitar_recall_percent)
    require_min_pair("guitar precision", int(summary["guitar_tp"]),
                     int(summary["guitar_tp"] + summary["guitar_fp"]),
                     args.min_precision_percent)

    if summary["max_contamination_percent"] > args.max_contamination_percent:
        fail(
            "expected max shard contamination <= "
            f"{args.max_contamination_percent}%, got {summary['max_contamination_percent']:.2f}%"
        )
    if summary["max_false_vocal_percent"] > args.max_false_vocal_percent:
        fail(
            "expected max shard false vocal windows <= "
            f"{args.max_false_vocal_percent}%, got {summary['max_false_vocal_percent']:.2f}%"
        )

    chord_total = int(summary["chord_total"])
    if args.min_chord_checks > 0 and chord_total < args.min_chord_checks:
        fail(f"expected at least {args.min_chord_checks} chord-checkable windows, got {chord_total}")
    if args.min_chord_checks > 0:
        require_min_pair("chord recall", int(summary["chord_hits"]), chord_total,
                         args.min_chord_recall_percent)
    if args.min_chord_hits > 0 and int(summary["chord_hits"]) < args.min_chord_hits:
        fail(f"expected at least {args.min_chord_hits} chord hits, got {int(summary['chord_hits'])}")
    if args.min_primary_chord_hits > 0 and int(summary["primary_hits"]) < args.min_primary_chord_hits:
        fail(
            "expected at least "
            f"{args.min_primary_chord_hits} primary chord hits, got {int(summary['primary_hits'])}"
        )
    if args.min_chord_checks > 0:
        require_min_pair("guitar chord precision", int(summary["chord_tp"]),
                         int(summary["chord_tp"] + summary["chord_fp"]),
                         args.min_chord_precision_percent)

    require_min_pair("major/minor chord recall", int(summary["major_minor_hits"]),
                     int(summary["major_minor_total"]), args.min_major_minor_chord_recall_percent)
    require_min_pair("other chord recall", int(summary["other_hits"]), int(summary["other_total"]),
                     args.min_other_chord_recall_percent)
    require_min_pair("simplified chord recall", int(summary["simple_hits"]),
                     int(summary["simple_total"]), args.min_simple_chord_recall_percent)
    require_min_pair("simplified major/minor chord recall",
                     int(summary["simple_major_minor_hits"]),
                     int(summary["simple_major_minor_total"]),
                     args.min_simple_major_minor_chord_recall_percent)
    require_min_pair("simplified other chord recall", int(summary["simple_other_hits"]),
                     int(summary["simple_other_total"]),
                     args.min_simple_other_chord_recall_percent)

    if args.max_single_note_chord_false_percent >= 0 and chord_total == 0:
        predicted = int(summary["chord_tp"] + summary["chord_fp"])
        actual = percent(predicted, windows)
        if actual > args.max_single_note_chord_false_percent:
            fail(
                "expected single-note chord false positives <= "
                f"{args.max_single_note_chord_false_percent}%, got {actual}% ({predicted}/{windows})"
            )
    if args.max_single_note_chord_false_count >= 0 and chord_total == 0:
        predicted = int(summary["chord_tp"] + summary["chord_fp"])
        if predicted > args.max_single_note_chord_false_count:
            fail(
                "expected single-note chord false positives <= "
                f"{args.max_single_note_chord_false_count}, got {predicted}/{windows}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--required-excerpts", type=int, default=20)
    parser.add_argument("--required-windows", type=int, default=80)
    parser.add_argument("--min-recall-percent", type=int, default=45)
    parser.add_argument("--min-precision-percent", type=int, default=90)
    parser.add_argument("--min-guitar-recall-percent", type=int, default=90)
    parser.add_argument("--max-contamination-percent", type=float, default=5.0)
    parser.add_argument("--max-false-vocal-percent", type=float, default=5.0)
    parser.add_argument("--min-chord-checks", type=int, default=5)
    parser.add_argument("--min-chord-recall-percent", type=int, default=30)
    parser.add_argument("--min-chord-hits", type=int, default=0)
    parser.add_argument("--min-primary-chord-hits", type=int, default=0)
    parser.add_argument("--min-chord-precision-percent", type=int, default=85)
    parser.add_argument("--min-major-minor-chord-recall-percent", type=int, default=0)
    parser.add_argument("--min-other-chord-recall-percent", type=int, default=0)
    parser.add_argument("--min-simple-chord-recall-percent", type=int, default=0)
    parser.add_argument("--min-simple-major-minor-chord-recall-percent", type=int, default=0)
    parser.add_argument("--min-simple-other-chord-recall-percent", type=int, default=0)
    parser.add_argument("--max-single-note-chord-false-percent", type=int, default=-1)
    parser.add_argument("--max-single-note-chord-false-count", type=int, default=-1)
    args = parser.parse_args()

    summary = empty_summary()
    summary["max_contamination_percent"] = 0.0
    summary["max_false_vocal_percent"] = 0.0
    for path in args.logs:
        add_summary(summary, parse_shard(path))
    validate(args, summary)

    print(
        "check_guitarset_shards: ok "
        f"(excerpts {int(summary['excerpts'])}, windows {int(summary['windows'])}, "
        f"note hits {int(summary['note_hits'])}/{int(summary['note_total'])}, "
        f"chord hits {int(summary['chord_hits'])}/{int(summary['chord_total'])}, "
        f"primary chord hits {int(summary['primary_hits'])}/{int(summary['primary_total'])}, "
        f"guitar tp/fp/fn {int(summary['guitar_tp'])}/{int(summary['guitar_fp'])}/"
        f"{int(summary['guitar_fn'])}, chord tp/fp/fn {int(summary['chord_tp'])}/"
        f"{int(summary['chord_fp'])}/{int(summary['chord_fn'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
