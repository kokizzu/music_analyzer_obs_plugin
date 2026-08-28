#!/usr/bin/env python3
"""Audit whether high raw bass notes can be safely recovered in full mixes."""

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "build/good_sounds_full_mix_attributes.tsv",
    ROOT / "build/real_note_full_mix_attributes.tsv",
)


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as source:
        yield from csv.DictReader(source, delimiter="\t")


def value(row, *names):
    for name in names:
        candidate = row.get(name, "").strip()
        if candidate:
            return candidate
    return ""


def integer(row, *names):
    try:
        return int(value(row, *names))
    except ValueError:
        return -1


def main() -> None:
    for path in FILES:
        if not path.is_file():
            print(f"missing {path.relative_to(ROOT)}")
            continue
        all_rows = list(rows(path))
        headers = tuple(all_rows[0]) if all_rows else ()
        print(f"--- {path.relative_to(ROOT)} rows={len(all_rows)}")
        print("fields=" + ",".join(
            field for field in headers
            if any(token in field.lower() for token in ("sample", "expected", "owner", "strongest", "midi", "status"))))
        candidates = []
        for row in all_rows:
            sample_id = value(row, "sample_id", "id", "source")
            expected_midi = integer(row, "expected_midi", "midi")
            status = value(row, "status")
            owner = value(row, "buffer_strongest_row", "first_row", "debug_owners")
            if "bass" in sample_id.lower() and expected_midi >= 56 and status == "ownership_miss":
                candidates.append((expected_midi, owner))
        print(f"high_bass_ownership_misses={len(candidates)}")
        print("owner_counts=" + ", ".join(
            f"{owner}:{count}" for owner, count in Counter(owner for _, owner in candidates).most_common()))


if __name__ == "__main__":
    main()
