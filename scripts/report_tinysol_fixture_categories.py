#!/usr/bin/env python3
"""Summarize TinySOL's labeled families and sources before fixture selection."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "build" / "tinysol_samples" / "manifest.tsv"
    by_family: Counter[str] = Counter()
    by_source: dict[str, Counter[str]] = defaultdict(Counter)
    midi_ranges: dict[str, list[int]] = defaultdict(list)
    examples: dict[str, list[str]] = defaultdict(list)
    with manifest.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            family = row["family"]
            source = row["source"]
            midi = int(row["midi"])
            by_family[family] += 1
            by_source[family][source] += 1
            midi_ranges[family].append(midi)
            if len(examples[family]) < 6:
                examples[family].append(f"{row['id']}|{source}|{row['note']}")
    for family, count in sorted(by_family.items()):
        midis = midi_ranges[family]
        print(f"family={family} count={count} midi={min(midis)}-{max(midis)}")
        print("  sources=" + " ".join(
            f"{source}={count}" for source, count in by_source[family].most_common()
        ))
        for example in examples[family]:
            print(f"  example={example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
