#!/usr/bin/env python3
"""Measure whether analysis-only guitar pitch classes are safe display recoveries."""

import argparse
import collections
import csv
import re


NOTE_TO_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def cells(text):
    values = {}
    for entry in (text or "").split(","):
        match = re.match(r"([A-G](?:#)?)(?:-?\d+)?:([0-9.]+)$", entry)
        if match:
            pc = NOTE_TO_PC[match.group(1)]
            values[pc] = max(values.get(pc, 0.0), float(match.group(2)))
    return values


def expected_pitch_classes(text):
    return {NOTE_TO_PC[note] for note in (text or "").split(",") if note in NOTE_TO_PC}


def is_missing_major_triad_flat_seventh(display, pitch_class):
    """Return whether pitch_class is the omitted b7 of a rendered major triad."""
    return any(
        pitch_class == (root + 10) % 12 and
        all(display.get((root + interval) % 12, 0.0) > 0.0 for interval in (0, 4, 7))
        for root in range(12)
    )


def is_missing_major_triad_sixth(display, pitch_class):
    """Return whether pitch_class is the omitted sixth of a rendered major triad."""
    return any(
        pitch_class == (root + 9) % 12 and
        all(display.get((root + interval) % 12, 0.0) > 0.0 for interval in (0, 4, 7))
        for root in range(12)
    )


def is_missing_minor_triad_sixth(display, pitch_class):
    """Return whether pitch_class is the omitted sixth of a rendered minor triad."""
    return any(
        pitch_class == (root + 9) % 12 and
        all(display.get((root + interval) % 12, 0.0) > 0.0 for interval in (0, 3, 7))
        for root in range(12)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-floor", type=float, default=0.30)
    parser.add_argument("--raw-floor", type=float, default=0.0)
    parser.add_argument("--detection-floor", type=float, default=0.0)
    parser.add_argument("--probe-floor", type=float, default=0.0)
    parser.add_argument("--melodic-floor", type=float, default=0.0)
    parser.add_argument("--display-ceiling", type=float, default=0.0)
    parser.add_argument("--min-visible-pitch-classes", type=int, default=0)
    parser.add_argument("--max-visible-pitch-classes", type=int, default=12)
    parser.add_argument("--missing-major-triad-flat-seventh", action="store_true")
    parser.add_argument("--missing-major-triad-sixth", action="store_true")
    parser.add_argument("--missing-minor-triad-sixth", action="store_true")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("tsv", nargs="?", default="build/gaps_guitar_full_attributes.tsv")
    args = parser.parse_args()

    true_rows = []
    false_rows = []
    by_level = collections.Counter()
    with open(args.tsv, newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            display = cells(row.get("guitar_cells"))
            analysis = cells(row.get("guitar_analysis_cells"))
            raw = cells(row.get("raw_pitch_class_levels"))
            detection = cells(row.get("guitar_detection_pitch_class_levels"))
            probe = cells(row.get("guitar_probe_pitch_class_levels"))
            melodic = cells(row.get("guitar_melodic_probe_pitch_class_levels"))
            expected = expected_pitch_classes(row.get("expected_pitch_classes"))
            if not args.min_visible_pitch_classes <= len(display) <= args.max_visible_pitch_classes:
                continue
            for pitch_class, level in analysis.items():
                raw_level = raw.get(pitch_class, 0.0)
                detection_level = detection.get(pitch_class, 0.0)
                probe_level = probe.get(pitch_class, 0.0)
                melodic_level = melodic.get(pitch_class, 0.0)
                if (level < args.analysis_floor or raw_level < args.raw_floor or
                        detection_level < args.detection_floor or
                        probe_level < args.probe_floor or melodic_level < args.melodic_floor or
                        display.get(pitch_class, 0.0) > args.display_ceiling):
                    continue
                if (args.missing_major_triad_flat_seventh and
                        not is_missing_major_triad_flat_seventh(display, pitch_class)):
                    continue
                if (args.missing_major_triad_sixth and
                        not is_missing_major_triad_sixth(display, pitch_class)):
                    continue
                if (args.missing_minor_triad_sixth and
                        not is_missing_minor_triad_sixth(display, pitch_class)):
                    continue
                item = (row, pitch_class, level, raw_level, detection_level, probe_level, melodic_level)
                (true_rows if pitch_class in expected else false_rows).append(item)
                by_level[round(level, 1)] += 1

    print(f"candidates {len(true_rows) + len(false_rows)} expected {len(true_rows)} "
          f"false {len(false_rows)} precision "
          f"{len(true_rows) / (len(true_rows) + len(false_rows)) if true_rows or false_rows else 0:.2%}")
    print("analysis-level buckets " + " ".join(
        f"{level:.1f}={count}" for level, count in sorted(by_level.items())))
    for tag, rows in (("expected", true_rows), ("false", false_rows)):
        for row, pitch_class, level, raw_level, detection_level, probe_level, melodic_level in rows[:args.limit]:
            note = next(name for name, value in NOTE_TO_PC.items() if value == pitch_class)
            print(f"{tag} {row['recording_id']}@{row['center_seconds']} note={note} "
                  f"analysis={level:.2f} raw={raw_level:.2f} detection={detection_level:.2f} probe={probe_level:.2f} "
                  f"melodic={melodic_level:.2f} expected={row['expected_pitch_classes']} "
                  f"visible={row['guitar_pitch_classes']} visible_count={len(cells(row['guitar_cells']))} "
                  f"chord={row['guitar_chord']}")


if __name__ == "__main__":
    main()
