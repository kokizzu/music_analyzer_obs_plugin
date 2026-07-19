#!/usr/bin/env python3
"""Evaluate simple drum primary-label rule candidates from verbose debug rows."""

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
ROW_RE = re.compile(r"debug 100ms (?P<sample>\S+) expected (?P<expected>\w+)")
TRANSIENT_RE = re.compile(
    r"transient=(?P<transient>[0-9.]+) onset=(?P<onset>[0-9.]+) "
    r"energy=(?P<low>[0-9.]+)/(?P<mid>[0-9.]+)/(?P<high>[0-9.]+)"
    r"(?: body=(?P<kick_body>[0-9.]+)/(?P<snare_body>[0-9.]+)/(?P<tom_body>[0-9.]+)"
    r" crack=(?P<snare_crack>[0-9.]+) upper_tom=(?P<upper_tom_body>[0-9.]+)"
    r" body_shape=(?P<body_shape>-?[0-9]+))?"
)


def parse_rows(path: pathlib.Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        row_match = ROW_RE.search(line)
        if not row_match:
            continue
        metrics = {}
        for match in DETAIL_RE.finditer(line):
            cat = match.group("cat")
            metrics[cat] = {key: float(match.group(key)) for key in (
                "band",
                "seg",
                "shape_score",
                "trigger",
                "threshold",
                "shape",
                "level",
            )}
        transient_match = TRANSIENT_RE.search(line)
        if not metrics or transient_match is None:
            continue
        rows.append(
            {
                "sample": row_match.group("sample"),
                "expected": row_match.group("expected"),
                "metrics": metrics,
                "transient": float(transient_match.group("transient")),
                "onset": float(transient_match.group("onset")),
                "low": float(transient_match.group("low")),
                "mid": float(transient_match.group("mid")),
                "high": float(transient_match.group("high")),
                "kick_body": float(transient_match.group("kick_body") or 0.0),
                "snare_body": float(transient_match.group("snare_body") or 0.0),
                "tom_body": float(transient_match.group("tom_body") or 0.0),
                "snare_crack": float(transient_match.group("snare_crack") or 0.0),
                "upper_tom_body": float(transient_match.group("upper_tom_body") or 0.0),
                "body_shape": int(transient_match.group("body_shape") or -1),
            }
        )
    return rows


def level_from(trigger: float, threshold: float) -> float:
    threshold_excess = trigger / (threshold + 1.0e-6) - 1.0
    return max(0.0, min(1.0, 0.25 + 0.75 * threshold_excess / (threshold_excess + 3.5)))


def primary(levels: dict[str, float]) -> str:
    best = "none"
    best_level = 0.0
    for cat in CATEGORIES:
        level = levels.get(cat, 0.0)
        if level <= 0.30 or level <= best_level:
            continue
        best = cat
        best_level = level
    if best == "none":
        return best
    ties = sum(
        1
        for cat in CATEGORIES
        if levels.get(cat, 0.0) > 0.30 and abs(levels[cat] - best_level) <= 0.005
    )
    return "ambiguous" if ties > 1 else best


def baseline_counts(rows):
    by_expected: dict[str, Counter[str]] = {cat: Counter() for cat in CATEGORIES}
    for row in rows:
        metrics = row["metrics"]
        levels = {cat: metrics[cat]["level"] for cat in CATEGORIES if cat in metrics}
        by_expected[row["expected"]][primary(levels)] += 1
    return by_expected


def primary_hit_count(by_expected: dict[str, Counter[str]], category: str) -> int:
    return by_expected[category][category]


def shell_primary_total(by_expected: dict[str, Counter[str]]) -> int:
    return sum(primary_hit_count(by_expected, category) for category in ("kick", "snare", "tom"))


def simulate(
    rows,
    *,
    snare_ratio: float,
    kick_ratio: float,
    mid_low_ratio: float,
    mul: float,
    add: float,
    lower_threshold: bool,
    active_bias: bool,
    max_crack_body: float,
    min_upper_tom_crack: float,
):
    by_expected: dict[str, Counter[str]] = {cat: Counter() for cat in CATEGORIES}
    changed = Counter()
    for row in rows:
        metrics = row["metrics"]
        levels = {cat: metrics[cat]["level"] for cat in CATEGORIES if cat in metrics}
        tom = metrics.get("tom")
        kick = metrics.get("kick")
        snare = metrics.get("snare")
        if tom and kick and snare:
            guard = (
                tom["shape"] > 0.5
                and row["onset"] >= 4.0
                and tom["trigger"] >= 1.42 * 1.70
                and tom["shape_score"] >= snare["shape_score"] * snare_ratio
                and tom["shape_score"] >= kick["shape_score"] * kick_ratio
                and row["mid"] >= row["low"] * mid_low_ratio
                and (
                    max_crack_body <= 0.0
                    or row["snare_body"] <= 1.0e-6
                    or row["snare_crack"] <= row["snare_body"] * max_crack_body
                    or (
                        min_upper_tom_crack > 0.0
                        and row["upper_tom_body"] >= row["snare_crack"] * min_upper_tom_crack
                    )
                )
            )
            if guard:
                if lower_threshold:
                    lowered = level_from(tom["trigger"], 1.42 * 0.30)
                    levels["tom"] = max(levels["tom"], lowered)
                if active_bias and levels["tom"] > 0.30:
                    levels["tom"] = min(1.0, levels["tom"] * mul + add)
        before = primary({cat: metrics[cat]["level"] for cat in CATEGORIES if cat in metrics})
        after = primary(levels)
        by_expected[row["expected"]][after] += 1
        if before != after:
            changed[f"{before}->{after}"] += 1
    return by_expected, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    parser.add_argument("--snare-ratios", default="1.08,1.10,1.12,1.15,1.18")
    parser.add_argument("--kick-ratios", default="0.90,1.00,1.05,1.10,1.20,1.30")
    parser.add_argument("--mid-low-ratios", default="0.75,0.90,1.00,1.10,1.20")
    parser.add_argument("--mul", type=float, default=1.015)
    parser.add_argument("--add", type=float, default=0.010)
    parser.add_argument("--no-lower-threshold", action="store_true")
    parser.add_argument("--active-bias", action="store_true")
    parser.add_argument("--max-crack-body", type=float, default=0.0)
    parser.add_argument("--min-upper-tom-crack", type=float, default=0.0)
    parser.add_argument("--score-mode", choices=("net", "legacy"), default="net",
                        help="net ranks by kick+snare+tom primary hits; legacy keeps the old tom-heavy score")
    parser.add_argument("--min-tom-gain", type=int, default=-1000000)
    parser.add_argument("--max-kick-loss", type=int, default=1000000)
    parser.add_argument("--max-snare-loss", type=int, default=1000000)
    parser.add_argument("--min-total-gain", type=int, default=-1000000)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    rows = []
    for path in args.logs:
        rows.extend(parse_rows(path))

    base = baseline_counts(rows)
    base_tom = primary_hit_count(base, "tom")
    base_kick = primary_hit_count(base, "kick")
    base_snare = primary_hit_count(base, "snare")
    base_total = shell_primary_total(base)
    print(f"baseline tom={base_tom} kick={base_kick} snare={base_snare} total={base_total}")

    snare_ratios = [float(value) for value in args.snare_ratios.split(",") if value]
    kick_ratios = [float(value) for value in args.kick_ratios.split(",") if value]
    mid_low_ratios = [float(value) for value in args.mid_low_ratios.split(",") if value]

    scored = []
    for snare_ratio in snare_ratios:
        for kick_ratio in kick_ratios:
            for mid_low_ratio in mid_low_ratios:
                by_expected, changed = simulate(
                    rows,
                    snare_ratio=snare_ratio,
                    kick_ratio=kick_ratio,
                    mid_low_ratio=mid_low_ratio,
                    mul=args.mul,
                    add=args.add,
                    lower_threshold=not args.no_lower_threshold,
                    active_bias=args.active_bias,
                    max_crack_body=args.max_crack_body,
                    min_upper_tom_crack=args.min_upper_tom_crack,
                )
                tom_primary = by_expected["tom"]["tom"]
                kick_primary = by_expected["kick"]["kick"]
                snare_primary = by_expected["snare"]["snare"]
                tom_delta = tom_primary - base_tom
                kick_delta = kick_primary - base_kick
                snare_delta = snare_primary - base_snare
                total = tom_primary + kick_primary + snare_primary
                total_delta = total - base_total
                if tom_delta < args.min_tom_gain:
                    continue
                if -kick_delta > args.max_kick_loss:
                    continue
                if -snare_delta > args.max_snare_loss:
                    continue
                if total_delta < args.min_total_gain:
                    continue
                score = total if args.score_mode == "net" else tom_primary * 10 + kick_primary + snare_primary
                scored.append(
                    (
                        score,
                        total,
                        total_delta,
                        tom_primary,
                        tom_delta,
                        kick_primary,
                        kick_delta,
                        snare_primary,
                        snare_delta,
                        snare_ratio,
                        kick_ratio,
                        mid_low_ratio,
                        changed,
                    )
                )

    if not scored:
        print("no candidates")
        return 0

    for (
        _score,
        total,
        total_delta,
        tom_primary,
        tom_delta,
        kick_primary,
        kick_delta,
        snare_primary,
        snare_delta,
        snare_ratio,
        kick_ratio,
        mid_low_ratio,
        changed,
    ) in sorted(scored, reverse=True)[: max(0, args.top)]:
        changed_text = " ".join(f"{key}={value}" for key, value in sorted(changed.items()))
        print(
            f"tom={tom_primary} ({tom_delta:+d}) kick={kick_primary} ({kick_delta:+d}) "
            f"snare={snare_primary} ({snare_delta:+d}) total={total} ({total_delta:+d}) "
            f"snare_ratio={snare_ratio:.2f} kick_ratio={kick_ratio:.2f} "
            f"mid_low={mid_low_ratio:.2f} changed=[{changed_text}]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
