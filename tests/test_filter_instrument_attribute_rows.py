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
kind	status	family	expected_family	program_name	note	midi	path	detected_expected_row	bass_level	piano_level	guitar_level	vocal_level	other_level	bass_notes	piano_notes	guitar_notes	vocal_notes	other_notes	display_note	display_midi	display_delta	debug_note	debug_midi	debug_owner
note	hit	bass	bass	bass	E1	28	bass.wav	1	0.7	0	0	0	0	E1:0.7,E2:0.4	--	--	--	--	E1	28	0	E2	40	bass
note	hit	piano	piano	piano	C4	60	piano.wav	1	0	0.9	0	0	0	--	C4:0.9	--	--	--	C4	60	0	C4	60	piano
note	hit	vocals	vocals	vocal	D4	62	vocal.wav	0	0	0	0	0	0	--	--	--	F4:0.7	--	F4	65	3	F4	65	piano
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
        assert "bass\tE1\tE1\t0\texact" in display_exact
        assert "piano\tC4\tC4\t0\texact" in display_exact
        assert "count\t2" in display_exact

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

    print("test_filter_instrument_attribute_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
