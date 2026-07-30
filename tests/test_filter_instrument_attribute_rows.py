#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "filter_instrument_attribute_rows.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        rows = write(
            root / "instrument.tsv",
            """
kind	status	family	expected_family	program_name	note	midi	path	detected_expected_row	bass_level	piano_level	guitar_level	vocal_level	other_level	bass_notes	piano_notes	guitar_notes	vocal_notes	other_notes	display_note	display_midi	display_delta	primary_note	primary_midi	primary_delta	debug_note	debug_midi	debug_owner
note	hit	bass	bass	bass	E1	28	bass.wav	1	0.7	0	0	0	0	E1:0.7,E2:0.4	--	--	--	--	E2	40	12	E1	28	0	E2	40	bass
note	hit	piano	piano	piano	C4	60	piano.wav	1	0	0.9	0	0	0	--	C4:0.9	--	--	--	C4	60	0	C4	60	0	C4	60	piano
note	hit	vocals	vocals	vocal	D4	62	vocal.wav	0	0	0	0	0	0	--	--	--	F4:0.7	--	F4	65	3	F4	65	3	F4	65	piano
            """,
        )
        octave = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--pitch-quality",
                "octave_alias",
                "--count-by",
                "family",
                "--count-by",
                "note",
                "--count-by",
                "debug_delta",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "bass\tE1\t12\t1" in octave
        assert "count\t1" in octave

        exact = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--pitch-quality",
                "exact",
                "--columns",
                "family,note,debug_note,debug_delta,pitch_quality",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "family\tnote\tdebug_note\tdebug_delta\tpitch_quality" in exact
        assert "piano\tC4\tC4\t0\texact" in exact
        assert "count\t1" in exact

        other = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--pitch-quality",
                "other_pitch",
                "--count-by",
                "family",
                "--count-by",
                "debug_delta",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "vocals\t3\t1" in other
        assert "count\t1" in other

        display_exact = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--display-pitch-quality",
                "exact",
                "--columns",
                "family,note,display_note,display_delta,display_pitch_quality",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "family\tnote\tdisplay_note\tdisplay_delta\tdisplay_pitch_quality" in display_exact
        assert "piano\tC4\tC4\t0\texact" in display_exact
        assert "count\t1" in display_exact

        primary_exact = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--primary-pitch-quality",
                "exact",
                "--columns",
                "family,note,primary_note,primary_delta,primary_pitch_quality",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "family\tnote\tprimary_note\tprimary_delta\tprimary_pitch_quality" in primary_exact
        assert "bass\tE1\tE1\t0\texact" in primary_exact
        assert "piano\tC4\tC4\t0\texact" in primary_exact
        assert "count\t2" in primary_exact

        duplicates = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--field",
                "target_octave_duplicates=1",
                "--columns",
                "family,note,target_notes,target_distinct_midis,target_octave_duplicates",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "bass\tE1\tE1:0.7,E2:0.4\t2\t1" in duplicates
        assert "count\t1" in duplicates

        note_filter = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--note",
                "E1",
                "--midi",
                "28",
                "--program-name",
                "bass",
                "--columns",
                "family,program_name,note,midi",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "bass\tbass\tE1\t28" in note_filter
        assert "count\t1" in note_filter

        target_visibility = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--kind",
                "note",
                "--columns",
                (
                    "family,note,primary_note,target_expected_visible,"
                    "target_primary_visible,target_lowest_same_pitch_delta"
                ),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "bass\tE1\tE1\t1\t1\t0" in target_visibility
        assert "piano\tC4\tC4\t1\t1\t0" in target_visibility
        assert "vocals\tD4\tF4\t0\t1\t" in target_visibility

        real_note_rows = write(
            root / "real_note.tsv",
            """
status	detected	detected_expected_row	first_row	visual_first_row	sample_id	family	source	expected_note	expected_midi	buffer	mode	bass_level	piano_level	guitar_level	vocal_level	other_level	bass_notes	piano_notes	guitar_notes	vocal_notes	other_notes	debug_note	debug_midi	debug_owner	debug_conf	bass_score	keyboard_score	guitar_score	vocal_score	other_score	pitch_confidence	periodicity	fit_error	centroid	slope	noise	partial2	partial3	partial4	partial5
hit	1	1	vocals	vocals	vocal_a	vocals	acoustic	D4	62	0	full_mix	0	0	0	0.8	0	--	--	--	D4:0.8	--	D4	62	vocals	0.9	0	0	0	0.9	0	0.8	0.75	0.04	0.2	0.3	0.05	0.2	0.1	0.05	0.02
hit	1	0	piano	piano	vocal_b	vocals	acoustic	E4	64	0	full_mix	0	1	0	0	0	--	E4:1.0	--	--	--	E4	64	piano	1	0	1	0	0	0	0.9	0.7	0.03	0.1	0.1	0.02	0.1	0.05	0.02	0.01
            """,
        )
        real_note_filter = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(real_note_rows),
                "--kind",
                "real-note",
                "--family",
                "vocals",
                "--pitch-quality",
                "exact",
                "--columns",
                "kind,family,note,midi,debug_note,debug_delta,pitch_quality,target_expected_visible",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "kind\tfamily\tnote\tmidi\tdebug_note\tdebug_delta\tpitch_quality\ttarget_expected_visible" in real_note_filter
        assert "real-note\tvocals\tD4\t62\tD4\t0\texact\t1" in real_note_filter
        assert "real-note\tvocals\tE4\t64\tE4\t0\texact\t0" in real_note_filter
        assert "count\t2" in real_note_filter

        real_note_count = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(real_note_rows),
                "--kind",
                "real-note",
                "--family",
                "vocals",
                "--count-by",
                "visual_first_row",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "vocals\t1" in real_note_count
        assert "piano\t1" in real_note_count
        assert "count\t2" in real_note_count

    print("test_filter_instrument_attribute_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
