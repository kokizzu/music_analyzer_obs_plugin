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
                audio_path="later_am.wav",
                expected_chords="Am",
                expected_chord_qualities="min",
                guitar_chord="C=C6=Am7=Cmaj7=Am",
                guitar_raw_chord="Am=C=C6=Am7=Cmaj7",
                guitar_smoothed_chord="C=C6=Am7=Cmaj7=Am",
                guitar_chord_confidence="0.20",
                guitar_raw_chord_confidence="0.80",
                guitar_smoothed_chord_confidence="0.30",
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
                recording_id="same_root_quality_rescue",
                audio_path="same_root_quality_rescue.wav",
                expected_chords="A#",
                expected_chord_qualities="maj",
                guitar_chord="A#m=F=A#pow=A#",
                guitar_raw_chord="A#m=F=A#pow=A#",
                guitar_smoothed_chord="A#=A#pow=A#m",
                guitar_chord_confidence="0.58",
                guitar_raw_chord_confidence="0.58",
                guitar_smoothed_chord_confidence="0.58",
                guitar_pitch_classes="F,A,A#",
                guitar_cells="F3:0.86,A2:0.80,A#2:1.00",
                guitar_analysis_pitch_classes="C#,F,A,A#",
                guitar_analysis_cells="C#3:0.03,F3:0.77,A2:0.43,A#2:1.00",
                guitar_smoothed_pitch_classes="F,A,A#",
                guitar_smoothed_cells="F3:0.77,A2:0.43,A#2:1.00",
                raw_pitch_class_levels=(
                    "C:0.010,C#:0.002,D:0.024,D#:0.016,E:0.013,F:0.838,"
                    "F#:0.004,G:0.025,G#:0.018,A:0.024,A#:1.000,B:0.022"
                ),
                guitar_probe_pitch_class_levels=(
                    "C:0.155,C#:0.025,D:0.033,D#:0.034,E:0.484,F:0.858,"
                    "F#:0.361,G:0.056,G#:0.336,A:0.795,A#:1.000,B:0.667"
                ),
            ),
            row(
                recording_id="extension_rescue",
                audio_path="extension_rescue.wav",
                expected_chords="Cmaj7",
                expected_chord_qualities="maj7",
                guitar_chord="C=Cmaj7",
                guitar_raw_chord="C=Cmaj7",
                guitar_smoothed_chord="C=Cmaj7",
            ),
            row(
                recording_id="extension_protected",
                audio_path="extension_protected.wav",
                expected_chords="C",
                expected_chord_qualities="maj",
                guitar_chord="C=Cmaj7",
                guitar_raw_chord="C=Cmaj7",
                guitar_smoothed_chord="C=Cmaj7",
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
        assert "guitar_chord: primary=2/7 later=4 miss=1" in output
        assert "guitar_raw_chord: primary=3/7 later=3 miss=1" in output
        assert "guitar_smoothed_chord: primary=3/7 later=3 miss=1" in output
        assert (
            "candidate primary relationships: display0_raw0_smooth0=3 "
            "display0_raw0_smooth1=1 "
            "display0_raw1_smooth0=1 display1_raw1_smooth1=2"
        ) in output
        assert "candidate primary rescues: raw=1 smoothed=1 both=0" in output
        assert "raw primary rescue examples" in output
        assert (
            "expected=Am display=C raw=Am smoothed=C score=r:5.640/s:5.515 "
            "conf=d:0.20/r:0.80/s:0.30 "
            "later_am.wav"
        ) in output
        assert (
            "same_root_extension_primary_probe: candidates=3 rescues=1 "
            "protected_false=1 neutral=1"
        ) in output
        assert (
            "rescue promote=Cmaj7 expected=Cmaj7 primary=C label=C=Cmaj7 "
            "extension_rescue.wav"
        ) in output
        assert (
            "protected_false promote=Cmaj7 expected=C primary=C label=C=Cmaj7 "
            "extension_protected.wav"
        ) in output
        assert (
            "same_root_quality_raw_probe_promote: candidates=1 rescues=1 protected_false=0"
            in output
        )
        assert (
            "same_root_quality_display_probe_promote: candidates=1 rescues=1 protected_false=0"
            in output
        )
        assert "rescue promote=A# expected=A# display=A#m raw=A#m smoothed=A#" in output
        assert "raw-only primary examples" in output
        assert "smoothed-only primary examples" in output
        assert (
            "guitar_primary_order: rows=7 primary_misses=4 expected_later=4 "
            "score_promotable=1 cpp_promotable=0"
        ) in output
        assert "gap=0.125 expected=Am primary=C" in output
        assert "invalid_power_minor" not in output
    print("test_analyze_guitar_primary_order: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
