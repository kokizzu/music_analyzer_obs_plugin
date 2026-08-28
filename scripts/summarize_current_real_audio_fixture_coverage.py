#!/usr/bin/env python3
"""Summarize committed and generated real-audio fixtures by labelled family."""

from __future__ import annotations

import collections
import csv
import pathlib


MANIFESTS = (
    pathlib.Path("build/real_note_samples/manifest.tsv"),
    pathlib.Path("tests/fixtures/mir1k_clean_vocals/manifest.tsv"),
)


def main() -> int:
    totals: collections.Counter[str] = collections.Counter()
    sources: collections.Counter[tuple[str, str]] = collections.Counter()
    midi_ranges: dict[str, list[int]] = collections.defaultdict(list)
    for manifest in MANIFESTS:
        if not manifest.is_file():
            print(f"missing: {manifest}")
            continue
        with manifest.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                family = row.get("family", "unknown")
                totals[family] += 1
                sources[(family, row.get("source") or row.get("nsynth_family") or "unknown")] += 1
                try:
                    midi_ranges[family].append(int(row.get("midi", "0")))
                except ValueError:
                    pass
    print("family coverage:")
    for family in sorted(totals):
        values = midi_ranges[family]
        print(f"{family}: samples={totals[family]} midi={min(values) if values else '--'}-{max(values) if values else '--'}")
        relevant = [(source, count) for (source_family, source), count in sources.items() if source_family == family]
        print("  " + " ".join(f"{source}={count}" for source, count in sorted(relevant)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
