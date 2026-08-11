#!/usr/bin/env python3
"""Summarize per-window MusicNet traits for offline analyzer tuning."""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


NOTE_PITCH_CLASSES = {
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11,
}


def tones(value: str) -> list[str]:
    return [] if value in {"", "--"} else value.split()


def rows_by_tone(value: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for match in re.finditer(r"(\w+)=((?:(?!\s\w+=).)*)", value):
        name, values = match.groups()
        for tone in tones(values.strip()):
            result[tone].add(name)
    return result


def plain_major_root(label: str) -> int | None:
    component = label.split("=", 1)[0]
    for name, pitch_class in sorted(NOTE_PITCH_CLASSES.items(), key=lambda item: -len(item[0])):
        if component == name:
            return pitch_class
    return None


def expected_has_dominant_seventh(value: str, root: int) -> bool:
    root_name = next(name for name, pitch_class in NOTE_PITCH_CLASSES.items() if pitch_class == root)
    return f"{root_name}7" in value.split("/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("attributes", type=Path)
    args = parser.parse_args()

    with args.attributes.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {
        "recording", "expected_pcs", "detected_pcs", "missing_pcs", "extra_pcs",
        "expected_chords", "chord_hit", "simple_chord_hit", "global_chord",
    }
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
    exact_pitch_chord_misses = Counter(
        ((row["expected_chords"] or "--"), (row["global_chord"] or "--"))
        for row in rows
        if not tones(row["missing_pcs"]) and not tones(row["extra_pcs"]) and row["chord_hit"] != "1"
    )
    exact_display_dominant_seventh = []
    for row in rows:
        root = plain_major_root(row["global_chord"])
        if root is None:
            continue
        detected = {NOTE_PITCH_CLASSES[tone] for tone in tones(row["detected_pcs"])}
        expected_tones = {root, (root + 4) % 12, (root + 7) % 12, (root + 10) % 12}
        if detected != expected_tones:
            continue
        exact_display_dominant_seventh.append(
            (expected_has_dominant_seventh(row["expected_chords"], root), row)
        )
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
    print("exact-pitch chord-label misses:")
    for (expected, detected), count in exact_pitch_chord_misses.most_common(16):
        print(f"  {expected} -> {detected}: {count}")
    dominant_hits = sum(hit for hit, _ in exact_display_dominant_seventh)
    print(
        "complete-display dominant-seventh candidates: "
        f"{dominant_hits}/{len(exact_display_dominant_seventh)} expected labels"
    )
    for hit, row in exact_display_dominant_seventh[:8]:
        print(
            f"  {'+' if hit else '-'} recording={row['recording']} expected={row['expected_chords']} "
            f"global={row['global_chord']} pcs={row['detected_pcs']}"
        )


if __name__ == "__main__":
    main()
