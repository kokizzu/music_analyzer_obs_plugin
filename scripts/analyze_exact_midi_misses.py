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
		"debug_conf", "raw_local_best_midi", "raw_local_best_peak", "raw_expected_peak",
		"raw_expected_rank", "raw_expected_ratio",
		"raw_octave_down_ratio", "raw_octave_up_ratio", "raw_fifth_up_ratio", "raw_second_octave_up_ratio",
		"raw_upper_major_third_ratio", "raw_upper_fifth_ratio", "raw_third_octave_up_ratio",
		"other_pre_envelope_midi", "other_pre_envelope_score", "other_pre_envelope_raw_level",
		"other_raw_candidate_midi", "other_raw_candidate_score", "other_raw_candidate_level",
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


def same_pitch_class_offset(first: dict[str, str], rows: list[dict[str, str]]) -> int | None:
    try:
        expected = int(first["expected_midi"])
    except ValueError:
        return None
    field = ROW_FIELD.get(first["family"])
    if field is None:
        return None
    candidates = [midi for row in rows for midi in notes(row.get(field, ""))
                  if midi % 12 == expected % 12]
    if not candidates:
        return None
    return min(candidates, key=lambda midi: abs(midi - expected)) - expected


def raw_local_offset(first: dict[str, str]) -> int | None:
    try:
        return int(first["raw_local_best_midi"]) - int(first["expected_midi"])
    except ValueError:
        return None


def analyze(path: Path, examples: int, sample_id: str = "", pre_offset: int | None = None,
            same_pc_offset: int | None = None, source: str = "", raw_offset: int | None = None) -> str:
    misses = sample_misses(path)
    if source:
        misses = [(first, rows) for first, rows in misses if first["source"] == source]
    if sample_id:
        selected = [(first, rows) for first, rows in misses if first["sample_id"] == sample_id]
        if not selected:
            return f"exact-midi miss not found for sample_id={sample_id}"
        return "\n".join(trait_text(first, rows) for first, rows in selected)
    if pre_offset is not None:
        selected = []
        for first, rows in misses:
            try:
                if int(first["other_pre_envelope_midi"]) - int(first["expected_midi"]) == pre_offset:
                    selected.append((first, rows))
            except ValueError:
                continue
        return "\n".join(trait_text(first, rows) for first, rows in selected[:examples]) or (
            f"exact-midi misses with pre-envelope offset {pre_offset:+d}: none"
        )
    if same_pc_offset is not None:
        selected = [
            (first, rows) for first, rows in misses
            if same_pitch_class_offset(first, rows) == same_pc_offset
        ]
        return "\n".join(trait_text(first, rows) for first, rows in selected[:examples]) or (
            f"exact-midi misses with displayed pitch-class offset {same_pc_offset:+d}: none"
        )
    if raw_offset is not None:
        selected = [(first, rows) for first, rows in misses if raw_local_offset(first) == raw_offset]
        return "\n".join(trait_text(first, rows) for first, rows in selected[:examples]) or (
            f"exact-midi misses with raw local-best offset {raw_offset:+d}: none"
        )
    by_family: collections.Counter[str] = collections.Counter()
    by_source: collections.Counter[str] = collections.Counter()
    by_expected_octave: collections.Counter[int] = collections.Counter()
    same_pc_offset: collections.Counter[str] = collections.Counter()
    raw_local_offsets: collections.Counter[str] = collections.Counter()
    pre_envelope_offset: collections.Counter[str] = collections.Counter()
    raw_rank: collections.Counter[str] = collections.Counter()
    example_rows: list[str] = []

    for first, rows in misses:
        family = first["family"]
        expected = int(first["expected_midi"])
        by_family[family] += 1
        by_source[f"{family}/{first['source']}"] += 1
        by_expected_octave[(expected // 12) - 1] += 1

        offset = same_pitch_class_offset(first, rows)
        if offset is not None:
            same_pc_offset[f"{offset:+d}"] += 1
        else:
            same_pc_offset["none"] += 1

        local_offset = raw_local_offset(first)
        if local_offset is not None:
            raw_local_offsets[f"{local_offset:+d}"] += 1
        else:
            raw_local_offsets["none"] += 1
        try:
            pre_envelope = int(first.get("other_pre_envelope_midi", ""))
            pre_envelope_offset[f"{pre_envelope - expected:+d}"] += 1
        except ValueError:
            pre_envelope_offset["none"] += 1
        raw_rank[first.get("raw_expected_rank", "none") or "none"] += 1

        if len(example_rows) < examples:
            example_rows.append(
                "  {sample} expected={note}/{midi} row={family} source={source} "
                "same_pc={same_pc} raw_best={best} rank={rank} "
                "raw_expected_ratio={ratio}".format(
                    sample=first["sample_id"], note=first["expected_note"], midi=expected,
                    family=family, source=first["source"],
                    same_pc=(offset if offset is not None else "none"),
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
        f"raw local-best MIDI offset {counter_text(raw_local_offsets)}",
        f"other pre-envelope MIDI offset {counter_text(pre_envelope_offset)}",
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
    parser.add_argument("--pre-offset", type=int)
    parser.add_argument("--same-pc-offset", type=int)
    parser.add_argument("--source", default="")
    parser.add_argument("--raw-offset", type=int)
    args = parser.parse_args()
    print(analyze(args.input, args.examples, args.sample_id, args.pre_offset, args.same_pc_offset,
                  args.source, args.raw_offset))


if __name__ == "__main__":
    main()
