#!/usr/bin/env python3
"""Regression check for DCS score-window summary accounting."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize_dagstuhl_choirset_measurement.py"
SPEC = importlib.util.spec_from_file_location("summarize_dcs", SCRIPT)
assert SPEC and SPEC.loader
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"pieces": [{"id": "DCS_Test_Take01"}]}), encoding="utf-8")
        attributes = root / "attributes.tsv"
        attributes.write_text(
            "\t".join((
                "recording", "detected_pcs", "active_notes", "chord_hit", "simple_chord_hit",
                "expected_chords", "bass_notes", "keys_notes", "guitar_notes", "vocal_notes",
                "other_notes", "amb_notes", "vocal_visual_notes",
            )) + "\n" + "\t".join((
                "1", "C E", "52:60,55:40", "1", "1", "C", "", "", "", "C4:1.00", "E4:1.00", "",
                "C4:0.25",
            )) + "\n",
            encoding="utf-8",
        )
        rows = {(group, metric): (hit, total) for group, metric, hit, total in SUMMARY.summarize(attributes, manifest)}
        assert rows[("All SATB notes", "Pitch-class recall")] == (2, 2)
        assert rows[("All SATB notes", "Exact-MIDI recall")] == (1, 2)
        assert rows[("SATB range — Soprano", "Vocal ownership")] == (1, 1)
        assert rows[("SATB range — Bass", "Visible vocal routing")] == (0, 1)
        assert rows[("All DCS vocal windows", "Current-note vocal ownership")] == (1, 1)
        assert rows[("All DCS vocal windows", "Visible current-note vocal routing")] == (1, 1)
        assert rows[("Configuration — DCS_Test_Take01", "Current-note vocal ownership")] == (1, 1)
        assert rows[("All DCS chord windows", "Exact chord accuracy")] == (1, 1)
    print("test_summarize_dagstuhl_choirset_measurement: 8 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
