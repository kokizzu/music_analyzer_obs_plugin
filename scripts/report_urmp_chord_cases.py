#!/usr/bin/env python3
"""Measure global chord labels on annotation-backed URMP mixture windows."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "build" / "urmp_mixture_cases" / "manifest.tsv"
ATTRIBUTES = ROOT / "build" / "urmp_other_recovery_profile.tsv"
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


def expected_chord(pitches: set[int]) -> tuple[str, str] | None:
    for root in range(12):
        intervals = {(pitch - root) % 12 for pitch in pitches}
        for suffix, template in TEMPLATES:
            if intervals == template:
                return f"{PITCH_NAMES[root]}{suffix}", suffix or "major"
    return None


def chord_tokens(label: str) -> set[str]:
    normalized = label.replace("\n", " ").replace("/", " ").replace("=", " ")
    return {token.strip() for token in normalized.split() if token.strip()}


def main() -> None:
    if not MANIFEST.is_file():
        raise SystemExit(f"missing mixture manifest: {MANIFEST}")
    if not ATTRIBUTES.is_file():
        raise SystemExit(
            "missing attribute replay; run `make report-urmp-other-recovery-profile` first")
    pitches_by_path: dict[str, set[int]] = defaultdict(set)
    path_by_id: dict[str, str] = {}
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            pitches_by_path[row["path"]].add(int(row["midi"]) % 12)
            path_by_id[row["id"]] = row["path"]

    labels_by_path: dict[str, set[str]] = defaultdict(set)
    with ATTRIBUTES.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            path = path_by_id.get(row["sample_id"])
            if path is not None:
                labels_by_path[path].update(chord_tokens(row["global_chord"]))

    totals: Counter[str] = Counter()
    hits: Counter[str] = Counter()
    misses: list[tuple[str, str, str]] = []
    for path, pitches in sorted(pitches_by_path.items()):
        detected = expected_chord(pitches)
        if detected is None:
            continue
        label, quality = detected
        totals[quality] += 1
        observed = labels_by_path[path]
        if label in observed:
            hits[quality] += 1
        else:
            misses.append((label, " ".join(sorted(observed)) or "--", path))

    total = sum(totals.values())
    hit_count = sum(hits.values())
    print(f"urmp-exact-chords={total}")
    print(f"global-chord-label={hit_count}/{total} ({(100 * hit_count // total) if total else 0}%)")
    print("by-quality=")
    for quality in sorted(totals):
        print(f"  {quality}={hits[quality]}/{totals[quality]}")
    print("misses=")
    for label, observed, path in misses[:24]:
        print(f"{label}\tobserved={observed}\t{path}")
    if "--verify" in sys.argv:
        required = {"major": 28, "m": 25, "sus2": 3, "sus4": 3, "dim": 2}
        failures = [
            f"{quality} expected at least {minimum}, got {hits[quality]}"
            for quality, minimum in required.items() if hits[quality] < minimum
        ]
        if hit_count < 61:
            failures.append(f"global chord expected at least 61 hits, got {hit_count}")
        if failures:
            raise SystemExit("URMP chord regression:\n" + "\n".join(failures))
        print("status=ready")


if __name__ == "__main__":
    main()
