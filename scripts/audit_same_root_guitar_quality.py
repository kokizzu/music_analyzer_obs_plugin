#!/usr/bin/env python3
"""Audit a measured same-root guitar quality promotion across corpora.

Unlike an oracle recovery sweep, the proposed major/minor quality is selected
only from the raw pitch-class levels.  A promotion is considered only when the
existing chord already contains the same-root power component and the display
has a bounded number of aliases.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_guitar_chord_recovery import (
    PROMOTION_RATIOS,
    expected_root,
    load_rows,
    power_root_allowed,
    promoted_quality_for_power_root,
    split_labels,
)


def audit(path: Path, ratio: float, max_labels: int) -> tuple[int, int, int]:
    rows = load_rows(path)
    gains = regressions = candidates = 0
    for row in rows:
        expected = set(split_labels(row.get("expected_chords", "")))
        if not expected:
            continue
        labels = split_labels(row.get("guitar_chord", ""))
        root = expected_root(next(iter(split_labels(row.get("expected_chords", ""))), ""))
        if root is None or len(labels) > max_labels or not power_root_allowed(labels, root, "any_power"):
            continue
        promoted = promoted_quality_for_power_root(row, root, ratio, 0.005, "raw")
        if promoted is None:
            continue
        candidates += 1
        current_hit = row.get("chord_hit", "") == "1"
        if not current_hit and promoted in expected:
            gains += 1
        elif current_hit and promoted not in expected:
            regressions += 1
    return candidates, gains, regressions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", nargs="+", type=Path)
    parser.add_argument("--max-labels", type=int, default=5)
    args = parser.parse_args()
    if args.max_labels < 1:
        parser.error("--max-labels must be positive")

    best_ratio = 0.0
    best_support = -1
    best_regressions = 0
    corpus_total = len(args.attributes)
    print("same-root guitar quality audit")
    for ratio in PROMOTION_RATIOS:
        results = [(path, audit(path, ratio, args.max_labels)) for path in args.attributes]
        support = sum(gains > 0 and regressions == 0 for _, (_, gains, regressions) in results)
        regressions = sum(result[2] for _, result in results)
        if support > best_support or (support == best_support and regressions < best_regressions):
            best_ratio, best_support, best_regressions = ratio, support, regressions
        print(f"floor=max(anchor*{ratio:.3f},0.005)")
        for path, (candidates, gains, false) in results:
            print(f"  {path.name}: candidates={candidates} gains={gains} regressions={false}")
        print(f"  zero-regression support={support}/{corpus_total} regressions={regressions}")
    common = int(best_support == corpus_total and best_regressions == 0)
    print(
        "same_root_guitar_quality: "
        f"best_floor={best_ratio:.3f} supported_corpora={best_support}/{corpus_total} "
        f"regressions={best_regressions} common_zero_regression={common}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
