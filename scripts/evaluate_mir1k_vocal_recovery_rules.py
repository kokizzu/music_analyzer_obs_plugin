#!/usr/bin/env python3
"""Evaluate conservative real-vocal recovery envelopes against protected fixtures."""

from __future__ import annotations

import csv
import pathlib


MIR_PATH = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_attributes.tsv")
REFERENCE_PATH = pathlib.Path("build/real_note_full_mix_attributes.tsv")


def load(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expected(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("debug_midi", "") == row.get("expected_midi", "")]


def value(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0"))
    except ValueError:
        return 0.0


def matches(row: dict[str, str], rule: dict[str, tuple[float, float]]) -> bool:
    if row.get("vocal_tone_profile") == "1":
        return False
    return all(minimum <= value(row, key) <= maximum for key, (minimum, maximum) in rule.items())


RULES = {
    "A": {
        "debug_midi": (55, 74), "pitch_confidence": (.82, 1), "periodicity": (.72, 1),
        "fit_error": (0, .18), "centroid": (.10, .40), "slope": (.04, .55), "noise": (.02, .30),
        "partial2": (.12, .90), "partial3": (.03, .45), "partial4": (0, .25), "partial5": (0, .15),
    },
    "B": {
        "debug_midi": (55, 74), "pitch_confidence": (.78, 1), "periodicity": (.68, 1),
        "fit_error": (0, .24), "centroid": (.08, .44), "slope": (.03, .70), "noise": (.01, .34),
        "partial2": (.10, 1.20), "partial3": (.02, .65), "partial4": (0, .32), "partial5": (0, .20),
    },
    "C": {
        "debug_midi": (55, 69), "pitch_confidence": (.82, 1), "periodicity": (.72, 1),
        "fit_error": (0, .20), "centroid": (.12, .38), "slope": (.05, .48), "noise": (.02, .28),
        "partial2": (.18, .90), "partial3": (.04, .42), "partial4": (.01, .22), "partial5": (0, .14),
    },
    "D": {
        "debug_midi": (60, 74), "pitch_confidence": (.84, 1), "periodicity": (.74, 1),
        "fit_error": (0, .15), "centroid": (.10, .32), "slope": (.04, .38), "noise": (.01, .22),
        "partial2": (.12, .70), "partial3": (.03, .32), "partial4": (0, .18), "partial5": (0, .10),
    },
}


def main() -> int:
    mir = [row for row in expected(load(MIR_PATH)) if row.get("debug_owner") != "vocals"]
    reference = expected(load(REFERENCE_PATH))
    print(f"MIR missed vocal windows: {len(mir)}")
    for name, rule in RULES.items():
        positive = sum(matches(row, rule) for row in mir)
        protected = {
            family: sum(matches(row, rule) for row in reference if row.get("family") == family)
            for family in ("bass", "guitar", "piano", "other")
        }
        total_protected = sum(protected.values())
        precision = positive / (positive + total_protected) if positive + total_protected else 0.0
        print(f"{name}: mir={positive}/{len(mir)} protected={total_protected} "
              f"precision={precision:.3f} "
              + " ".join(f"{family}={count}" for family, count in protected.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
