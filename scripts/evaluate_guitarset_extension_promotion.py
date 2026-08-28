#!/usr/bin/env python3
"""Measure conservative primary-label promotion candidates on GuitarSet data."""

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "build/guitarset_attributes.tsv"
NOTE_VALUES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
               "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
               "A#": 10, "Bb": 10, "B": 11}
TEMPLATES = {
    "": (0, 4, 7), "m": (0, 3, 7), "pow": (0, 7), "sus2": (0, 2, 7),
    "sus4": (0, 5, 7), "dim": (0, 3, 6), "aug": (0, 4, 8), "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9), "7": (0, 4, 7, 10), "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10), "dim7": (0, 3, 6, 9), "m7b5": (0, 3, 6, 10),
    "9": (0, 2, 4, 7, 10), "maj9": (0, 2, 4, 7, 11),
    "m9": (0, 2, 3, 7, 10), "add9": (0, 2, 4, 7),
}
CANONICAL_PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def components(label: str) -> list[str]:
    return [component for component in label.split("=") if component and component != "--"]


def expected_components(label: str) -> list[str]:
    return [component for component in label.split("/") if component and component != "--"]


def pitch_classes(value: str) -> set[str]:
    return {pitch_class for pitch_class in value.split(",") if pitch_class}


def is_plain_major_minor(label: str) -> bool:
    if not label:
        return False
    suffix = label[1:]
    if label[1:2] in {"#", "b"}:
        suffix = label[2:]
    return suffix in {"", "m"}


def chord_root(label: str) -> str:
    match = re.match(r"^[A-G](?:#|b)?", label)
    return match.group(0) if match else ""


def chord_pitch_classes(label: str) -> set[str]:
    root = chord_root(label)
    if root not in NOTE_VALUES:
        return set()
    suffix = label[len(root):]
    intervals = TEMPLATES.get(suffix)
    if intervals is None:
        return set()
    return {CANONICAL_PITCH_CLASSES[(NOTE_VALUES[root] + interval) % 12] for interval in intervals}


def normalized_pitch_classes(value: str) -> set[str]:
    return {CANONICAL_PITCH_CLASSES[NOTE_VALUES[pitch_class]] for pitch_class in pitch_classes(value)}


def full_expected_tone_support(row: dict[str, str]) -> bool:
    expected = normalized_pitch_classes(row.get("expected_pitch_classes", ""))
    return bool(expected) and all(
        expected <= normalized_pitch_classes(row.get(column, ""))
        for column in (
            "guitar_pitch_classes",
            "guitar_analysis_pitch_classes",
            "guitar_smoothed_pitch_classes",
        )
    )


def main() -> None:
    if not ATTRIBUTES.exists():
        raise SystemExit("missing GuitarSet attributes; run make analyze-guitarset-attributes first")

    with ATTRIBUTES.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise SystemExit("GuitarSet attributes are empty")

    print("columns", ",".join(rows[0].keys()))
    expected_later = []
    for row in rows:
        label = row.get("guitar_chord", "")
        expected = expected_components(row.get("expected_chords", ""))
        labels = components(label)
        if expected and any(component in labels[1:] for component in expected):
            expected_later.append(row)

    print("expected_later", len(expected_later))
    same_root = [
        row
        for row in expected_later
        if components(row.get("guitar_chord", ""))
        and any(
            chord_root(component) == chord_root(components(row["guitar_chord"])[0])
            for component in expected_components(row.get("expected_chords", ""))
        )
    ]
    same_root_full = [row for row in same_root if full_expected_tone_support(row)]
    print("expected_later_same_root", len(same_root))
    print(
        "expected_later_same_root_full_support",
        len(same_root_full),
        "primary_plain=" + str(sum(
            is_plain_major_minor(components(row["guitar_chord"])[0]) for row in same_root_full
        )),
    )
    for threshold in ("3", "4"):
        eligible = [
            row
            for row in expected_later
            if len(pitch_classes(row.get("expected_pitch_classes", ""))
                   & pitch_classes(row.get("guitar_pitch_classes", ""))) >= int(threshold)
            and len(pitch_classes(row.get("expected_pitch_classes", ""))
                    & pitch_classes(row.get("guitar_analysis_pitch_classes", ""))) >= int(threshold)
            and len(pitch_classes(row.get("expected_pitch_classes", ""))
                    & pitch_classes(row.get("guitar_smoothed_pitch_classes", ""))) >= int(threshold)
        ]
        primary_plain = sum(
            is_plain_major_minor(components(row.get("guitar_chord", ""))[0])
            for row in eligible
        )
        print(
            f"expected_later_v{threshold}_a{threshold}_s{threshold}",
            len(eligible),
            f"primary_plain={primary_plain}",
        )

    quality = Counter(row.get("expected_chord_qualities", "") for row in expected_later)
    print("expected_later_quality", " ".join(f"{name}={count}" for name, count in quality.most_common()))

    promotion_rows = []
    for row in rows:
        labels = components(row.get("guitar_chord", ""))
        if not labels or not is_plain_major_minor(labels[0]):
            continue
        grids = [normalized_pitch_classes(row.get(column, "")) for column in (
            "guitar_pitch_classes", "guitar_analysis_pitch_classes", "guitar_smoothed_pitch_classes",
        )]
        for candidate in labels[1:]:
            tones = chord_pitch_classes(candidate)
            if chord_root(candidate) != chord_root(labels[0]) or not tones:
                continue
            if all(tones <= grid for grid in grids):
                promotion_rows.append((row, candidate))
                break

    gains = 0
    harms = 0
    unresolved = 0
    promoted_quality = Counter()
    for row, candidate in promotion_rows:
        expected = expected_components(row.get("expected_chords", ""))
        current = components(row["guitar_chord"])[0]
        candidate_correct = candidate in expected
        current_correct = current in expected
        if candidate_correct and not current_correct:
            gains += 1
        elif current_correct and not candidate_correct:
            harms += 1
        elif not candidate_correct and not current_correct:
            unresolved += 1
        promoted_quality[row.get("expected_chord_qualities", "")] += 1
    print(
        "conservative_same_root_extension_promotion",
        len(promotion_rows),
        f"gain={gains}",
        f"harm={harms}",
        f"unresolved={unresolved}",
    )
    print("conservative_promotion_quality", " ".join(
        f"{name}={count}" for name, count in promoted_quality.most_common()
    ))

    full_smoothed_misses = [
        row
        for row in rows
        if row.get("status") == "chord_miss"
        and full_expected_tone_support(row)
    ]
    full_smoothed_quality = Counter(
        row.get("expected_chord_qualities", "") for row in full_smoothed_misses
    )
    print(
        "full_expected_support_chord_miss",
        len(full_smoothed_misses),
        "quality=" + " ".join(
            f"{name}={count}" for name, count in full_smoothed_quality.most_common()
        ),
    )
    for row in full_smoothed_misses[:12]:
        print(
            "full_support_miss",
            row.get("recording_id", ""),
            f"@{row.get('center_seconds', '')}s",
            "expected=" + row.get("expected_chords", ""),
            "guitar=" + row.get("guitar_chord", ""),
        )


if __name__ == "__main__":
    main()
