#!/usr/bin/env python3
"""Summarize per-window MusicNet traits for offline analyzer tuning."""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


def tones(value: str) -> list[str]:
    return [] if value in {"", "--"} else value.split()


def rows_by_tone(value: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for match in re.finditer(r"(\w+)=((?:(?!\s\w+=).)*)", value):
        name, values = match.groups()
        for tone in tones(values.strip()):
            result[tone].add(name)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", type=Path)
    args = parser.parse_args()

    with args.attributes.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected_pcs", "missing_pcs", "extra_pcs", "expected_chords", "chord_hit", "simple_chord_hit"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        parser.error(f"{args.attributes}: missing columns: {', '.join(sorted(missing))}")

    missing_tones = Counter(tone for row in rows for tone in tones(row["missing_pcs"]))
    extra_tones = Counter(tone for row in rows for tone in tones(row["extra_pcs"]))
    owned_extras = Counter(
        (row_name, tone)
        for row in rows
        for tone in tones(row["extra_pcs"])
        for row_name in rows_by_tone(row["detected_by_row"]).get(tone, set())
    )
    chords: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for row in rows:
        label = row["expected_chords"] or "--"
        chords[label][0] += 1
        chords[label][1] += int(row["chord_hit"] == "1")
        chords[label][2] += int(row["simple_chord_hit"] == "1")

    exact_pitch = sum(not tones(row["missing_pcs"]) and not tones(row["extra_pcs"]) for row in rows)
    exact_chords = sum(values[1] for values in chords.values())
    simple_chords = sum(values[2] for values in chords.values())
    print(f"MusicNet traits: windows {len(rows)}, exact pitch sets {exact_pitch}/{len(rows)}, "
          f"exact chords {exact_chords}/{len(rows)}, simplified chords {simple_chords}/{len(rows)}")
    print("missing pitch classes: " + " ".join(f"{tone}={count}" for tone, count in missing_tones.most_common()))
    print("extra pitch classes: " + " ".join(f"{tone}={count}" for tone, count in extra_tones.most_common()))
    print("extra pitch classes by row: " + " ".join(
        f"{row_name}:{tone}={count}" for (row_name, tone), count in owned_extras.most_common(16)
    ))
    print("hard expected chords:")
    for label, values in sorted(chords.items(), key=lambda item: (item[1][1], -item[1][0], item[0]))[:12]:
        total, hits, simple_hits = values
        print(f"  {label}: exact={hits}/{total} simple={simple_hits}/{total}")


if __name__ == "__main__":
    main()
