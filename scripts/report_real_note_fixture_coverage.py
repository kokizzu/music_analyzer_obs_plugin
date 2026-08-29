#!/usr/bin/env python3
"""Summarize real-note fixture coverage by family and source."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "real_note_samples" / "manifest.tsv"


def main() -> int:
    if not MANIFEST.is_file():
        raise SystemExit(f"missing fixture manifest: {MANIFEST}")
    with MANIFEST.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows:
        raise SystemExit("fixture manifest has no rows")
    print(f"manifest={MANIFEST} rows={len(rows)} columns={','.join(rows[0])}")
    for field in ("family", "source", "nsynth_family"):
        if field not in rows[0]:
            continue
        counts = Counter(row.get(field, "") or "--" for row in rows)
        print(f"{field}=" + " ".join(f"{key}:{value}" for key, value in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
