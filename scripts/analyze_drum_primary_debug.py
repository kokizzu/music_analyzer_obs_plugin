#!/usr/bin/env python3
"""Summarize analyzer_drum_samples verbose primary miss logs."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import defaultdict


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
ROW_DUMP_FIELDS = (
    [
        "sample",
        "expected",
        "got",
        "energy_low",
        "energy_mid",
        "energy_high",
        "kick_body",
        "snare_body",
        "tom_body",
        "snare_crack",
        "upper_tom_body",
        "body_shape",
    ]
    + [
        f"{category}_{field}"
        for category in CATEGORIES
        for field in ("band", "seg", "shape_score", "trigger", "threshold", "shape", "level")
    ]
    + ["merged_expected"]
)
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
DEBUG_RE = re.compile(r"debug 100ms (?P<sample>\S+) expected (?P<expected>\w+).*?\[(?P<detail>.*)\]$")
ENERGY_RE = re.compile(r"energy=(?P<low>[0-9.]+)/(?P<mid>[0-9.]+)/(?P<high>[0-9.]+)")
BODY_RE = re.compile(
    r"body=(?P<kick_body>[0-9.]+)/(?P<snare_body>[0-9.]+)/(?P<tom_body>[0-9.]+) "
    r"crack=(?P<snare_crack>[0-9.]+) upper_tom=(?P<upper_tom_body>[0-9.]+) "
    r"body_shape=(?P<body_shape>-?[0-9]+)"
)
MERGED_EXPECTED_RE = re.compile(r"\bmerged_expected=(?P<merged>[01])\b")


def parse_detail(detail: str):
    metrics = {}
    for detail_match in DETAIL_RE.finditer(detail):
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
    energy_match = ENERGY_RE.search(detail)
    energy = None
    if energy_match:
        energy = (
            float(energy_match.group("low")),
            float(energy_match.group("mid")),
            float(energy_match.group("high")),
        )
    body_match = BODY_RE.search(detail)
    body = {}
    if body_match:
        body = {
            "kick_body": float(body_match.group("kick_body")),
            "snare_body": float(body_match.group("snare_body")),
            "tom_body": float(body_match.group("tom_body")),
            "snare_crack": float(body_match.group("snare_crack")),
            "upper_tom_body": float(body_match.group("upper_tom_body")),
            "body_shape": float(body_match.group("body_shape")),
        }
    return metrics, energy, body


def row_from_match(match, got: str):
    metrics, energy, body = parse_detail(match.group("detail"))
    merged_match = MERGED_EXPECTED_RE.search(match.group("detail"))
    return {
        "sample": match.group("sample"),
        "expected": match.group("expected"),
        "got": got,
        "metrics": metrics,
        "energy": energy,
        "body": body,
        "merged_expected": merged_match.group("merged") if merged_match else "0",
    }


def parse_log(path: pathlib.Path, *, include_debug_rows: bool = False):
    rows = []
    debug_rows = []
    miss_keys = set()
    for line in path.read_text(errors="replace").splitlines():
        miss_match = MISS_RE.search(line)
        if miss_match:
            row = row_from_match(miss_match, miss_match.group("got"))
            rows.append(row)
            miss_keys.add((row["sample"], row["expected"]))
            continue
        if include_debug_rows:
            debug_match = DEBUG_RE.search(line)
            if debug_match:
                debug_rows.append(row_from_match(debug_match, debug_match.group("expected")))
    if include_debug_rows:
        rows.extend(row for row in debug_rows if (row["sample"], row["expected"]) not in miss_keys)
    return rows


def row_expected(row):
    return row["expected"]


def row_got(row):
    return row["got"]


def row_metrics(row):
    return row["metrics"]


def row_energy(row):
    return row["energy"]


def row_body(row):
    return row["body"]


def body_ratio(body, lhs: str, rhs: str) -> float:
    return body[lhs] / (body[rhs] + 1.0e-9)


def summarize_values(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"avg={sum(values) / len(values):.2f} min={min(values):.2f} max={max(values):.2f}"


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


def dump_rows(rows, expected_filter: str, limit: int) -> None:
    printed = 0
    print("\t".join(ROW_DUMP_FIELDS))
    for row in rows:
        if expected_filter and row_expected(row) != expected_filter:
            continue
        metrics = row_metrics(row)
        energy = row_energy(row) or ("", "", "")
        values = {
            "sample": row["sample"],
            "expected": row_expected(row),
            "got": row_got(row),
            "energy_low": "" if energy[0] == "" else f"{energy[0]:.6f}",
            "energy_mid": "" if energy[1] == "" else f"{energy[1]:.6f}",
            "energy_high": "" if energy[2] == "" else f"{energy[2]:.6f}",
        }
        for field, value in row_body(row).items():
            values[field] = f"{value:.6f}"
        for category in CATEGORIES:
            category_metrics = metrics.get(category, {})
            for field in ("band", "seg", "shape_score", "trigger", "threshold", "shape", "level"):
                value = category_metrics.get(field, "")
                values[f"{category}_{field}"] = "" if value == "" else f"{value:.6f}"
        values["merged_expected"] = row.get("merged_expected", "0")
        print("\t".join(values.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


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
        body_rows = [row_body(row) for row in group if row_body(row)]
        if body_rows:
            for lhs, rhs, label in (
                ("tom_body", "snare_body", "tom/snare body"),
                ("tom_body", "kick_body", "tom/kick body"),
                ("snare_crack", "snare_body", "crack/snare body"),
                ("upper_tom_body", "snare_crack", "upper_tom/crack"),
            ):
                print(
                    f"    {label}: "
                    f"{summarize_values([body_ratio(body, lhs, rhs) for body in body_rows])}"
                )
            body_shapes = defaultdict(int)
            for body in body_rows:
                body_shapes[int(body["body_shape"])] += 1
            shapes = " ".join(f"{shape}={count}" for shape, count in sorted(body_shapes.items()))
            print(f"    body_shape: {shapes}")
        print(f"    near-level ties: {ties}/{len(group)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--expected", default="", help="only print this expected drum in --dump-rows mode")
    parser.add_argument(
        "--dump-rows",
        action="store_true",
        help="print compact per-primary-miss drum attributes as TSV and skip summaries",
    )
    parser.add_argument(
        "--include-debug-rows",
        action="store_true",
        help="include analyzer_drum_samples debug rows in --dump-rows output, including correct primaries",
    )
    parser.add_argument(
        "--dump-limit",
        type=int,
        default=0,
        help="maximum rows to print in --dump-rows mode; 0 means all",
    )
    args = parser.parse_args()

    all_rows = []
    parsed_logs = []
    for path in args.logs:
        rows = parse_log(path, include_debug_rows=args.include_debug_rows)
        parsed_logs.append((path, rows))
        all_rows.extend(rows)
    if args.dump_rows:
        dump_rows(all_rows, args.expected, max(0, args.dump_limit))
        return 0

    print_overall(all_rows)
    for path, rows in parsed_logs:
        summarize(path.stem.replace("_primary_debug", ""), rows, max(0, args.examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
