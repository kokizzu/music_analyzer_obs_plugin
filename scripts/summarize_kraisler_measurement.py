#!/usr/bin/env python3
"""Summarize KRAISLER piano/violin mixture measurements as x/total rows."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from summarize_dagstuhl_choirset_measurement import parse_notes, parse_visual_notes


PIANO_PROGRAM = 0
VIOLIN_PROGRAM = 40


def active_notes(value: str) -> list[tuple[int, int]]:
    parsed = []
    for token in value.split(","):
        try:
            program, midi = token.strip().split(":", 1)
            parsed.append((int(program), int(midi)))
        except ValueError:
            continue
    return parsed


def add(counter: dict[tuple[str, str], list[int]], group: str, metric: str, hit: bool) -> None:
    values = counter[group, metric]
    values[0] += int(hit)
    values[1] += 1


def configurations(manifest: Path) -> dict[int, str]:
    pieces = json.loads(manifest.read_text(encoding="utf-8")).get("pieces", [])
    return {index: str(piece.get("configuration", "unknown")) for index, piece in enumerate(pieces, start=1)}


def summarize(attributes: Path, manifest: Path) -> list[tuple[str, str, int, int]]:
    configs = configurations(manifest)
    totals: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    with attributes.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {
            "recording", "active_notes", "detected_pcs", "expected_chords", "chord_hit", "simple_chord_hit",
            "bass_notes", "keys_notes", "guitar_notes", "vocal_notes", "other_notes", "amb_notes",
            "keys_visual_notes", "other_visual_notes",
        }
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{attributes}: missing columns: {', '.join(sorted(missing))}")
        for row in rows:
            config = configs.get(int(row["recording"]), "unknown")
            detected_pcs = {token for token in row["detected_pcs"].split() if token}
            detected_pc_numbers = {
                note % 12
                for field in ("bass_notes", "keys_notes", "guitar_notes", "vocal_notes", "other_notes", "amb_notes")
                for note in parse_notes(row[field])
            }
            exact_notes = set().union(*(parse_notes(row[field]) for field in (
                "bass_notes", "keys_notes", "guitar_notes", "vocal_notes", "other_notes", "amb_notes")))
            key_notes = parse_notes(row["keys_notes"])
            other_notes = parse_notes(row["other_notes"])
            key_visual = parse_visual_notes(row["keys_visual_notes"])
            other_visual = parse_visual_notes(row["other_visual_notes"])
            for program, midi in active_notes(row["active_notes"]):
                if program == PIANO_PROGRAM:
                    expected_row, expected_visual, name = key_notes, key_visual, "Piano"
                elif program == VIOLIN_PROGRAM:
                    expected_row, expected_visual, name = other_notes, other_visual, "Violin"
                else:
                    continue
                groups = ("All KRAISLER notes", f"KRAISLER {name} notes", f"Configuration — {config}")
                metrics = {
                    "Pitch-class recall": midi % 12 in detected_pc_numbers,
                    "Exact-MIDI recall": midi in exact_notes,
                    "Expected instrument row": midi % 12 in {note % 12 for note in expected_row},
                    "Visible expected instrument row": midi % 12 in {note % 12 for note in expected_visual},
                }
                for group in groups:
                    for metric, hit in metrics.items():
                        add(totals, group, metric, hit)
            if row["expected_chords"]:
                for metric, hit in (
                    ("Exact chord accuracy", row["chord_hit"] == "1"),
                    ("Simplified chord accuracy", row["simple_chord_hit"] == "1"),
                ):
                    add(totals, "All KRAISLER chord windows", metric, hit)
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
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, delimiter="\t")
        writer.writerow(("group", "metric", "accurate", "total"))
        writer.writerows(rows)
    print(f"summarize_kraisler_measurement: wrote {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
