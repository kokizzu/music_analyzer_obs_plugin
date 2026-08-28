#!/usr/bin/env python3
"""Measure restoration of analysis-supported plain guitar triad tones on GAPS."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/gaps_guitar_attributes.tsv"
PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
ROOT_INDEX = {name: index for index, name in enumerate(PITCH_CLASSES)}
MIN_CONFIDENCES = (0.36, 0.48, 0.58, 0.68, 0.80)


def pitch_classes(value: str) -> set[str]:
    return {item for item in value.split(",") if item and item != "--"}


def primary_plain_triad(label: str) -> tuple[str, set[str]] | None:
    primary = label.split("=", 1)[0]
    for root in sorted(PITCH_CLASSES, key=len, reverse=True):
        if not primary.startswith(root):
            continue
        suffix = primary[len(root):]
        if suffix == "":
            intervals = (0, 4, 7)
        elif suffix == "m":
            intervals = (0, 3, 7)
        else:
            return None
        root_index = ROOT_INDEX[root]
        tones = {PITCH_CLASSES[(root_index + interval) % 12] for interval in intervals}
        return primary, tones
    return None


def expected_simple_components(value: str) -> set[str]:
    return {component for component in value.split("/") if primary_plain_triad(component) is not None}


@dataclass
class Result:
    rows: int = 0
    correct_primary_rows: int = 0
    incorrect_primary_rows: int = 0
    correct_added: int = 0
    false_added: int = 0
    no_add_rows: int = 0

    def render(self) -> str:
        return (f"rows={self.rows} correct_primary_rows={self.correct_primary_rows} "
                f"incorrect_primary_rows={self.incorrect_primary_rows} "
                f"correct_added={self.correct_added} false_added={self.false_added} "
                f"no_add_rows={self.no_add_rows}")


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row.get("instrument") == "guitar"]

    print(f"guitar_rows={len(rows)}")
    for minimum_confidence in MIN_CONFIDENCES:
        result = Result()
        examples: list[str] = []
        for row in rows:
            triad = primary_plain_triad(row["guitar_raw_chord"])
            if triad is None or float(row["guitar_raw_chord_confidence"] or 0.0) < minimum_confidence:
                continue
            _, tones = triad
            analysis = pitch_classes(row["guitar_analysis_pitch_classes"])
            displayed = pitch_classes(row["guitar_pitch_classes"])
            if len(analysis) > 6 or len(tones & analysis) < 3 or len(tones & displayed) < 2:
                continue
            additions = (tones & analysis) - displayed
            result.rows += 1
            if not additions:
                result.no_add_rows += 1
                continue
            expected_components = expected_simple_components(row["expected_chords"])
            primary = row["guitar_raw_chord"].split("=", 1)[0]
            correct_primary = primary in expected_components
            if correct_primary:
                result.correct_primary_rows += 1
            else:
                result.incorrect_primary_rows += 1
            expected = pitch_classes(row["expected_pitch_classes"])
            result.correct_added += len(additions & expected)
            result.false_added += len(additions - expected)
            if len(examples) < 10:
                examples.append(
                    f"conf={row['guitar_raw_chord_confidence']} primary={primary} "
                    f"expected={row['expected_chords']} add={','.join(sorted(additions))} "
                    f"correct_primary={int(correct_primary)} sample={Path(row['audio_path']).name}@{row['center_seconds']}"
                )
        print(f"min_confidence={minimum_confidence:.2f} {result.render()}")
        for example in examples:
            print("  " + example)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
