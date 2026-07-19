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
MISS_RE = re.compile(r"expected (?P<expected>\w+) got (?P<got>\w+|ambiguous|none).*?\[(?P<detail>.*)\]$")
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
        rows.append((match.group("expected"), match.group("got"), metrics, energy))
    return rows


def summarize(label: str, rows) -> None:
    print(f"{label}: {len(rows)} primary misses")
    grouped = defaultdict(list)
    for expected, got, metrics, energy in rows:
        grouped[(expected, got)].append((metrics, energy))

    for (expected, got), group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"  {expected} -> {got}: {len(group)}")
        if expected not in CATEGORIES or got not in CATEGORIES:
            continue
        for metric in ("band", "seg", "shape_score", "trigger", "level"):
            ratios = [
                metrics[expected][metric] / (metrics[got][metric] + 1.0e-9)
                for metrics, _energy in group
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
            for metrics, _energy in group
            if expected in metrics
            and got in metrics
            and abs(metrics[expected]["level"] - metrics[got]["level"]) <= 0.015
        )
        supported = sum(
            1 for metrics, _energy in group if expected in metrics and metrics[expected]["shape"] > 0.5
        )
        got_supported = sum(1 for metrics, _energy in group if got in metrics and metrics[got]["shape"] > 0.5)
        expected_active = sum(
            1 for metrics, _energy in group if expected in metrics and metrics[expected]["level"] > 0.30
        )
        got_level_avg = sum(metrics[got]["level"] for metrics, _energy in group if got in metrics) / max(
            1, sum(1 for metrics, _energy in group if got in metrics)
        )
        expected_level_avg = sum(
            metrics[expected]["level"] for metrics, _energy in group if expected in metrics
        ) / max(1, sum(1 for metrics, _energy in group if expected in metrics))
        print(f"    expected shape supported: {supported}/{len(group)}")
        print(f"    got shape supported: {got_supported}/{len(group)}")
        print(f"    expected active: {expected_active}/{len(group)}")
        print(f"    avg levels expected={expected_level_avg:.2f} got={got_level_avg:.2f}")
        energies = [energy for _metrics, energy in group if energy is not None]
        if energies:
            avg_low = sum(energy[0] for energy in energies) / len(energies)
            avg_mid = sum(energy[1] for energy in energies) / len(energies)
            avg_high = sum(energy[2] for energy in energies) / len(energies)
            print(f"    avg energy low/mid/high={avg_low:.2f}/{avg_mid:.2f}/{avg_high:.2f}")
        print(f"    near-level ties: {ties}/{len(group)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    for path in args.logs:
        summarize(path.stem.replace("_primary_debug", ""), parse_log(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
