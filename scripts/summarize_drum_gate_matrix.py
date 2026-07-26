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
OK_RE = re.compile(r"^analyzer_drum_samples: ok \((?P<body>.+)\)$")
SAMPLE_RE = re.compile(
    r"(?P<label>kick|snare|hihat|crash|tom|ride|rim) "
    r"recall (?P<recall_hit>\d+)/(?P<recall_total>\d+) "
    r"primary (?P<primary_hit>\d+)/(?P<primary_total>\d+) "
    r"precision (?P<precision_hit>\d+)/(?P<precision_total>\d+) "
    r"false (?P<false>\d+)(?: (?P<precision_percent>\d+)%)?"
)


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


def parse_sample_metrics(text: str) -> tuple[int | None, int | None, dict[str, dict[str, int]]]:
    usable: int | None = None
    skipped: int | None = None
    metrics: dict[str, dict[str, int]] = {}
    for line in text.splitlines():
        ok_match = OK_RE.match(line)
        if not ok_match:
            continue
        body = ok_match.group("body")
        header = re.search(r"\busable (?P<usable>\d+), skipped (?P<skipped>\d+)", body)
        if header:
            usable = int(header.group("usable"))
            skipped = int(header.group("skipped"))
        for sample_match in SAMPLE_RE.finditer(body):
            metrics[sample_match.group("label")] = {
                name: int(sample_match.group(name))
                for name in (
                    "recall_hit",
                    "recall_total",
                    "primary_hit",
                    "primary_total",
                    "precision_hit",
                    "precision_total",
                    "false",
                )
            }
    return usable, skipped, metrics


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


def percent(hit: int, total: int) -> float:
    return 100.0 * hit / total if total else 0.0


def print_sample_metrics(usable: int | None, skipped: int | None, metrics: dict[str, dict[str, int]]) -> None:
    if usable is None and skipped is None and not metrics:
        return
    header_parts = []
    if usable is not None:
        header_parts.append(f"usable={usable}")
    if skipped is not None:
        header_parts.append(f"skipped={skipped}")
    print("sample metrics" + (f" {' '.join(header_parts)}" if header_parts else ""))
    for label in CATEGORIES:
        row = metrics.get(label)
        if not row:
            continue
        print(
            f"sample {label}: "
            f"recall={row['recall_hit']}/{row['recall_total']} "
            f"{percent(row['recall_hit'], row['recall_total']):.2f}% "
            f"primary={row['primary_hit']}/{row['primary_total']} "
            f"{percent(row['primary_hit'], row['primary_total']):.2f}% "
            f"precision={row['precision_hit']}/{row['precision_total']} "
            f"{percent(row['precision_hit'], row['precision_total']):.2f}% "
            f"false={row['false']}"
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
        hit_share = percent(hit, total)
        print(
            f"{kind} expected {expected}: hit={hit}/{total} "
            f"hit_share={hit_share:.2f}% off_target={off_target} "
            f"top_off_target={top_misses(expected, counts)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=pathlib.Path)
    args = parser.parse_args()

    text = args.log.read_text(errors="replace")
    matrices = parse_matrix_text(text)
    usable, skipped, metrics = parse_sample_metrics(text)
    print(f"drum gate matrix log: {args.log}")
    print_sample_metrics(usable, skipped, metrics)
    for kind in ("active", "primary"):
        print_kind_summary(kind, matrices[kind])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
