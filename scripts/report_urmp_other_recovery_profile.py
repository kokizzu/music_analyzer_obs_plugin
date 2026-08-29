#!/usr/bin/env python3
"""Measure a candidate generic-mix Other-row recovery profile on URMP fixtures."""

from __future__ import annotations

import csv
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from subprocess import run
from time import monotonic


ROOT = Path(__file__).resolve().parent.parent
ANALYZER = ROOT / "build" / "analyzer_real_note_samples"
FIXTURES = ROOT / "build" / "urmp_mixture_cases"
ATTRIBUTES = ROOT / "build" / "urmp_other_recovery_profile.tsv"


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, ValueError):
        return 0.0


def enabled(value: str) -> bool:
    return value in {"1", "true", "yes"}


def is_sustained_other_candidate(row: dict[str, str]) -> bool:
    """Profile for a voice where generic timbre ownership is genuinely uncertain."""
    if not row["source"].startswith("urmpmix-") or row["source"] == "urmpmix-db":
        return False
    if row["debug_owner"] != "piano":
        return False
    if not row["debug_midi"]:
        return False
    if int(row["debug_midi"]) % 12 != int(row["expected_midi"]) % 12:
        return False
    return (
        55 <= int(row["debug_midi"]) <= 88
        and number(row, "keyboard_score") >= 0.80
        and number(row, "guitar_score") <= 0.05
        and number(row, "vocal_score") <= 0.05
        and number(row, "other_score") <= 0.05
        and number(row, "spectral_level") >= 0.45
        and number(row, "pitch_confidence") >= 0.12
        and number(row, "periodicity") >= 0.55
        and number(row, "fit_error") <= 0.10
        and number(row, "noise") <= 0.42
        and 0.06 <= number(row, "centroid") <= 0.20
        and 0.01 <= number(row, "slope") <= 0.22
        and number(row, "partial2") <= 0.24
        and number(row, "partial3") <= 0.16
        and number(row, "partial4") <= 0.14
        and number(row, "partial5") <= 0.08
    )


def export_attributes() -> None:
    if not ANALYZER.is_file():
        raise SystemExit(f"missing analyzer test binary: {ANALYZER}")
    if not FIXTURES.is_dir():
        raise SystemExit(f"missing URMP mixture fixtures: {FIXTURES}")
    environment = os.environ.copy()
    environment.update(
        {
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT": str(FIXTURES),
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES": "1",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
            "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
            "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
        }
    )
    result = run([str(ANALYZER)], cwd=ROOT, env=environment, check=False,
                 capture_output=True, text=True)
    if result.returncode:
        print(result.stdout, end="")
        print(result.stderr, end="")
        raise SystemExit(result.returncode)


def main() -> None:
    started = monotonic()
    if "--reuse" not in sys.argv:
        export_attributes()
    elif not ATTRIBUTES.is_file():
        raise SystemExit(f"missing reusable attributes: {ATTRIBUTES}")
    outcomes: dict[str, dict[str, bool | str]] = defaultdict(
        lambda: {"hit": False, "profile": False, "source": ""})
    eligible_by_source: Counter[str] = Counter()
    with ATTRIBUTES.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            if not row["source"].startswith("urmpmix-"):
                continue
            key = row["sample_id"]
            outcomes[key]["source"] = row["source"]
            outcomes[key]["hit"] = outcomes[key]["hit"] or enabled(row["detected_expected_row"])
            if is_sustained_other_candidate(row):
                outcomes[key]["profile"] = True
                eligible_by_source[row["source"]] += 1

    expected_other = {
        key: outcome for key, outcome in outcomes.items()
        if outcome["source"] != "urmpmix-db"
    }
    total = len(expected_other)
    current_hits = sum(outcome["hit"] for outcome in expected_other.values())
    misses = [key for key, outcome in expected_other.items() if not outcome["hit"]]
    recovered = [key for key in misses if outcomes[key]["profile"]]
    print(f"urmp-other-mixtures={total}")
    print(f"current-other-row={current_hits}/{total}")
    print(f"ownership-misses={len(misses)}")
    print(f"profile-recoverable={len(recovered)}/{len(misses)}")
    print(f"projected-other-row={current_hits + len(recovered)}/{total}")
    print("profile-by-instrument=" + ",".join(
        f"{source}={count}" for source, count in sorted(eligible_by_source.items())))
    print(f"duration-seconds={monotonic() - started:.2f}")


if __name__ == "__main__":
    main()
