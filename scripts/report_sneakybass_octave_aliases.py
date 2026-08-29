#!/usr/bin/env python3
"""Print probe ratios for external real-bass octave/subharmonic misses."""

import csv
from pathlib import Path


def number(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "0"))
    except ValueError:
        return 0.0


def main() -> int:
    path = Path("build/sneakybass_fixture_attributes.tsv")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    missed = [row for row in rows if row.get("detected_expected_row") != "1"]
    missed.sort(key=lambda row: number(row, "raw_expected_ratio"), reverse=True)
    print(f"sneakybass_octave_alias_misses={len(missed)}")
    for row in missed[:24]:
        print(
            f"articulation={row.get('program_name', '--')}"
            f" expected={row.get('note', '--')}({row.get('midi', '--')})"
            f" display={row.get('bass_label', '--')}"
            f" spectral={row.get('bass_spectral_midi', '--')}"
            f" periodic={row.get('bass_periodic_midi', '--')}"
            f" expected_ratio={row.get('raw_expected_ratio', '--')}"
            f" down={row.get('raw_octave_down_ratio', '--')}"
            f" up={row.get('raw_octave_up_ratio', '--')}"
            f" second_up={row.get('raw_second_octave_up_ratio', '--')}"
            f" rank={row.get('raw_expected_rank', '--')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
