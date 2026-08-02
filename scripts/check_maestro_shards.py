#!/usr/bin/env python3
"""Aggregate analyzer_maestro shard summaries and validate the original global gate."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


SUMMARY_RE = re.compile(
    r"^analyzer_maestro: \d+ checks passed "
    r"\(recordings (?P<recordings>\d+)/(?P<total_recordings>\d+), windows (?P<windows>\d+), "
    r"read failures (?P<read_failures>\d+), no-candidate recordings (?P<no_candidate>\d+), "
    r"unusable (?P<unusable>\d+), note hits (?P<note_hits>\d+)/(?P<note_expected>\d+), "
    r"chord hits (?P<chord_hits>\d+)/(?P<chord_checks>\d+), (?P<body>.+)\)$"
)
TP_FP_FN_RE = re.compile(r"\btp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)")
CONTAMINATION_RE = re.compile(
    r"\bcontamination [^,]+ \((?P<contaminated>\d+)/(?P<expected>\d+)\)"
)
FALSE_NON_KEYBOARD_RE = re.compile(
    r"\bfalse non-keyboard windows [^,]+ \((?P<false>\d+)/(?P<windows>\d+)\)"
)


def percent_floor(numerator: int, denominator: int) -> int:
    return numerator * 100 // denominator if denominator > 0 else 0


def fail(message: str) -> None:
    print(f"check_maestro_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_required(pattern: re.Pattern[str], text: str, path: pathlib.Path) -> re.Match[str]:
    match = pattern.search(text)
    if match is None:
        fail(f"{path}: missing {pattern.pattern}")
    return match


def parse_shard(path: pathlib.Path) -> dict[str, int]:
    summary_match: re.Match[str] | None = None
    for line in path.read_text(errors="replace").splitlines():
        match = SUMMARY_RE.match(line)
        if match:
            summary_match = match
    if summary_match is None:
        fail(f"{path}: missing analyzer_maestro pass summary line")

    body = summary_match.group("body")
    if ", keyboard chord precision " not in body:
        fail(f"{path}: missing keyboard chord precision section")
    keyboard_body, chord_tail = body.split(", keyboard chord precision ", 1)
    chord_body = "keyboard chord precision " + chord_tail

    keyboard_counts = parse_required(TP_FP_FN_RE, keyboard_body, path)
    chord_counts = parse_required(TP_FP_FN_RE, chord_body, path)
    contamination = parse_required(CONTAMINATION_RE, keyboard_body, path)
    false_non_keyboard = parse_required(FALSE_NON_KEYBOARD_RE, keyboard_body, path)

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
        "keyboard_tp": int(keyboard_counts.group("tp")),
        "keyboard_fp": int(keyboard_counts.group("fp")),
        "keyboard_fn": int(keyboard_counts.group("fn")),
        "contaminated": int(contamination.group("contaminated")),
        "contamination_expected": int(contamination.group("expected")),
        "false_non_keyboard_windows": int(false_non_keyboard.group("false")),
        "false_non_keyboard_total": int(false_non_keyboard.group("windows")),
        "chord_tp": int(chord_counts.group("tp")),
        "chord_fp": int(chord_counts.group("fp")),
        "chord_fn": int(chord_counts.group("fn")),
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
    recordings = totals.get("recordings", 0)
    windows = totals.get("windows", 0)
    if recordings < args.min_recordings:
        fail(f"expected at least {args.min_recordings} recordings, got {recordings}")
    if windows < args.min_windows:
        fail(f"expected at least {args.min_windows} windows, got {windows}")
    if totals.get("note_expected", 0) <= 0:
        fail("expected at least one piano pitch-class check")

    require_min_pair(
        "piano pitch-class recall",
        totals["note_hits"],
        totals["note_expected"],
        args.min_recall_percent,
    )

    keyboard_precision_total = totals["keyboard_tp"] + totals["keyboard_fp"]
    keyboard_recall_total = totals["keyboard_tp"] + totals["keyboard_fn"]
    if keyboard_precision_total <= 0 or keyboard_recall_total <= 0:
        fail("expected at least one keyboard row precision/recall check")
    require_min_pair(
        "keyboard precision",
        totals["keyboard_tp"],
        keyboard_precision_total,
        args.min_precision_percent,
    )
    require_min_pair(
        "keyboard row recall",
        totals["keyboard_tp"],
        keyboard_recall_total,
        args.min_keyboard_recall_percent,
    )

    contamination_total = totals["contamination_expected"]
    if contamination_total <= 0:
        fail("expected at least one contamination check")
    contamination = percent_floor(totals["contaminated"], contamination_total)
    if contamination > args.max_contamination_percent:
        fail(
            f"expected cross-row contamination <= {args.max_contamination_percent}%, got "
            f"{contamination}% ({totals['contaminated']}/{contamination_total})"
        )

    if totals["false_non_keyboard_total"] != windows:
        fail(
            "false non-keyboard window denominator mismatch "
            f"{totals['false_non_keyboard_total']}/{windows}"
        )
    false_non_keyboard = percent_floor(totals["false_non_keyboard_windows"], windows)
    if false_non_keyboard > args.max_false_non_keyboard_percent:
        fail(
            f"expected false non-keyboard windows <= {args.max_false_non_keyboard_percent}%, got "
            f"{false_non_keyboard}% ({totals['false_non_keyboard_windows']}/{windows})"
        )

    if totals["chord_checks"] >= args.min_chord_checks:
        require_min_pair(
            "piano chord recall",
            totals["chord_hits"],
            totals["chord_checks"],
            args.min_chord_recall_percent,
        )
        chord_precision_total = totals["chord_tp"] + totals["chord_fp"]
        if chord_precision_total <= 0:
            fail("expected at least one keyboard chord prediction")
        require_min_pair(
            "keyboard chord precision",
            totals["chord_tp"],
            chord_precision_total,
            args.min_chord_precision_percent,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-recordings", type=int, required=True)
    parser.add_argument("--min-windows", type=int, required=True)
    parser.add_argument("--min-recall-percent", type=int, required=True)
    parser.add_argument("--min-precision-percent", type=int, required=True)
    parser.add_argument("--min-keyboard-recall-percent", type=int, required=True)
    parser.add_argument("--max-contamination-percent", type=int, required=True)
    parser.add_argument("--max-false-non-keyboard-percent", type=int, required=True)
    parser.add_argument("--min-chord-recall-percent", type=int, required=True)
    parser.add_argument("--min-chord-precision-percent", type=int, required=True)
    parser.add_argument("--min-chord-checks", type=int, required=True)
    args = parser.parse_args()

    totals: dict[str, int] = {}
    for path in args.logs:
        add_summary(totals, parse_shard(path))

    validate(args, totals)
    print(
        "check_maestro_shards: ok "
        f"(recordings {totals['recordings']}/{totals['total_recordings']}, "
        f"windows {totals['windows']}, note hits {totals['note_hits']}/{totals['note_expected']}, "
        f"keyboard precision {totals['keyboard_tp']}/{totals['keyboard_tp'] + totals['keyboard_fp']}, "
        f"keyboard recall {totals['keyboard_tp']}/{totals['keyboard_tp'] + totals['keyboard_fn']}, "
        f"contamination {totals['contaminated']}/{totals['contamination_expected']}, "
        f"false non-keyboard windows {totals['false_non_keyboard_windows']}/{totals['windows']}, "
        f"chord hits {totals['chord_hits']}/{totals['chord_checks']}, "
        f"chord precision {totals['chord_tp']}/{totals['chord_tp'] + totals['chord_fp']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
