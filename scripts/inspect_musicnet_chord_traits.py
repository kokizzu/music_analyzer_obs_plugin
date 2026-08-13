#!/usr/bin/env python3
"""Find fully visible MusicNet chord misses that may support ranking fixes."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


def pitch_classes(value: str) -> set[str]:
    if not value or value == "--":
        return set()
    return set(value.split())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_musicnet_chord_traits.py ATTRIBUTE_TSV", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames or []
        print("fields=" + ",".join(fields))
        rows = list(reader)
    misses = [row for row in rows if row.get("chord_hit") == "0"]
    full_visible = [
        row
        for row in misses
        if (expected := pitch_classes(row.get("expected_pcs", "")))
        and expected.issubset(pitch_classes(row.get("detected_pcs", "")))
    ]
    simple_full_visible = [row for row in full_visible if row.get("simple_chord_hit") == "0"]
    print(f"rows={len(rows)} chord_misses={len(misses)}")
    print(
        "full_expected_pitch_class_visible="
        f"{len(full_visible)}/{len(misses)} "
        f"({(100.0 * len(full_visible) / len(misses)) if misses else 0.0:.1f}%)"
    )
    print(f"full_visible_simple_chord_misses={len(simple_full_visible)}")
    routes = Counter(
        (row.get("expected_chords", "--"), row.get("global_chord", "--")) for row in full_visible
    )
    print("top_full_visible_expected_to_global_routes=")
    for (expected, detected), count in routes.most_common(20):
        print(f"{count}\t{expected}\t=>\t{detected}")
    for row in full_visible[:20]:
        details = (
            "recording",
            "center_sample",
            "expected_pcs",
            "detected_pcs",
            "expected_chords",
            "global_chord",
            "keyboard_chord",
            "guitar_chord",
            "other_chord",
            "raw_chroma",
            "detected_levels",
        )
        print("candidate=" + "\t".join(f"{field}={row.get(field, '')}" for field in details))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
