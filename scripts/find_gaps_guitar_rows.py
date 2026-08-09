#!/usr/bin/env python3
"""Select concise expanded-GAPS rows by expected and detected chord labels."""

import argparse
import csv


FIELDS = (
    "recording_id", "center_seconds", "audio_path", "status", "expected_chords",
    "guitar_chord", "guitar_raw_chord", "guitar_smoothed_chord",
    "expected_pitch_classes", "guitar_pitch_classes", "guitar_cells",
    "guitar_analysis_pitch_classes", "guitar_analysis_cells",
    "guitar_smoothed_pitch_classes", "guitar_smoothed_cells",
    "expected_quality_raw_profile", "raw_pitch_class_levels",
    "guitar_probe_pitch_class_levels", "guitar_detection_pitch_class_levels",
)


def labels(text, separator):
    return set(part for part in (text or "").split(separator) if part and part != "--")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--missing", default="")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("tsv", nargs="?", default="build/gaps_guitar_full_attributes.tsv")
    args = parser.parse_args()

    matches = []
    with open(args.tsv, newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            if args.expected not in labels(row.get("expected_chords"), "/"):
                continue
            if args.missing and args.missing in labels(row.get("guitar_chord"), "="):
                continue
            matches.append(row)

    print("\t".join(FIELDS))
    for row in matches[:args.limit]:
        print("\t".join(row.get(field, "") for field in FIELDS))
    print(f"rows {len(matches)}", flush=True)


if __name__ == "__main__":
    main()
