#!/usr/bin/env python3
"""Summarize cached GAPS guitar detector rows without assuming a fixed schema."""

import csv
from collections import Counter
from pathlib import Path


PATH = Path("build/gaps_guitar_attributes.tsv")


def main() -> None:
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        raise SystemExit("no GAPS rows")
    fields = list(rows[0])
    print("fields=" + ",".join(fields))
    print(f"rows={len(rows)}")
    for field in fields:
        lower = field.lower()
        if not any(word in lower for word in ("expected", "got", "detected", "match", "owner", "source", "chord", "note")):
            continue
        values = Counter(row.get(field, "") for row in rows)
        if len(values) <= 32:
            summary = ", ".join(f"{key or '<empty>'}:{value}" for key, value in values.most_common(16))
            print(f"{field}={summary}")

    grouped = {}
    for row in rows:
        quality = row.get("expected_chord_qualities", "<empty>")
        total, hits, notes = grouped.get(quality, (0, 0, 0))
        grouped[quality] = (
            total + 1,
            hits + (row.get("guitar_chord_hit") == "1"),
            notes + int(row.get("guitar_note_hits", "0") or 0),
        )
    print("quality recall")
    for quality, (total, hits, notes) in sorted(grouped.items(), key=lambda item: (item[1][1] / item[1][0], item[1][0])):
        print(f"  {quality}: chord={hits}/{total} notes={notes}/{total}")

    misses = [row for row in rows if row.get("guitar_chord_hit") != "1"]
    print("missed labels")
    for (quality, detected), count in Counter(
        (row.get("expected_chord_qualities", ""), row.get("guitar_chord", "")) for row in misses
    ).most_common(30):
        print(f"  {quality} -> {detected or '--'}: {count}")


if __name__ == "__main__":
    main()
