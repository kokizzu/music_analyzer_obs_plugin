#!/usr/bin/env python3
"""Aggregate analyzer_egmd shard summaries and validate the original global gate."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


RECORDINGS_RE = re.compile(r"\brecordings (?P<with>\d+)/(?P<total>\d+)")
WINDOWS_RE = re.compile(r"\bwindows (?P<windows>\d+)")
DRUM_HITS_RE = re.compile(r"\bdrum hits (?P<hits>\d+)/(?P<expected>\d+)")
FALSE_WINDOWS_RE = re.compile(r"\bfalse-positive windows [^,]+ \((?P<false>\d+)/(?P<windows>\d+)\)")
TP_FP_FN_RE = re.compile(r"\btp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)")


def percent_floor(numerator: int, denominator: int) -> int:
    return numerator * 100 // denominator if denominator > 0 else 0


def fail(message: str) -> None:
    print(f"check_egmd_shards: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_required(pattern: re.Pattern[str], text: str, path: pathlib.Path) -> re.Match[str]:
    match = pattern.search(text)
    if match is None:
        fail(f"{path}: missing {pattern.pattern}")
    return match


def parse_shard(path: pathlib.Path) -> dict[str, int]:
    summary = ""
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("analyzer_egmd: ") and "drum hits " in line and "tp/fp/fn " in line:
            summary = line
    if not summary:
        fail(f"{path}: missing analyzer_egmd summary line")

    recordings = parse_required(RECORDINGS_RE, summary, path)
    windows = parse_required(WINDOWS_RE, summary, path)
    drum_hits = parse_required(DRUM_HITS_RE, summary, path)
    false_windows = parse_required(FALSE_WINDOWS_RE, summary, path)
    tp_fp_fn = parse_required(TP_FP_FN_RE, summary, path)

    return {
        "recordings": int(recordings.group("with")),
        "total_recordings": int(recordings.group("total")),
        "windows": int(windows.group("windows")),
        "drum_hits": int(drum_hits.group("hits")),
        "drum_expected": int(drum_hits.group("expected")),
        "false_positive_windows": int(false_windows.group("false")),
        "false_positive_window_total": int(false_windows.group("windows")),
        "tp": int(tp_fp_fn.group("tp")),
        "fp": int(tp_fp_fn.group("fp")),
        "fn": int(tp_fp_fn.group("fn")),
    }


def validate(args: argparse.Namespace, totals: dict[str, int]) -> None:
    recordings = totals["recordings"]
    windows = totals["windows"]
    drum_hits = totals["drum_hits"]
    drum_expected = totals["drum_expected"]
    true_positives = totals["tp"]
    false_positives = totals["fp"]
    false_positive_windows = totals["false_positive_windows"]

    if recordings < args.min_recordings:
        fail(f"expected at least {args.min_recordings} recordings, got {recordings}")
    if windows < args.min_windows:
        fail(f"expected at least {args.min_windows} windows, got {windows}")
    if drum_expected <= 0:
        fail("expected at least one drum-category check")
    recall = percent_floor(drum_hits, drum_expected)
    if recall < args.min_recall_percent:
        fail(
            f"expected drum-category recall >= {args.min_recall_percent}%, got "
            f"{recall}% ({drum_hits}/{drum_expected})"
        )
    precision_denominator = true_positives + false_positives
    if precision_denominator <= 0:
        fail("expected at least one predicted drum category")
    precision = percent_floor(true_positives, precision_denominator)
    if precision < args.min_precision_percent:
        fail(
            f"expected drum precision >= {args.min_precision_percent}%, got "
            f"{precision}% ({true_positives}/{precision_denominator})"
        )
    false_window_percent = percent_floor(false_positive_windows, windows)
    if false_window_percent > args.max_false_positive_windows_percent:
        fail(
            f"expected false-positive windows <= {args.max_false_positive_windows_percent}%, got "
            f"{false_window_percent}% ({false_positive_windows}/{windows})"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--min-recordings", type=int, required=True)
    parser.add_argument("--min-windows", type=int, required=True)
    parser.add_argument("--min-recall-percent", type=int, required=True)
    parser.add_argument("--min-precision-percent", type=int, required=True)
    parser.add_argument("--max-false-positive-windows-percent", type=int, required=True)
    args = parser.parse_args()

    totals = {
        "recordings": 0,
        "total_recordings": 0,
        "windows": 0,
        "drum_hits": 0,
        "drum_expected": 0,
        "false_positive_windows": 0,
        "false_positive_window_total": 0,
        "tp": 0,
        "fp": 0,
        "fn": 0,
    }
    for path in args.logs:
        shard = parse_shard(path)
        for key, value in shard.items():
            if key == "total_recordings":
                totals[key] = max(totals[key], value)
            else:
                totals[key] += value

    if totals["false_positive_window_total"] != totals["windows"]:
        fail(
            "false-positive window denominator mismatch "
            f"{totals['false_positive_window_total']}/{totals['windows']}"
        )

    validate(args, totals)
    print(
        "check_egmd_shards: ok "
        f"(recordings {totals['recordings']}/{totals['total_recordings']}, "
        f"windows {totals['windows']}, drum hits {totals['drum_hits']}/{totals['drum_expected']}, "
        f"precision {totals['tp']}/{totals['tp'] + totals['fp']}, "
        f"false-positive windows {totals['false_positive_windows']}/{totals['windows']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
