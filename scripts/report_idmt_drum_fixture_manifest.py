#!/usr/bin/env python3
"""Summarize the external IDMT drum manifest for deterministic test selection."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


DEFAULT_ROOT = Path("/media/kyz/sshflashtor/InstrumentSamples/idmt_drums_samples")


def main() -> None:
    root = DEFAULT_ROOT
    manifest = root / "manifest.tsv"
    if not manifest.is_file():
        raise SystemExit(f"missing IDMT drum manifest: {manifest}")
    with manifest.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows:
        raise SystemExit("empty IDMT drum manifest")
    print("manifest=" + str(manifest))
    print("columns=" + ",".join(rows[0]))
    print("rows=" + str(len(rows)))
    for field in ("category", "family", "source", "instrument", "class", "drum", "note"):
        values = Counter(row.get(field, "") for row in rows)
        if values and any(values):
            print(field + "=" + ",".join(f"{name}={count}" for name, count in values.most_common(20)))
    for row in rows[:12]:
        print("sample=" + "|".join(f"{field}={value}" for field, value in row.items()))


if __name__ == "__main__":
    main()
