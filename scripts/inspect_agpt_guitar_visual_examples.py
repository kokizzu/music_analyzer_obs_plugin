#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


PATH = Path("build/agpt_guitar_full_mix_attributes.tsv")


def main() -> int:
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        count = 0
        for row in rows:
            if row["visual_first_row"] != "guitar":
                continue
            print(
                "sample={sample}\texpected={expected}\tvisual_notes={notes}\tdetected_expected_row={detected}".format(
                    sample=row["sample_id"],
                    expected=row["expected_note"],
                    notes=row["guitar_visual_notes"],
                    detected=row["detected_expected_row"],
                )
            )
            count += 1
            if count == 8:
                break
    if count == 0:
        raise SystemExit("no AG-PT Guitar visual-primary rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
