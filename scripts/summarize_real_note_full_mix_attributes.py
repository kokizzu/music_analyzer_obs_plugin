#!/usr/bin/env python3
"""Summarize expected-pitch full-mix ownership evidence by labelled family."""

from __future__ import annotations

import collections
import csv
import pathlib


PATH = pathlib.Path("build/real_note_full_mix_attributes.tsv")


def main() -> int:
    if not PATH.is_file():
        raise SystemExit("attributes are missing; run make collect-real-note-full-mix-attributes first")
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = [
        row for row in rows
        if row.get("debug_midi", "") and row.get("debug_midi", "") == row.get("expected_midi", "")
    ]
    print(f"expected-pitch debug rows: {len(expected)}/{len(rows)}")
    by_family: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in expected:
        by_family[row.get("family", "unknown")].append(row)
    for family in sorted(by_family):
        family_rows = by_family[family]
        owners = collections.Counter(row.get("debug_owner", "unknown") for row in family_rows)
        supported = sum(row.get("vocal_tone_profile") == "1" for row in family_rows)
        print(f"{family}: rows={len(family_rows)} vocal-profile={supported} "
              + " ".join(f"{owner}={count}" for owner, count in sorted(owners.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
