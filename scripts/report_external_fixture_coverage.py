#!/usr/bin/env python3
"""Summarize family, source, and MIDI coverage across external TSV manifests."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    fixture_root = (root / "build" / "InstrumentSamples").resolve()
    manifests = sorted(fixture_root.rglob("manifest.tsv"))
    families: Counter[str] = Counter()
    sources: Counter[tuple[str, str]] = Counter()
    midi_ranges: dict[str, list[int]] = defaultdict(list)

    for manifest in manifests:
        with manifest.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            for row in reader:
                family = row.get("family", "")
                if not family:
                    continue
                families[family] += 1
                sources[(family, row.get("source", row.get("program_name", "unknown")))] += 1
                try:
                    midi_ranges[family].append(int(row.get("midi", "")))
                except ValueError:
                    pass

    print(f"fixture_store={fixture_root}")
    for family, count in families.most_common():
        midis = midi_ranges[family]
        midi_text = f" midi={min(midis)}..{max(midis)}" if midis else ""
        print(f"{family}: {count}{midi_text}")
        family_sources = [
            (source, source_count)
            for (source_family, source), source_count in sources.items()
            if source_family == family
        ]
        for source, source_count in sorted(family_sources, key=lambda item: (-item[1], item[0]))[:12]:
            print(f"  {source}: {source_count}")


if __name__ == "__main__":
    main()
