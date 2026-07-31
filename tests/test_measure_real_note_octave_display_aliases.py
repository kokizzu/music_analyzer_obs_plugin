#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "measure_real_note_octave_display_aliases.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        rows = write(
            pathlib.Path(tmpdir) / "real-note.tsv",
            """
status	detected	detected_expected_row	first_row	visual_first_row	sample_id	family	source	expected_note	expected_midi	buffer	mode	bass_visual_notes	guitar_visual_notes	piano_visual_notes	vocal_visual_notes	other_visual_notes	debug_midi	debug_owner	raw_expected_ratio	pitch_confidence	guitar_score	keyboard_score	other_score
hit	1	1	guitar	guitar	keyboard_alias	piano	electronic	A1	33	0	full_mix	A2:0.60	A3:0.72	A1:0.80,A2:0.62	--	--	57	other	1.20	0.71	0.12	0.10	0.88
hit	1	1	guitar	guitar	guitar_true	guitar	acoustic	A2	45	0	full_mix	--	A3:0.74	A2:0.58	--	--	57	guitar	0.96	0.88	0.79	0.31	0.10
hit	1	1	other	other	other_harm	other	acoustic	C3	48	0	full_mix	--	--	G4:0.72,C6:0.91	--	C3:0.80	84	other	1.44	0.63	0.12	0.35	0.74
hit	1	1	guitar	guitar	guitar_non_alias_risk	guitar	electric	B2	47	0	full_mix	--	B2:0.76	--	--	--	47	other	1.08	0.81	0.18	0.16	0.82
            """,
        )

        octave = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--shadow-row",
                "guitar",
                "--support-row",
                "piano",
                "--support-row",
                "bass",
                "--interval-mode",
                "same-pitch-class",
                "--examples",
                "4",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "groups=4 alias_groups=2 positive_visual=1 protected_visual=1" in octave
        assert "positive_routes piano/electronic->guitar=1" in octave
        assert "protected_routes guitar/acoustic->guitar=1" in octave
        assert "positive_example\tkeyboard_alias@0" in octave

        profiled = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--shadow-row",
                "guitar",
                "--support-row",
                "piano",
                "--support-row",
                "bass",
                "--interval-mode",
                "same-pitch-class",
                "--examples",
                "4",
                "--details",
                "--detail-field",
                "raw_expected_ratio",
                "--detail-field",
                "pitch_confidence",
                "--profile",
                "--profile-field",
                "interval",
                "--profile-field",
                "shadow_level:0.05",
                "--profile-field",
                "level_delta:0.05",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "positive_profile interval 12=1" in profiled
        assert "protected_profile shadow_level 0.70-0.75=1" in profiled
        assert "positive_profile level_delta 0.10-0.15=1" in profiled
        assert "positive_example\tsample_id=keyboard_alias" in profiled
        assert "raw_expected_ratio=1.20" in profiled
        assert "pitch_confidence=0.71" in profiled

        searched = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--shadow-row",
                "guitar",
                "--support-row",
                "piano",
                "--support-row",
                "bass",
                "--interval-mode",
                "same-pitch-class",
                "--details",
                "--detail-field",
                "raw_expected_ratio",
                "--threshold-search",
                "--search-min-positive",
                "1",
                "--search-limit",
                "2",
                "--search-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "threshold_search: candidates=" in searched
        assert "positive_total=1 protected_total=1 row_protected_total=2 other_total=0" in searched
        assert "threshold_rule positive=1/1 protected=0/1 row_protected=0/2" in searched
        assert "debug_relation=shadow" in searched
        assert "threshold_positive\tsample_id=keyboard_alias" in searched

        harmonic = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--shadow-row",
                "piano",
                "--support-row",
                "other",
                "--interval-mode",
                "harmonic",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "groups=4 alias_groups=1 positive_visual=0 protected_visual=0 other_alias=1" in harmonic
        assert "alias_routes other/acoustic->piano=1" in harmonic
        assert "intervals 36=1" in harmonic

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
