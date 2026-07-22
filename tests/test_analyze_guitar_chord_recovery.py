#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

from test_inspect_guitarset_attribute_buckets import HEADER, ROOT, row


SCRIPT = ROOT / "scripts" / "analyze_guitar_chord_recovery.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "guitarset.tsv"
        rows = [
            row(),
            row(
                status="chord_miss",
                recording_id="visible_and_analysis",
                expected_chords="G",
                guitar_chord="Gpow",
                guitar_pitch_classes="G,D",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_smoothed_pitch_classes="G,D",
                raw_pitch_class_levels="G:1.000,B:0.380,D:0.600",
            ),
            row(
                status="chord_miss",
                recording_id="analysis_only",
                expected_chords="D",
                guitar_chord="--",
                guitar_pitch_classes="D,F#",
                guitar_analysis_pitch_classes="D,A",
                guitar_smoothed_pitch_classes="D,A",
                raw_pitch_class_levels="D:1.000,F#:0.100,A:0.650",
            ),
            row(
                status="chord_miss",
                recording_id="wrong_fifth",
                expected_chords="A",
                guitar_chord="--",
                guitar_pitch_classes="A,E",
                guitar_analysis_pitch_classes="A,D",
                guitar_smoothed_pitch_classes="A,D",
                raw_pitch_class_levels="A:1.000,C#:0.050,E:0.700",
            ),
            row(
                status="chord_miss",
                recording_id="minor_root_fifth",
                expected_chords="Cm",
                guitar_chord="C",
                guitar_pitch_classes="C,G",
                guitar_analysis_pitch_classes="C,D#,G",
                guitar_smoothed_pitch_classes="C,G",
                raw_pitch_class_levels="C:1.000,D#:0.420,G:0.900",
            ),
        ]
        path.write_text(
            "\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--examples", "2"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = completed.stdout
        assert "guitar chord recovery rows=4" in output
        assert "guitar_pitch_classes root+fifth=3" in output
        assert "guitar_analysis_pitch_classes root+fifth=3" in output
        assert "guitar_smoothed_pitch_classes root+fifth=3" in output
        assert "visible+analysis root+fifth=2" in output
        assert "visible_and_analysis expected=G got=Gpow" in output
        assert "raw=1/0.38/0.6" in output
        combined_output = output.split("visible+analysis root+fifth=2", 1)[1]
        assert "minor_root_fifth expected=Cm got=C" in combined_output
        assert "wrong_fifth" not in combined_output
    print("test_analyze_guitar_chord_recovery: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
