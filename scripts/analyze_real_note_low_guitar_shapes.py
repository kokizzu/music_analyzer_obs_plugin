#!/usr/bin/env python3
"""Compare the broad low-guitar mirror shape across piano and guitar fixtures."""

import csv
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "guitar_score", "other_score", "pitch_confidence", "periodicity", "fit_error",
    "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5",
)


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "0"))
    except ValueError:
        return 0.0


def shared_low_guitar_shape(row: dict[str, str]) -> bool:
    return (
        row.get("debug_owner") == "other"
        and int(row.get("debug_midi", "-1")) <= 52
        and number(row, "pitch_confidence") >= 0.50
        and number(row, "periodicity") >= 0.65
        and number(row, "fit_error") <= 0.20
        and 0.18 <= number(row, "noise") <= 0.70
        and number(row, "partial2") >= 0.25
        and number(row, "partial3") >= 0.18
        and number(row, "partial4") >= 0.050
    )


def run_family(family: str) -> int:
    output = ROOT / "build" / f"real_note_{family}_low_guitar.tsv"
    env = os.environ.copy()
    env.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER": family,
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(output),
    })
    completed = subprocess.run(
        [str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT, env=env,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    print(f"{family} runner exit={completed.returncode}")
    if completed.returncode:
        print(completed.stdout, end="")
        return completed.returncode

    by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    with output.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            by_sample[row["sample_id"]].append(row)
    shaped = []
    for sample_id, rows in by_sample.items():
        matching = [row for row in rows if shared_low_guitar_shape(row)]
        if matching:
            shaped.append(matching[0])
    print(f"{family} fixtures={len(by_sample)} broad_low_guitar_shape={len(shaped)}")
    if shaped:
        print(f"{family} medians " + " ".join(
            f"{field}={statistics.median(number(row, field) for row in shaped):.3f}"
            for field in FIELDS
        ))
        for row in sorted(shaped, key=lambda item: item["sample_id"])[:12]:
            print(f"{family} " + " ".join(
                f"{field}={row.get(field, '')}" for field in (
                    "sample_id", "source", "expected_note", "expected_midi", "buffer", *FIELDS,
                )
            ))
    return 0


def main() -> int:
    for family in ("piano", "guitar"):
        result = run_family(family)
        if result:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
