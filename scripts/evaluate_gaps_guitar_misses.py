#!/usr/bin/env python3
"""Summarize simple-chord misses in the annotated GAPS guitar corpus."""

from collections import Counter, defaultdict
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/gaps_guitar_attributes.tsv"
SIMPLE_QUALITIES = {"maj", "min", "pow"}


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    simple = [row for row in rows if row.get("expected_chord_qualities") in SIMPLE_QUALITIES]
    misses = [row for row in simple if row.get("simple_chord_hit") != "1"]
    print(f"simple_rows={len(simple)} simple_misses={len(misses)}")
    by_quality: dict[str, Counter[str]] = defaultdict(Counter)
    by_note_hits: Counter[str] = Counter()
    for row in simple:
        quality = row.get("expected_chord_qualities", "?")
        by_quality[quality]["total"] += 1
        by_quality[quality]["hit"] += row.get("simple_chord_hit") == "1"
        by_note_hits[row.get("guitar_note_hits", "?")] += row.get("simple_chord_hit") != "1"
    for quality in sorted(by_quality):
        counts = by_quality[quality]
        print(f"{quality}: hit={counts['hit']}/{counts['total']} miss={counts['total'] - counts['hit']}")
    print("misses_by_guitar_note_hits=" + ",".join(
        f"{name}:{count}" for name, count in sorted(by_note_hits.items(), key=lambda item: int(item[0]))
    ))
    print("simple chord misses")
    for row in misses:
        print(
            f"{row.get('expected_chord_qualities', '?'):3} expected={row.get('expected_chords', '?'):14} "
            f"got={row.get('guitar_chord', '?'):42} notes={row.get('guitar_note_hits', '?')}/"
            f"{row.get('expected_note_count', '?')} pcs={row.get('guitar_pitch_classes', '?')} "
            f"smoothed={row.get('guitar_smoothed_pitch_classes', '?')} "
            f"rms={row.get('rms', '?')} sample={row.get('audio_path', '?')}@{row.get('center_seconds', '?')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
