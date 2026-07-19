#!/usr/bin/env python3
"""Summarize analyzer_drum_samples verbose primary miss logs."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import defaultdict


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
DETAIL_RE = re.compile(
    r"(?P<cat>kick|snare|hihat|crash|tom|ride|rim) "
    r"band=(?P<band>[0-9.]+) "
    r"seg=(?P<seg>[0-9.]+) "
    r"shape_score=(?P<shape_score>[0-9.]+) "
    r"trigger=(?P<trigger>[0-9.]+)/(?P<threshold>[0-9.]+) "
    r"shape=(?P<shape>[01]) "
    r"level=(?P<level>[0-9.]+)"
)
MISS_RE = re.compile(
    r"primary miss 100ms (?P<sample>\S+) expected (?P<expected>\w+) "
    r"got (?P<got>\w+|ambiguous|none).*?\[(?P<detail>.*)\]$"
)
ENERGY_RE = re.compile(r"energy=(?P<low>[0-9.]+)/(?P<mid>[0-9.]+)/(?P<high>[0-9.]+)")


def parse_log(path: pathlib.Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        if "primary miss" not in line:
            continue
        match = MISS_RE.search(line)
        if not match:
            continue
        metrics = {}
        for detail_match in DETAIL_RE.finditer(match.group("detail")):
            cat = detail_match.group("cat")
            metrics[cat] = {
                "band": float(detail_match.group("band")),
                "seg": float(detail_match.group("seg")),
                "shape_score": float(detail_match.group("shape_score")),
                "trigger": float(detail_match.group("trigger")),
                "threshold": float(detail_match.group("threshold")),
                "shape": float(detail_match.group("shape")),
                "level": float(detail_match.group("level")),
            }
        energy_match = ENERGY_RE.search(match.group("detail"))
        energy = None
        if energy_match:
            energy = (
                float(energy_match.group("low")),
                float(energy_match.group("mid")),
                float(energy_match.group("high")),
            )
        rows.append(
            {
                "sample": match.group("sample"),
                "expected": match.group("expected"),
                "got": match.group("got"),
                "metrics": metrics,
                "energy": energy,
            }
        )
    return rows


def row_expected(row):
    return row["expected"]


def row_got(row):
    return row["got"]


def row_metrics(row):
    return row["metrics"]


def row_energy(row):
    return row["energy"]


def print_overall(rows) -> None:
    if not rows:
        return

    print("overall primary misses")
    for expected in CATEGORIES:
        by_got = defaultdict(int)
        for row in rows:
            if row_expected(row) == expected:
                by_got[row_got(row)] += 1
        if not by_got:
            continue
        sorted_pairs = sorted(by_got.items(), key=lambda item: (-item[1], item[0]))
        pairs = " ".join(f"{got}={count}" for got, count in sorted_pairs)
        print(f"  expected {expected}: {pairs}")


def summarize(label: str, rows, example_count: int) -> None:
    print(f"{label}: {len(rows)} primary misses")
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row_expected(row), row_got(row))].append(row)

    for (expected, got), group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"  {expected} -> {got}: {len(group)}")
        examples = [row["sample"] for row in group[:example_count]]
        if examples:
            print(f"    examples: {', '.join(examples)}")
        if expected not in CATEGORIES or got not in CATEGORIES:
            continue
        metric_rows = [row_metrics(row) for row in group]
        for metric in ("band", "seg", "shape_score", "trigger", "level"):
            ratios = [
                metrics[expected][metric] / (metrics[got][metric] + 1.0e-9)
                for metrics in metric_rows
                if expected in metrics and got in metrics
            ]
            if not ratios:
                continue
            print(
                f"    {metric:11s} expected/got "
                f"avg={sum(ratios) / len(ratios):.2f} "
                f"min={min(ratios):.2f} max={max(ratios):.2f}"
            )
        ties = sum(
            1
            for metrics in metric_rows
            if expected in metrics
            and got in metrics
            and abs(metrics[expected]["level"] - metrics[got]["level"]) <= 0.015
        )
        supported = sum(
            1
            for metrics in metric_rows
            if expected in metrics and metrics[expected]["shape"] > 0.5
        )
        got_supported = sum(
            1
            for metrics in metric_rows
            if got in metrics and metrics[got]["shape"] > 0.5
        )
        expected_active = sum(
            1
            for metrics in metric_rows
            if expected in metrics and metrics[expected]["level"] > 0.30
        )
        expected_active_but_lower = sum(
            1
            for metrics in metric_rows
            if expected in metrics
            and got in metrics
            and metrics[expected]["level"] > 0.30
            and metrics[expected]["level"] < metrics[got]["level"]
        )
        got_level_count = sum(1 for metrics in metric_rows if got in metrics)
        expected_level_count = sum(1 for metrics in metric_rows if expected in metrics)
        got_level_avg = sum(metrics[got]["level"] for metrics in metric_rows if got in metrics) / max(
            1, got_level_count
        )
        expected_level_avg = sum(
            metrics[expected]["level"] for metrics in metric_rows if expected in metrics
        ) / max(1, expected_level_count)
        print(f"    expected shape supported: {supported}/{len(group)}")
        print(f"    got shape supported: {got_supported}/{len(group)}")
        print(f"    expected active: {expected_active}/{len(group)}")
        print(f"    expected active but lower: {expected_active_but_lower}/{len(group)}")
        print(f"    avg levels expected={expected_level_avg:.2f} got={got_level_avg:.2f}")
        energies = [row_energy(row) for row in group if row_energy(row) is not None]
        if energies:
            avg_low = sum(energy[0] for energy in energies) / len(energies)
            avg_mid = sum(energy[1] for energy in energies) / len(energies)
            avg_high = sum(energy[2] for energy in energies) / len(energies)
            print(f"    avg energy low/mid/high={avg_low:.2f}/{avg_mid:.2f}/{avg_high:.2f}")
        print(f"    near-level ties: {ties}/{len(group)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--examples", type=int, default=3)
    args = parser.parse_args()

    all_rows = []
    parsed_logs = []
    for path in args.logs:
        rows = parse_log(path)
        parsed_logs.append((path, rows))
        all_rows.extend(rows)
    print_overall(all_rows)
    for path, rows in parsed_logs:
        summarize(path.stem.replace("_primary_debug", ""), rows, max(0, args.examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
