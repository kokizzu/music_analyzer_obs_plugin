#!/usr/bin/env python3
"""Measure octave/harmonic display aliases in real-note full-mix TSV rows."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import pathlib
import re
import sys


NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")
NOTE_BASE = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

ROW_NOTE_FIELDS = {
    "bass": ("bass_visual_notes", "bass_notes"),
    "guitar": ("guitar_visual_notes", "guitar_notes"),
    "piano": ("piano_visual_notes", "piano_notes"),
    "vocals": ("vocal_visual_notes", "vocal_notes"),
    "other": ("other_visual_notes", "other_notes"),
    "amb": ("amb_visual_notes", "amb_notes"),
}

EXPECTED_ROW = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
    "strings": "other",
    "synth": "other",
}

HARMONIC_INTERVALS = (12, 19, 24, 28, 31, 36, 40, 43, 47, 48, 49, 51, 52, 55, 57, 58, 60)


@dataclass(frozen=True)
class NoteLevel:
    row: str
    note: str
    midi: int
    level: float


@dataclass(frozen=True)
class Alias:
    shadow: NoteLevel
    support: NoteLevel
    interval: int


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def pitch_class(midi: int) -> int:
    return (midi % 12 + 12) % 12


def parse_note_levels(row: dict[str, str], row_name: str) -> list[NoteLevel]:
    fields = ROW_NOTE_FIELDS.get(row_name)
    if not fields:
        return []

    value = ""
    for field in fields:
        value = row.get(field, "")
        if value:
            break

    notes: list[NoteLevel] = []
    seen: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part or part == "--":
            continue
        note, _, level_text = part.partition(":")
        note = note.strip()
        midi = midi_from_note(note)
        if midi is None:
            continue
        try:
            level = float(level_text) if level_text else 1.0
        except ValueError:
            level = 0.0
        if midi in seen:
            continue
        seen.add(midi)
        notes.append(NoteLevel(row_name, note, midi, level))
    return notes


def expected_row(row: dict[str, str]) -> str:
    family = row.get("family", "")
    return EXPECTED_ROW.get(family, family or "unknown")


def source_key(row: dict[str, str]) -> str:
    family = row.get("family", "") or "unknown"
    source = row.get("source", "") or row.get("nsynth_family", "") or "unknown"
    return f"{family}/{source}"


def group_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("sample_id", ""), row.get("buffer", "")


def interval_supported(interval: int, mode: str, tolerance: int) -> bool:
    if interval <= 0:
        return False
    if mode == "octave":
        return interval % 12 == 0
    if mode == "same-pitch-class":
        return interval % 12 == 0
    return any(abs(interval - candidate) <= tolerance for candidate in HARMONIC_INTERVALS)


def find_alias(
    row: dict[str, str],
    shadow_row: str,
    support_rows: list[str],
    min_shadow_level: float,
    min_support_level: float,
    min_interval: int,
    max_interval: int,
    interval_mode: str,
    interval_tolerance: int,
) -> Alias | None:
    shadows = parse_note_levels(row, shadow_row)
    supports: list[NoteLevel] = []
    for support_row in support_rows:
        supports.extend(parse_note_levels(row, support_row))

    best: Alias | None = None
    best_score = -1.0
    for shadow in shadows:
        if shadow.level < min_shadow_level:
            continue
        for support in supports:
            if support.level < min_support_level:
                continue
            interval = shadow.midi - support.midi
            if interval < min_interval or interval > max_interval:
                continue
            if interval_mode in {"octave", "same-pitch-class"} and pitch_class(shadow.midi) != pitch_class(support.midi):
                continue
            if not interval_supported(interval, interval_mode, interval_tolerance):
                continue
            score = (shadow.level - support.level * 0.5) + interval * 0.001
            if score > best_score:
                best = Alias(shadow, support, interval)
                best_score = score
    return best


def read_groups(path: pathlib.Path) -> dict[tuple[str, str], list[dict[str, str]]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            groups[group_key(row)].append(row)
    return groups


def first_group_row(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        return {}
    return rows[0]


def print_counter(label: str, counter: Counter[str], top: int) -> None:
    if not counter:
        print(f"{label} --")
        return
    print(label, " ".join(f"{key}={value}" for key, value in counter.most_common(top)))


def alias_text(alias: Alias) -> str:
    return (
        f"{alias.shadow.row}:{alias.shadow.note}:{alias.shadow.level:.2f}"
        f"<-{alias.support.row}:{alias.support.note}:{alias.support.level:.2f}"
        f"/+{alias.interval}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--shadow-row", choices=sorted(ROW_NOTE_FIELDS), default="guitar")
    parser.add_argument(
        "--support-row",
        action="append",
        dest="support_rows",
        choices=sorted(ROW_NOTE_FIELDS),
        help="support row to compare against; repeatable",
    )
    parser.add_argument("--min-shadow-level", type=float, default=0.68)
    parser.add_argument("--min-support-level", type=float, default=0.45)
    parser.add_argument("--min-interval", type=int, default=12)
    parser.add_argument("--max-interval", type=int, default=60)
    parser.add_argument(
        "--interval-mode",
        choices=("octave", "same-pitch-class", "harmonic"),
        default="same-pitch-class",
    )
    parser.add_argument("--interval-tolerance", type=int, default=1)
    parser.add_argument("--examples", type=int, default=6)
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    support_rows = args.support_rows or ["piano", "other"]
    if args.shadow_row in support_rows:
        print("shadow row must not also be a support row", file=sys.stderr)
        return 2

    groups = read_groups(args.path)
    alias_groups = 0
    positive_visual = 0
    protected_visual = 0
    other_alias = 0
    positive_routes: Counter[str] = Counter()
    protected_routes: Counter[str] = Counter()
    alias_routes: Counter[str] = Counter()
    interval_counts: Counter[str] = Counter()
    examples: list[str] = []
    protected_examples: list[str] = []

    for rows in groups.values():
        row = first_group_row(rows)
        alias = find_alias(
            row,
            args.shadow_row,
            support_rows,
            args.min_shadow_level,
            args.min_support_level,
            args.min_interval,
            args.max_interval,
            args.interval_mode,
            args.interval_tolerance,
        )
        if alias is None:
            continue

        alias_groups += 1
        expected = expected_row(row)
        visual_first = row.get("visual_first_row", "") or row.get("first_row", "")
        route = f"{source_key(row)}->{args.shadow_row}"
        alias_routes[route] += 1
        interval_counts[str(alias.interval)] += 1

        example = (
            f"{row.get('sample_id', '')}@{row.get('buffer', '')}"
            f" expected={expected}/{row.get('expected_note', '')}"
            f" visual={visual_first} alias={alias_text(alias)}"
        )
        if visual_first == args.shadow_row and expected != args.shadow_row:
            positive_visual += 1
            positive_routes[route] += 1
            if len(examples) < args.examples:
                examples.append(example)
        elif visual_first == args.shadow_row and expected == args.shadow_row:
            protected_visual += 1
            protected_routes[route] += 1
            if len(protected_examples) < args.examples:
                protected_examples.append(example)
        else:
            other_alias += 1

    print(
        "measure_real_note_octave_display_aliases:"
        f" groups={len(groups)} alias_groups={alias_groups}"
        f" positive_visual={positive_visual} protected_visual={protected_visual}"
        f" other_alias={other_alias}"
    )
    print_counter("positive_routes", positive_routes, args.top)
    print_counter("protected_routes", protected_routes, args.top)
    print_counter("alias_routes", alias_routes, args.top)
    print_counter("intervals", interval_counts, args.top)
    for example in examples:
        print(f"positive_example\t{example}")
    for example in protected_examples:
        print(f"protected_example\t{example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
