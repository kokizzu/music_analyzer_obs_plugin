#!/usr/bin/env python3
"""Summarize exact-MIDI vocal evidence across labelled full-mix corpora."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


NOTE_RE = re.compile(r"^([A-G])(#?)(-?\d+):[0-9.]+$")
NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NOTE_FIELDS = (
    "bass_notes", "guitar_notes", "piano_notes", "keys_notes", "vocal_notes", "other_notes", "amb_notes"
)

# Analyzer attribute rows include comma-separated note evidence.  A long
# evidence history is valid generated data, so retain it rather than failing at
# Python csv's small default field cap while keeping a finite safety bound.
csv.field_size_limit(8 * 1024 * 1024)


def parsed_midis(value: str) -> set[int]:
    result: set[int] = set()
    for token in value.split(","):
        match = NOTE_RE.fullmatch(token.strip())
        if not match:
            continue
        letter, sharp, octave = match.groups()
        result.add((int(octave) + 1) * 12 + NOTE_OFFSETS[letter] + int(bool(sharp)))
    return result


def summarize(inputs: list[tuple[str, Path]]) -> list[tuple[str, int, int, int, int, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for corpus, path in inputs:
        with path.open(encoding="utf-8", newline="") as source:
            rows = csv.DictReader(source, delimiter="\t")
            required = {"family", "expected_midi", "vocal_notes"}
            missing = required - set(rows.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
            for row in rows:
                if row.get("family") != "vocals":
                    continue
                try:
                    midi = int(row["expected_midi"])
                except ValueError:
                    continue
                all_midis: set[int] = set()
                for field in NOTE_FIELDS:
                    all_midis.update(parsed_midis(row.get(field, "")))
                vocal_midis = parsed_midis(row.get("vocal_notes", ""))
                counts[corpus]["total"] += 1
                if midi in vocal_midis:
                    counts[corpus]["exact_vocal"] += 1
                elif midi in all_midis:
                    counts[corpus]["exact_foreign"] += 1
                elif any(candidate % 12 == midi % 12 for candidate in all_midis):
                    counts[corpus]["pitch_class_only"] += 1
                else:
                    counts[corpus]["no_pitch_class"] += 1
    return [
        (corpus, item["exact_vocal"], item["exact_foreign"], item["pitch_class_only"], item["no_pitch_class"], item["total"])
        for corpus, item in sorted(counts.items())
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="CORPUS=TSV")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    inputs: list[tuple[str, Path]] = []
    for value in args.input:
        try:
            corpus, text_path = value.split("=", 1)
        except ValueError:
            parser.error(f"invalid --input `{value}`; expected CORPUS=TSV")
        inputs.append((corpus, Path(text_path)))
    try:
        rows = summarize(inputs)
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))
    header = ("corpus", "exact_vocal", "exact_foreign", "pitch_class_only", "no_pitch_class", "total")
    if args.output is None:
        writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target, delimiter="\t")
            writer.writerow(header)
            writer.writerows(rows)
        print(f"inspect_vocal_exact_note_cross_corpus: wrote {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
