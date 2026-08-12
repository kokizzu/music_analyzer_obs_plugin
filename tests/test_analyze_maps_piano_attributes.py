#!/usr/bin/env python3
"""Regression checks for MAPS piano chord-miss trait summaries."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "analyze_maps_piano_attributes.py"
SPEC = importlib.util.spec_from_file_location("analyze_maps_piano_attributes", MODULE_PATH)
assert SPEC and SPEC.loader
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


HEADER = "\t".join(
    (
        "missing_pcs", "extra_pcs", "expected_pcs", "detected_keyboard_pcs", "expected_midis",
        "detected_keyboard_midis", "expected_chords", "chord_hit", "keyboard_chord",
        "detected_chord_pcs", "chord_debug", "audio_rms", "audio_peak", "recording", "center_sample",
    )
)


class MapsPianoAttributeSummaryTest(unittest.TestCase):
    def test_midi_level_harmonic_aliases_are_parsed(self) -> None:
        levels = SUMMARY.midi_levels("48:0.800,60:0.320,67:0.250,broken")
        self.assertEqual({48: 0.8, 60: 0.32, 67: 0.25}, levels)
        self.assertEqual({60, 67}, SUMMARY.harmonic_aliases([48, 60, 67], levels, 0.5))

    def test_complete_pitch_chord_misses_are_traced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "maps.tsv"
            source.write_text(
                "\n".join(
                    (
                        HEADER,
                        "--\t--\tC,E,G\tC,E,G\t60,64,67\t60,64,67\tC\t0\tCpow\tC,G\tclusters=3 templates=2 conflicts=0 selected=1\t0.1\t0.2\t1\t10",
                        "F\t--\tD,F,A\tD,A\t62,65,69\t62,69\tDm\t0\t--\tD,A\tclusters=2 templates=2 conflicts=0 selected=0\t0.1\t0.2\t2\t20",
                        "--\t--\tE,G#,B\tE,G#,B\t64,68,71\t64,68,71\tE\t1\tE\tE,G#,B\tclusters=3 templates=0 conflicts=0 selected=1\t0.1\t0.2\t3\t30",
                        "A\t--\tA\t--\t69\t\t\t0\t--\t\tno-pitch\t0.01\t0.2\t4\t40",
                    )
                ) + "\n",
                encoding="utf-8",
            )
            lines = SUMMARY.summarize(source, 12)

        self.assertIn("chord misses with every expected pitch class visible=1/2", lines)
        self.assertIn("complete-pitch missed expected chord labels C=1", lines)
        self.assertIn("keyboard labels on complete-pitch chord misses Cpow=1", lines)
        self.assertTrue(
            any(line.startswith("complete-pitch chord miss examples 1@10 expected=C keyboard=Cpow") for line in lines)
        )
        self.assertIn(
            "isolated-note miss examples 4@40 expected=A detected=-- midis=-- levels=-- rms=0.01 peak=0.2",
            lines,
        )
        self.assertIn(
            "loudest isolated-note miss examples 4@40 expected=A detected=-- midis=-- levels=-- rms=0.01 peak=0.2",
            lines,
        )
        self.assertIn("low-MIDI miss upper-partial routes none", lines)
        self.assertTrue(any(
            line.startswith(
                "isolated harmonic-alias pruning simulation lower/upper>=0.25: "
                "removed=0 recall=0/1 (0.0%) precision=--"
            )
            for line in lines
        ))


if __name__ == "__main__":
    unittest.main()
