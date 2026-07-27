#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

from test_inspect_guitarset_attribute_buckets import HEADER, ROOT, row


SCRIPT = ROOT / "scripts" / "analyze_guitar_primary_order.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "guitarset.tsv"
        rows = [
            row(),
            row(
                recording_id="later_am",
                expected_chords="Am",
                expected_chord_qualities="min",
                guitar_chord="C=C6=Am7=Cmaj7=Am",
                guitar_raw_chord="Am=C=C6=Am7=Cmaj7",
                guitar_smoothed_chord="C=C6=Am7=Cmaj7=Am",
                guitar_pitch_classes="C,E",
                guitar_cells="C3:1.00,E3:0.80",
                guitar_analysis_pitch_classes="C,E,G,A",
                guitar_analysis_cells="C3:1.00,E3:0.80,G3:0.70,A3:0.90",
            ),
            row(
                recording_id="invalid_power_minor",
                expected_chords="Am",
                expected_chord_qualities="min",
                guitar_chord="A=E=Apow=Am",
                guitar_raw_chord="A=E=Apow=Am",
                guitar_smoothed_chord="A=E=Apow=Am",
                guitar_pitch_classes="E,A",
                guitar_cells="E3:1.00,A2:0.70",
                guitar_analysis_pitch_classes="E,A",
                guitar_analysis_cells="E3:1.00,A2:0.70",
            ),
            row(
                recording_id="miss",
                status="chord_miss",
                expected_chords="D",
                expected_chord_qualities="maj",
                chord_hit="0",
                simple_chord_hit="0",
                guitar_chord_hit="0",
                guitar_chord="--",
                guitar_raw_chord="--",
                guitar_smoothed_chord="--",
                guitar_pitch_classes="D,A",
                guitar_analysis_pitch_classes="D,A",
                guitar_smoothed_pitch_classes="D,A",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--examples", "4"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = completed.stdout
        assert "guitar_chord: primary=1/4 later=2 miss=1" in output
        assert "guitar_raw_chord: primary=2/4 later=1 miss=1" in output
        assert "guitar_smoothed_chord: primary=1/4 later=2 miss=1" in output
        assert (
            "guitar_primary_order: rows=4 primary_misses=2 expected_later=2 "
            "score_promotable=1 cpp_promotable=0"
        ) in output
        assert "gap=0.125 expected=Am primary=C" in output
        assert "invalid_power_minor" not in output
    print("test_analyze_guitar_primary_order: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
