#!/usr/bin/env python3
"""Compare external bass fixture labels with spectral, periodic, and rendered states."""

import csv
from collections import Counter
from pathlib import Path


def integer(row: dict[str, str], key: str) -> int:
    try:
        return int(row.get(key, "-1"))
    except ValueError:
        return -1


def main() -> int:
    path = Path("build/sneakybass_fixture_attributes.tsv")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    counts = Counter()
    examples: list[dict[str, str]] = []
    for row in rows:
        expected = integer(row, "midi")
        spectral = integer(row, "bass_spectral_midi")
        periodic = integer(row, "bass_periodic_midi")
        detected = row.get("detected_expected_row") == "1"
        counts["spectral_expected"] += spectral == expected
        counts["periodic_expected"] += periodic == expected
        counts["detected"] += detected
        if spectral == expected and not detected:
            examples.append(row)
    print(f"rows={len(rows)}")
    for key in ("spectral_expected", "periodic_expected", "detected"):
        print(f"{key}={counts[key]}/{len(rows)}")
    print(f"spectral_expected_but_not_rendered={len(examples)}")
    for row in examples[:24]:
        print(
            f"expected={row.get('note', '--')}({row.get('midi', '--')})"
            f" label={row.get('bass_label', '--')}"
            f" grid={row.get('bass_notes', '--')}"
            f" spectral={row.get('bass_spectral_midi', '--')}"
            f" periodic={row.get('bass_periodic_midi', '--')}"
            f" spectral_conf={row.get('bass_spectral_confidence', '--')}"
            f" periodic_conf={row.get('bass_periodic_confidence', '--')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
