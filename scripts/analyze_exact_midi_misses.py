#!/usr/bin/env python3
"""Summarize exact-MIDI misses from a real-note attribute TSV."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path


NOTE_OFFSETS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
                "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
ROW_FIELD = {"bass": "bass_notes", "guitar": "guitar_notes", "piano": "piano_notes",
             "vocals": "vocal_notes", "other": "other_notes"}
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+):([0-9.]+)$")


def note_midi(token: str) -> int | None:
    match = NOTE_RE.fullmatch(token.strip())
    if not match:
        return None
    return (int(match.group(2)) + 1) * 12 + NOTE_OFFSETS[match.group(1)]


def notes(value: str) -> list[int]:
    return [midi for token in value.split(",") if (midi := note_midi(token)) is not None]


def sample_misses(path: Path) -> list[tuple[dict[str, str], list[dict[str, str]]]]:
    samples: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            samples[row["sample_id"]].append(row)

    misses = []
    for rows in samples.values():
        first = rows[0]
        field = ROW_FIELD.get(first["family"])
        try:
            expected = int(first["expected_midi"])
        except ValueError:
            continue
        if field and not any(expected in notes(row.get(field, "")) for row in rows):
            misses.append((first, rows))
    return misses


def counter_text(counter: collections.Counter, limit: int = 16) -> str:
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit)) or "none"


def trait_text(first: dict[str, str], rows: list[dict[str, str]]) -> str:
    fields = (
		"buffer", "expected_note", "expected_midi", "debug_note", "debug_midi", "debug_owner",
		"debug_conf", "raw_local_best_midi", "raw_expected_peak", "raw_expected_rank", "raw_expected_ratio",
		"raw_octave_up_ratio", "raw_fifth_up_ratio", "raw_second_octave_up_ratio",
		"raw_upper_major_third_ratio", "raw_upper_fifth_ratio", "raw_third_octave_up_ratio",
		"other_pre_envelope_midi", "other_pre_envelope_score", "other_pre_envelope_raw_level",
        "other_score", "bass_score", "guitar_score", "keyboard_score", "vocal_score",
        "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error",
        "centroid", "slope", "noise", "partial1", "partial2", "partial3", "partial4", "partial5",
    )
    header = (
        f"traits {first['sample_id']} expected={first['expected_note']}/{first['expected_midi']} "
        f"family={first['family']} source={first['source']}"
    )
    lines = [header]
    for row in rows:
        values = " ".join(f"{field}={row.get(field, '')}" for field in fields)
        lines.append(f"  {values} {ROW_FIELD[first['family']]}={row.get(ROW_FIELD[first['family']], '')}")
    return "\n".join(lines)


def analyze(path: Path, examples: int, sample_id: str = "") -> str:
    misses = sample_misses(path)
    if sample_id:
        selected = [(first, rows) for first, rows in misses if first["sample_id"] == sample_id]
        if not selected:
            return f"exact-midi miss not found for sample_id={sample_id}"
        return "\n".join(trait_text(first, rows) for first, rows in selected)
    by_family: collections.Counter[str] = collections.Counter()
    by_source: collections.Counter[str] = collections.Counter()
    by_expected_octave: collections.Counter[int] = collections.Counter()
    same_pc_offset: collections.Counter[str] = collections.Counter()
    raw_local_offset: collections.Counter[str] = collections.Counter()
    raw_rank: collections.Counter[str] = collections.Counter()
    example_rows: list[str] = []

    for first, rows in misses:
        family = first["family"]
        expected = int(first["expected_midi"])
        by_family[family] += 1
        by_source[f"{family}/{first['source']}"] += 1
        by_expected_octave[(expected // 12) - 1] += 1

        field = ROW_FIELD[family]
        candidates = [midi for row in rows for midi in notes(row.get(field, ""))
                      if midi % 12 == expected % 12]
        if candidates:
            closest = min(candidates, key=lambda midi: abs(midi - expected))
            same_pc_offset[f"{closest - expected:+d}"] += 1
        else:
            same_pc_offset["none"] += 1

        try:
            local_best = int(first.get("raw_local_best_midi", ""))
            raw_local_offset[f"{local_best - expected:+d}"] += 1
        except ValueError:
            raw_local_offset["none"] += 1
        raw_rank[first.get("raw_expected_rank", "none") or "none"] += 1

        if len(example_rows) < examples:
            example_rows.append(
                "  {sample} expected={note}/{midi} row={family} source={source} "
                "same_pc={same_pc} raw_best={best} rank={rank} "
                "raw_expected_ratio={ratio}".format(
                    sample=first["sample_id"], note=first["expected_note"], midi=expected,
                    family=family, source=first["source"],
                    same_pc=(closest - expected if candidates else "none"),
                    best=first.get("raw_local_best_midi", "none"),
                    rank=first.get("raw_expected_rank", "none"),
                    ratio=first.get("raw_expected_ratio", "none"),
                )
            )

    lines = [
        f"exact-midi misses {len(misses)}",
        f"by family {counter_text(by_family)}",
        f"by source {counter_text(by_source)}",
        f"by expected octave {counter_text(by_expected_octave)}",
        f"expected-row same-pitch-class MIDI offset {counter_text(same_pc_offset)}",
        f"raw local-best MIDI offset {counter_text(raw_local_offset)}",
        f"raw expected rank {counter_text(raw_rank)}",
        "examples:",
        *example_rows,
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--examples", type=int, default=12)
    parser.add_argument("--sample-id", default="")
    args = parser.parse_args()
    print(analyze(args.input, args.examples, args.sample_id))


if __name__ == "__main__":
    main()
