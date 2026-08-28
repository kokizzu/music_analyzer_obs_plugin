#!/usr/bin/env python3
"""Summarize true-pitch versus harmonic aliases in piano guitar-owner routes."""

import csv
from collections import Counter
from pathlib import Path


path = Path("build/real_note_piano_ownership.tsv")
rows: list[dict[str, str]] = []
with path.open(encoding="utf-8", newline="") as stream:
    for row in csv.DictReader(stream, delimiter="\t"):
        if row.get("buffer_strongest_row") != "guitar" or row.get("debug_owner") != "guitar":
            continue
        rows.append(row)

same_pitch = 0
aliases = Counter()
low_expected = Counter()
for row in rows:
    expected = int(row.get("expected_midi", "-1"))
    debug = int(row.get("debug_midi", "-1"))
    if expected == debug:
        same_pitch += 1
    else:
        aliases[debug - expected] += 1
    if expected < 48:
        low_expected[(expected, debug)] += 1

print(f"guitar-owner buffers={len(rows)} same_pitch={same_pitch} aliases={len(rows) - same_pitch}")
print("alias intervals=" + ",".join(f"{interval}:{count}" for interval, count in aliases.most_common()))
print("low expected/debug=" + ",".join(
    f"{expected}->{debug}:{count}" for (expected, debug), count in low_expected.most_common(30)
))
