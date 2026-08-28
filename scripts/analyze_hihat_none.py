#!/usr/bin/env python3
"""Report suppression flags for hi-hat samples that produce no primary class."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def main() -> int:
    path = Path("build/drum_primary_miss_attribute_rows.tsv")
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    misses = [row for row in rows if row.get("expected") == "hihat" and row.get("got") == "none"]
    flags = Counter(row.get("rule_flags", "") for row in misses)
    print(f"hihat_none rows={len(misses)} rule_flags={dict(flags)}")
    for row in misses:
        print(
            f"sample={row.get('sample', '')} flags={row.get('rule_flags', '')}"
            f" high={row.get('energy_high', '')} band={row.get('hihat_band', '')}"
            f" trigger={row.get('hihat_trigger', '')} threshold={row.get('hihat_threshold', '')}"
            f" shape={row.get('hihat_shape_score', '')}/{row.get('hihat_shape', '')}"
            f" segment={row.get('hihat_seg', '')} crash={row.get('crash_level', '')}"
            f" ride={row.get('ride_level', '')} rim={row.get('rim_level', '')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
