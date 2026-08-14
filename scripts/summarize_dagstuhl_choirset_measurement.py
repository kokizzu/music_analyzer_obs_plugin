#!/usr/bin/env python3
"""Summarize real DCS SATB analyzer windows into auditable x/total metrics."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


NOTE_RE = re.compile(r"^([A-G])(#?)(-?\d+):([0-9.]+)$")
NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ROLE_FOR_PROGRAM = {52: "Soprano", 53: "Alto", 54: "Tenor", 55: "Bass"}
VISUAL_LIT_THRESHOLD = 0.25


def parse_notes(value: str) -> set[int]:
    notes: set[int] = set()
    for token in value.split(","):
        match = NOTE_RE.fullmatch(token.strip())
        if not match:
            continue
        letter, sharp, octave, _level = match.groups()
        notes.add((int(octave) + 1) * 12 + NOTE_OFFSETS[letter] + bool(sharp))
    return notes


def parse_visual_notes(value: str) -> set[int]:
    notes: set[int] = set()
    for token in value.split(","):
        match = NOTE_RE.fullmatch(token.strip())
        if not match:
            continue
        letter, sharp, octave, level = match.groups()
        if float(level) >= VISUAL_LIT_THRESHOLD:
            notes.add((int(octave) + 1) * 12 + NOTE_OFFSETS[letter] + bool(sharp))
    return notes


def parse_active_notes(value: str) -> list[tuple[int, int]]:
    notes: list[tuple[int, int]] = []
    for token in value.split(","):
        try:
            program, midi = token.strip().split(":", 1)
            notes.append((int(program), int(midi)))
        except ValueError:
            continue
    return notes


def add(counter: dict[tuple[str, str], list[int]], group: str, metric: str, hit: bool) -> None:
    values = counter[group, metric]
    values[0] += int(hit)
    values[1] += 1


def manifest_configs(path: Path) -> dict[int, str]:
    pieces = json.loads(path.read_text(encoding="utf-8")).get("pieces", [])
    return {index: str(piece["id"]) for index, piece in enumerate(pieces, start=1)}


def summarize(attributes: Path, manifest: Path) -> list[tuple[str, str, int, int]]:
    configs = manifest_configs(manifest)
    totals: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    with attributes.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"recording", "detected_pcs", "active_notes", "chord_hit", "simple_chord_hit",
                    "expected_chords", "bass_notes", "keys_notes", "guitar_notes", "vocal_notes",
                    "other_notes", "amb_notes", "vocal_visual_notes"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{attributes}: missing columns: {', '.join(sorted(missing))}")
        for row in rows:
            recording = int(row["recording"])
            config = configs.get(recording, f"recording-{recording}")
            detected_pcs = {
                NOTE_OFFSETS[note[0]] + (1 if len(note) > 1 and note[1] == "#" else 0)
                for note in row["detected_pcs"].split()
                if note and note[0] in NOTE_OFFSETS
            }
            all_notes = set().union(*(parse_notes(row[field]) for field in (
                "bass_notes", "keys_notes", "guitar_notes", "vocal_notes", "other_notes", "amb_notes")))
            vocal_notes = parse_notes(row["vocal_notes"])
            vocal_visual_notes = parse_visual_notes(row["vocal_visual_notes"])
            active_notes = parse_active_notes(row["active_notes"])
            expected_pitch_classes = {midi % 12 for _program, midi in active_notes}
            vocal_pitch_classes = {note % 12 for note in vocal_notes}
            visual_vocal_pitch_classes = {note % 12 for note in vocal_visual_notes}

            # The vocal UI intentionally shows one current note, not every
            # simultaneous SATB part. Keep the stricter per-part accounting
            # below, but also measure whether that one display can represent
            # any score-active singer in this analysis window.
            for metric, hit in (
                ("Current-note vocal ownership", bool(expected_pitch_classes & vocal_pitch_classes)),
                ("Visible current-note vocal routing",
                 bool(expected_pitch_classes & visual_vocal_pitch_classes)),
            ):
                add(totals, "All DCS vocal windows", metric, hit)
                add(totals, f"Configuration — {config}", metric, hit)

            for program, midi in active_notes:
                role = ROLE_FOR_PROGRAM.get(program, f"Program {program}")
                groups = ("All SATB notes", f"SATB range — {role}", f"Configuration — {config}")
                metrics = {
                    "Pitch-class recall": midi % 12 in detected_pcs,
                    "Exact-MIDI recall": midi in all_notes,
                    "Vocal ownership": midi % 12 in vocal_pitch_classes,
                    "Visible vocal routing": midi % 12 in visual_vocal_pitch_classes,
                }
                for group in groups:
                    for metric, hit in metrics.items():
                        add(totals, group, metric, hit)
            if row["expected_chords"]:
                for metric, hit in (("Exact chord accuracy", row["chord_hit"] == "1"),
                                    ("Simplified chord accuracy", row["simple_chord_hit"] == "1")):
                    add(totals, "All DCS chord windows", metric, hit)
                    add(totals, f"Configuration — {config}", metric, hit)
    return [(group, metric, hit, total) for (group, metric), (hit, total) in sorted(totals.items())]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attributes", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        rows = summarize(args.attributes, args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, delimiter="\t")
        writer.writerow(("group", "metric", "accurate", "total"))
        writer.writerows(rows)
    print(f"summarize_dagstuhl_choirset_measurement: wrote {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
