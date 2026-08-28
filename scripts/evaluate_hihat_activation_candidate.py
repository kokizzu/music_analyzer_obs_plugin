#!/usr/bin/env python3
"""Evaluate a measured one-shot hi-hat activation signature against all classes."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def number(row: dict[str, str], name: str) -> float:
    return float(row.get(name, "0") or 0)


def candidate(row: dict[str, str]) -> bool:
    return (
        row.get("flag_one_shot_source") == "1"
        and number(row, "hihat_level") <= 0.001
        and number(row, "hihat_shape") >= 0.99
        and number(row, "hihat_band") >= 8.75
        and number(row, "hihat_band") <= 60.0
        and number(row, "hihat_trigger") >= 28.4
        and number(row, "energy_high") >= 0.44
        and number(row, "crash_level") <= 0.001
        and number(row, "ride_level") <= 0.001
        and number(row, "rim_level") <= 0.001
        and number(row, "kick_level") <= 0.001
        and number(row, "snare_level") <= 0.001
        and number(row, "tom_level") <= 0.001
    )


def main() -> int:
    path = Path("build/drum_primary_miss_attribute_rows.tsv")
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    matches = [row for row in rows if candidate(row)]
    expected = Counter(row.get("expected", "") for row in matches)
    got = Counter(row.get("got", "") for row in matches)
    print(f"hihat_activation_candidate rows={len(matches)} expected={dict(expected)} got={dict(got)}")
    for row in matches:
        if row.get("expected") != "hihat":
            print(
                f"non_hihat sample={row.get('sample', '')} expected={row.get('expected', '')}"
                f" got={row.get('got', '')} high={row.get('energy_high', '')}"
                f" band={row.get('hihat_band', '')} trigger={row.get('hihat_trigger', '')}"
                f" tom_level={row.get('tom_level', '')} tom_shape={row.get('tom_shape', '')}"
                f" tom_band={row.get('tom_band', '')} tom_body={row.get('tom_body', '')}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
