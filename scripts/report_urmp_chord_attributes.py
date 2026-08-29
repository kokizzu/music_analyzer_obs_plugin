#!/usr/bin/env python3
"""Show chord-related replay attributes for annotated URMP chord misses."""

from collections import defaultdict
import csv
from pathlib import Path

from report_urmp_chord_cases import (
    ATTRIBUTES,
    MANIFEST,
    chord_tokens,
    expected_chord,
)


def main() -> int:
    pitches_by_path: dict[str, set[int]] = defaultdict(set)
    path_by_id: dict[str, str] = {}
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            pitches_by_path[row["path"]].add(int(row["midi"]) % 12)
            path_by_id[row["id"]] = row["path"]

    rows_by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    with ATTRIBUTES.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            path = path_by_id.get(row["sample_id"])
            if path is not None:
                rows_by_path[path].append(row)

    for path, pitches in sorted(pitches_by_path.items()):
        detected = expected_chord(pitches)
        if detected is None:
            continue
        expected, _ = detected
        rows = rows_by_path[path]
        observed = set().union(*(chord_tokens(row.get("global_chord", "")) for row in rows))
        if expected in observed:
            continue
        print(f"expected={expected} observed={' '.join(sorted(observed)) or '--'} path={path}")
        keys = sorted({key for row in rows for key in row if "chord" in key or "root" in key})
        for row in rows:
            values = " ".join(f"{key}={row[key]}" for key in keys if row.get(key))
            print(f"  id={row['sample_id']} {values}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
