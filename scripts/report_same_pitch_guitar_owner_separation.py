#!/usr/bin/env python3
"""Compare same-pitch Guitar-owner evidence for piano versus guitar fixtures."""

import csv
import statistics
from collections import Counter
from pathlib import Path


FIELDS = (
    "onset_strength", "decay_rate", "pitch_stability", "guitar_score", "keyboard_score",
    "other_score", "pitch_confidence", "periodicity", "harmonicity", "fit_error",
    "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5",
)


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "0"))
    except ValueError:
        return 0.0


def selected(path: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row.get("buffer_strongest_row") != "guitar" or row.get("debug_owner") != "guitar":
                continue
            if row.get("debug_midi") != row.get("expected_midi"):
                continue
            result.append(row)
    return result


def electronic_piano_guitar_shadow(row: dict[str, str]) -> bool:
    midi = int(row.get("debug_midi", "-1"))
    return (
        40 <= midi <= 64
        and number(row, "noise") <= 0.040
        and 0.45 <= number(row, "partial2") <= 0.75
        and 0.10 <= number(row, "partial3") <= 0.22
        and number(row, "partial4") <= 0.030
        and number(row, "partial5") <= 0.010
        and 0.12 <= number(row, "centroid") <= 0.30
        and 0.04 <= number(row, "slope") <= 0.24
    )


def profile_variants(row: dict[str, str]) -> dict[str, bool]:
    midi = int(row.get("debug_midi", "-1"))
    second = number(row, "partial2")
    third = number(row, "partial3")
    fourth = number(row, "partial4")
    fifth = number(row, "partial5")
    noise = number(row, "noise")
    return {
        "tight": electronic_piano_guitar_shadow(row),
        "clean": 40 <= midi <= 76 and noise <= 0.040 and 0.35 <= second <= 0.85
        and 0.10 <= third <= 0.28 and fourth <= 0.040 and fifth <= 0.030,
        "clean_wide": 40 <= midi <= 76 and noise <= 0.060 and 0.30 <= second <= 0.95
        and 0.09 <= third <= 0.30 and fourth <= 0.050 and fifth <= 0.040,
        "piano_tine": 40 <= midi <= 76 and noise <= 0.080 and 0.40 <= second <= 0.95
        and 0.10 <= third <= 0.32 and fourth <= 0.060 and fifth <= 0.050,
    }


def report(label: str, rows: list[dict[str, str]]) -> None:
    counts = Counter()
    for row in rows:
        counts.update(name for name, active in profile_variants(row).items() if active)
    print(f"{label} same-pitch guitar-owner buffers={len(rows)} " +
          " ".join(f"{name}={counts[name]}" for name in ("tight", "clean", "clean_wide", "piano_tine")))
    if rows:
        print(label + " medians " + " ".join(
            f"{field}={statistics.median(number(row, field) for row in rows):.3f}"
            for field in FIELDS
        ))


def main() -> int:
    root = Path("build")
    report("piano", selected(root / "real_note_piano_ownership.tsv"))
    report("guitar", selected(root / "real_note_guitar_low_guitar.tsv"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
