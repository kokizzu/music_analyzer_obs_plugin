#!/usr/bin/env python3
"""Convert DCS score windows into the common real-note pattern-mining schema."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
ROLE_FOR_PROGRAM = {52: "soprano", 53: "alto", 54: "tenor", 55: "bass"}
ROW_FIELDS = {
    "bass": "bass_notes",
    "piano": "keys_notes",
    "guitar": "guitar_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
    "amb": "amb_notes",
}
VISUAL_ROW_FIELDS = {name: field.replace("_notes", "_visual_notes") for name, field in ROW_FIELDS.items()}
NOTE_RE = re.compile(r"^([A-G])(#?)(-?\d+):([0-9.]+)$")
NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
DEBUG_OWNER_NAMES = {"keys": "piano"}
OUTPUT_FIELDS = (
    "status", "detected", "detected_anywhere", "detected_expected_row", "first_row", "visual_first_row",
    "sample_id", "family", "nsynth_family", "source", "expected_note", "expected_midi", "buffer", "mode",
    "bass_notes", "guitar_notes", "piano_notes", "vocal_notes", "other_notes", "amb_notes",
    "bass_visual_notes", "guitar_visual_notes", "piano_visual_notes", "vocal_visual_notes", "other_visual_notes", "amb_visual_notes",
    "raw_octave_down_ratio",
    "debug_note", "debug_midi", "debug_owner", "debug_conf", "bass_score", "keyboard_score", "guitar_score",
    "vocal_score", "other_score", "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error",
    "centroid", "slope", "noise", "adjacent_lower_ratio", "adjacent_upper_ratio", "third_octave_ratio",
    "partial1", "partial2", "partial3", "partial4", "partial5", "harmonic_product_score",
    "lower_subharmonic_product_ratio", "vocal_tone_profile", "vocal_rejected_polyphony",
)


def midi_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def parse_active_notes(value: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for token in value.split(","):
        try:
            program, midi = token.strip().split(":", 1)
            result.append((int(program), int(midi)))
        except ValueError:
            continue
    return result


def parse_note_cells(value: str) -> list[tuple[int, float]]:
    result: list[tuple[int, float]] = []
    for token in value.split(","):
        match = NOTE_RE.fullmatch(token.strip())
        if not match:
            continue
        letter, sharp, octave, level = match.groups()
        result.append(((int(octave) + 1) * 12 + NOTE_OFFSETS[letter] + bool(sharp), float(level)))
    return result


def candidate_evidence(value: str) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for item in value.split(";"):
        fields = item.split(",")
        try:
            midi = int(fields[0])
        except (IndexError, ValueError):
            continue
        if len(fields) >= 12:
            result[midi] = fields
    return result


def configs(manifest: Path) -> dict[int, str]:
    pieces = json.loads(manifest.read_text(encoding="utf-8")).get("pieces", [])
    return {index: str(piece["id"]) for index, piece in enumerate(pieces, start=1)}


def best_matching_row(row: dict[str, str], midi: int, fields: dict[str, str], threshold: float = 0.0) -> str:
    pitch_class = midi % 12
    matches: list[tuple[float, str]] = []
    for name, field in fields.items():
        for note_midi, level in parse_note_cells(row.get(field, "")):
            if note_midi % 12 == pitch_class and level >= threshold:
                matches.append((level, name))
    if not matches:
        return ""
    # Prefer the expected vocal row when it is tied: this represents the row
    # actually relevant to a score-aligned vocal ownership observation.
    return max(matches, key=lambda item: (item[0], item[1] == "vocals"))[1]


def export_rows(attributes: Path, manifest: Path) -> list[dict[str, str]]:
    config_by_recording = configs(manifest)
    result: list[dict[str, str]] = []
    with attributes.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"recording", "center_sample", "active_notes", "candidate_evidence", *ROW_FIELDS.values(), *VISUAL_ROW_FIELDS.values()}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{attributes}: missing columns: {', '.join(sorted(missing))}")
        for source_row in rows:
            source_name = config_by_recording.get(int(source_row["recording"]), f"recording-{source_row['recording']}")
            evidence = candidate_evidence(source_row["candidate_evidence"])
            for program, midi in parse_active_notes(source_row["active_notes"]):
                first_row = best_matching_row(source_row, midi, ROW_FIELDS)
                visual_first_row = best_matching_row(source_row, midi, VISUAL_ROW_FIELDS, 0.25)
                expected_hit = first_row == "vocals"
                detected = bool(first_row)
                candidate = evidence.get(midi, [])
                row = {field: "" for field in OUTPUT_FIELDS}
                row.update({
                    "status": "hit" if expected_hit else ("ownership_miss" if detected else "miss"),
                    "detected": str(int(detected)), "detected_anywhere": str(int(detected)),
                    "detected_expected_row": str(int(expected_hit)), "first_row": first_row,
                    "visual_first_row": visual_first_row,
                    "sample_id": f"{source_name}/window-{source_row['center_sample']}/{ROLE_FOR_PROGRAM.get(program, str(program))}",
                    "family": "vocals", "nsynth_family": "vocal", "source": source_name,
                    "expected_note": midi_name(midi), "expected_midi": str(midi), "buffer": source_row["center_sample"],
                    "mode": "full_mix",
                    # This ratio is derived entirely from the analyzed audio at
                    # the candidate pitch.  It lets a later ownership audit
                    # distinguish a physical high voice from a lower-octave
                    # fundamental whose upper harmonic was selected.
                    "raw_octave_down_ratio": candidate[12] if len(candidate) >= 13 else "",
                })
                for name, field in ROW_FIELDS.items():
                    output_name = "vocal" if name == "vocals" else name
                    row[f"{output_name}_notes"] = source_row.get(field, "")
                    row[f"{output_name}_visual_notes"] = source_row.get(VISUAL_ROW_FIELDS[name], "")
                if candidate:
                    row.update({
                        "debug_note": midi_name(midi), "debug_midi": str(midi),
                        "debug_owner": DEBUG_OWNER_NAMES.get(candidate[1], candidate[1]),
                        "debug_conf": candidate[2], "bass_score": candidate[3], "keyboard_score": candidate[4],
                        "guitar_score": candidate[5], "vocal_score": candidate[6], "other_score": candidate[7],
                        "pitch_confidence": candidate[8], "periodicity": candidate[9],
                        "vocal_tone_profile": candidate[10], "vocal_rejected_polyphony": candidate[11],
                    })
                    if len(candidate) >= 27:
                        row.update({
                            "spectral_level": candidate[13], "harmonicity": candidate[14], "fit_error": candidate[15],
                            "centroid": candidate[16], "slope": candidate[17], "noise": candidate[18],
                            "adjacent_lower_ratio": candidate[19], "adjacent_upper_ratio": candidate[20],
                            "third_octave_ratio": candidate[21], "partial1": candidate[22], "partial2": candidate[23],
                            "partial3": candidate[24], "partial4": candidate[25], "partial5": candidate[26],
                        })
                    if len(candidate) >= 29:
                        row.update({
                            "harmonic_product_score": candidate[27],
                            "lower_subharmonic_product_ratio": candidate[28],
                        })
                result.append(row)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attributes", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        rows = export_rows(args.attributes, args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"export_dagstuhl_choirset_pattern_rows: wrote {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
