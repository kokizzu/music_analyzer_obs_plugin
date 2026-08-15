#!/usr/bin/env python3
import csv
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


PROJECT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
SPEC = importlib.util.spec_from_file_location("summary", PROJECT / "scripts" / "summarize_kraisler_measurement.py")
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


FIELDS = [
    "recording", "active_notes", "detected_pcs", "expected_chords", "chord_hit", "simple_chord_hit",
    "bass_notes", "keys_notes", "guitar_notes", "vocal_notes", "other_notes", "amb_notes",
    "keys_visual_notes", "other_visual_notes",
]


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"pieces": [{"configuration": "dry"}]}), encoding="utf-8")
        attributes = root / "attributes.tsv"
        row = {
            "recording": "1", "active_notes": "0:60,40:67", "detected_pcs": "C G", "expected_chords": "C",
            "chord_hit": "1", "simple_chord_hit": "1", "bass_notes": "--", "keys_notes": "C4:1.0",
            "guitar_notes": "--", "vocal_notes": "--", "other_notes": "G4:1.0", "amb_notes": "--",
            "keys_visual_notes": "C4:0.8", "other_visual_notes": "G4:0.8",
        }
        with attributes.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=FIELDS, delimiter="\t")
            writer.writeheader()
            writer.writerow(row)
        rows = {(group, metric): (hit, total) for group, metric, hit, total in SUMMARY.summarize(attributes, manifest)}
        assert rows[("KRAISLER Piano notes", "Exact-MIDI recall")] == (1, 1)
        assert rows[("KRAISLER Violin notes", "Expected instrument row")] == (1, 1)
        assert rows[("All KRAISLER chord windows", "Exact chord accuracy")] == (1, 1)
    print("test_summarize_kraisler_measurement: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
