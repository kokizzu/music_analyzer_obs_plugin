#!/usr/bin/env python3
"""Assert that verified real-audio GAPS guitar recovery cases remain labeled."""

import csv
import sys


CASES = (
    ("239_wy1wc", 19.3797, "Cmaj7"),
    ("317_5V1wc", 298.9810, "Apow"),
    ("232_m41wc", 11.4057, "Gpow"),
    ("117_cD1wc", 101.8670, "Em"),
    ("100_Lf1wc", 9.34531, "Gadd9"),
    ("241_ly1wc", 33.3016, "Gpow"),
)
NOTE_CASES = (
    ("004_JSswc", 84.5896, "G#"),
    ("351_8k1wc", 65.3151, "G#"),
    ("106_nf1wc", 27.3042, "E"),
    ("047_xc1wc", 8.33437, "G"),
)
TIME_TOLERANCE_SECONDS = 0.01


def main(path):
    rows = list(csv.DictReader(open(path, newline=""), delimiter="\t"))
    failures = []
    for recording_id, center_seconds, expected_label in CASES:
        matches = [
            row for row in rows
            if row["recording_id"] == recording_id and
            abs(float(row["center_seconds"]) - center_seconds) <= TIME_TOLERANCE_SECONDS
        ]
        if len(matches) != 1:
            failures.append(f"{recording_id}@{center_seconds}: expected one row, got {len(matches)}")
            continue
        labels = set(part for part in matches[0]["guitar_chord"].split("=") if part)
        if expected_label not in labels:
            failures.append(
                f"{recording_id}@{center_seconds}: expected {expected_label}, got "
                f"{matches[0]['guitar_chord']}")
    for recording_id, center_seconds, expected_note in NOTE_CASES:
        matches = [
            row for row in rows
            if row["recording_id"] == recording_id and
            abs(float(row["center_seconds"]) - center_seconds) <= TIME_TOLERANCE_SECONDS
        ]
        if len(matches) != 1:
            failures.append(f"{recording_id}@{center_seconds}: expected one note row, got {len(matches)}")
            continue
        visible_notes = set(part for part in matches[0]["guitar_pitch_classes"].split(",") if part)
        if expected_note not in visible_notes:
            failures.append(
                f"{recording_id}@{center_seconds}: expected visible {expected_note}, got "
                f"{matches[0]['guitar_pitch_classes']}")
    if failures:
        for failure in failures:
            print(f"check_gaps_guitar_regressions: {failure}", file=sys.stderr)
        return 1
    print(f"check_gaps_guitar_regressions: ok ({len(CASES)} chord and {len(NOTE_CASES)} note real-audio cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_gaps_guitar_regressions.py <attributes.tsv>")
    raise SystemExit(main(sys.argv[1]))
