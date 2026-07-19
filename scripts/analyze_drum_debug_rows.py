#!/usr/bin/env python3
"""Summarize analyzer_drum_samples verbose debug rows."""

from __future__ import annotations

import argparse
from collections import Counter
import pathlib
import re


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
DEBUG_RE = re.compile(r"debug 100ms (?P<sample>\S+) expected (?P<expected>\w+)")
BODY_RE = re.compile(
    r"body=(?P<kick_body>[0-9.]+)/(?P<snare_body>[0-9.]+)/(?P<tom_body>[0-9.]+) "
    r"crack=(?P<snare_crack>[0-9.]+) upper_tom=(?P<upper_tom_body>[0-9.]+) "
    r"body_shape=(?P<body_shape>-?[0-9]+)"
)


def parse_debug_rows(path: pathlib.Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        debug_match = DEBUG_RE.search(line)
        if not debug_match:
            continue
        metrics = {}
        for match in DETAIL_RE.finditer(line):
            metrics[match.group("cat")] = {
                "band": float(match.group("band")),
                "seg": float(match.group("seg")),
                "shape_score": float(match.group("shape_score")),
                "trigger": float(match.group("trigger")),
                "threshold": float(match.group("threshold")),
                "shape": float(match.group("shape")),
                "level": float(match.group("level")),
            }
        body_match = BODY_RE.search(line)
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
        if metrics:
            rows.append(
                {
                    "sample": debug_match.group("sample"),
                    "expected": debug_match.group("expected"),
                    "metrics": metrics,
                    "body": body,
                }
            )
    return rows


def primary(metrics):
    best = "none"
    best_level = 0.0
    for category in CATEGORIES:
        level = metrics.get(category, {}).get("level", 0.0)
        if level <= 0.30 or level <= best_level:
            continue
        best = category
        best_level = level
    if best == "none":
        return best

    tied = sum(
        1
        for category in CATEGORIES
        if metrics.get(category, {}).get("level", 0.0) > 0.30
        and abs(metrics[category]["level"] - best_level) <= 0.005
    )
    return "ambiguous" if tied > 1 else best


def ratio(metrics, lhs, rhs, key):
    return metrics[lhs][key] / (metrics[rhs][key] + 1.0e-9)


def body_ratio(body, lhs, rhs):
    return body[lhs] / (body[rhs] + 1.0e-9)


def summarize_values(values):
    if not values:
        return "n/a"
    return f"avg={sum(values) / len(values):.2f} min={min(values):.2f} max={max(values):.2f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=pathlib.Path)
    parser.add_argument("--expected", default="")
    parser.add_argument("--focus", default="")
    parser.add_argument("--against", default="snare")
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()

    rows = parse_debug_rows(args.log)
    if args.expected:
        rows = [row for row in rows if row["expected"] == args.expected]

    by_primary = Counter(primary(row["metrics"]) for row in rows)
    print(f"rows={len(rows)} primary=" + " ".join(f"{k}={v}" for k, v in sorted(by_primary.items())))

    focus = args.focus
    against = args.against
    if focus and against:
        for got, count in sorted(by_primary.items(), key=lambda item: (-item[1], item[0])):
            group = [row for row in rows if primary(row["metrics"]) == got]
            if not group:
                continue
            complete = [
                row["metrics"]
                for row in group
                if focus in row["metrics"] and against in row["metrics"]
            ]
            print(f"{got}: {count}")
            for key in ("band", "seg", "shape_score", "trigger", "level"):
                print(
                    f"  {focus}/{against} {key}: "
                    f"{summarize_values([ratio(metrics, focus, against, key) for metrics in complete])}"
                )
            print(
                f"  {focus} support: "
                f"{sum(1 for metrics in complete if metrics[focus]['shape'] > 0.5)}/{len(complete)}"
            )
            print(
                f"  {focus} active: "
                f"{sum(1 for metrics in complete if metrics[focus]['level'] > 0.30)}/{len(complete)}"
            )
            body_rows = [row["body"] for row in group if row.get("body")]
            if body_rows:
                for lhs, rhs, label in (
                    ("tom_body", "snare_body", "tom/snare body"),
                    ("tom_body", "kick_body", "tom/kick body"),
                    ("snare_crack", "snare_body", "crack/snare body"),
                    ("upper_tom_body", "snare_crack", "upper_tom/crack"),
                ):
                    print(
                        f"  {label}: "
                        f"{summarize_values([body_ratio(body, lhs, rhs) for body in body_rows])}"
                    )
                body_shapes = Counter(int(body["body_shape"]) for body in body_rows)
                print(
                    "  body_shape: "
                    + " ".join(f"{shape}={count}" for shape, count in sorted(body_shapes.items()))
                )
            examples = [row["sample"] for row in group[: max(0, args.examples)]]
            if examples:
                print(f"  examples: {', '.join(examples)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
