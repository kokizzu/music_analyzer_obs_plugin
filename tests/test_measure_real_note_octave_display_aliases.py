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
status	detected	detected_expected_row	first_row	visual_first_row	sample_id	family	source	expected_note	expected_midi	buffer	mode	bass_visual_notes	guitar_visual_notes	piano_visual_notes	vocal_visual_notes	other_visual_notes
hit	1	1	guitar	guitar	keyboard_alias	piano	electronic	A1	33	0	full_mix	A2:0.60	A3:0.72	A1:0.80,A2:0.62	--	--
hit	1	1	guitar	guitar	guitar_true	guitar	acoustic	A2	45	0	full_mix	--	A3:0.74	A2:0.58	--	--
hit	1	1	other	other	other_harm	other	acoustic	C3	48	0	full_mix	--	--	G4:0.72,C6:0.91	--	C3:0.80
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
        assert "groups=3 alias_groups=2 positive_visual=1 protected_visual=1" in octave
        assert "positive_routes piano/electronic->guitar=1" in octave
        assert "protected_routes guitar/acoustic->guitar=1" in octave
        assert "positive_example\tkeyboard_alias@0" in octave

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
        assert "groups=3 alias_groups=1 positive_visual=0 protected_visual=0 other_alias=1" in harmonic
        assert "alias_routes other/acoustic->piano=1" in harmonic
        assert "intervals 36=1" in harmonic

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
