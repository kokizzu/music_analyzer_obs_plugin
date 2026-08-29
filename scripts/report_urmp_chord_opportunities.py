#!/usr/bin/env python3
"""Report annotation-backed chord opportunities in the external URMP mixture set."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "build" / "urmp_mixture_cases" / "manifest.tsv"
PITCH_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
TEMPLATES = (
    ("", {0, 4, 7}),
    ("m", {0, 3, 7}),
    ("sus2", {0, 2, 7}),
    ("sus4", {0, 5, 7}),
    ("dim", {0, 3, 6}),
    ("aug", {0, 4, 8}),
    ("7", {0, 4, 7, 10}),
    ("maj7", {0, 4, 7, 11}),
    ("m7", {0, 3, 7, 10}),
)


def chord_label(pitches: set[int]) -> tuple[str, str] | None:
    for root in range(12):
        intervals = {(pitch - root) % 12 for pitch in pitches}
        for suffix, template in TEMPLATES:
            if intervals == template:
                return f"{PITCH_NAMES[root]}{suffix}", suffix or "major"
    return None


def main() -> None:
    if not MANIFEST.is_file():
        raise SystemExit(f"missing mixture manifest: {MANIFEST}")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            grouped[row["path"]].append(row)

    labels: Counter[str] = Counter()
    by_quality: Counter[str] = Counter()
    examples: dict[str, str] = {}
    for path, rows in grouped.items():
        pitches = {int(row["midi"]) % 12 for row in rows}
        detected = chord_label(pitches)
        if detected is None:
            continue
        label, quality = detected
        labels[label] += 1
        by_quality[quality] += 1
        examples.setdefault(label, path)

    print(f"urmp-mixture-windows={len(grouped)}")
    print(f"exact-template-chords={sum(labels.values())}")
    print("by-quality=" + ",".join(
        f"{quality}={count}" for quality, count in sorted(by_quality.items())))
    print("examples=")
    for label in sorted(labels):
        print(f"{label}\tcount={labels[label]}\t{examples[label]}")


if __name__ == "__main__":
    main()
