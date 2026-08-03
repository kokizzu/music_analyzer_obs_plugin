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
                status="chord_hit",
                recording_id="protected_power_false",
                expected_chords="G",
                guitar_chord="Gpow=G",
                guitar_pitch_classes="G,D",
                guitar_analysis_pitch_classes="G,A#,D",
                guitar_smoothed_pitch_classes="G,D",
                raw_pitch_class_levels="G:1.000,A#:0.420,B:0.050,D:0.600",
                guitar_probe_pitch_class_levels="G:1.000,A#:0.420,B:0.050,D:0.600",
                guitar_melodic_probe_pitch_class_levels="G:1.000,A#:0.420,B:0.050,D:0.600",
            ),
            row(
                status="chord_miss",
                recording_id="visible_and_analysis",
                expected_chords="G",
                guitar_chord="Gpow",
                guitar_pitch_classes="G,D",
                guitar_analysis_pitch_classes="G,B,D",
                guitar_smoothed_pitch_classes="G,D",
                raw_pitch_class_levels="G:1.000,B:0.380,D:0.600",
                guitar_probe_pitch_class_levels="G:1.000,B:0.380,D:0.600",
                guitar_melodic_probe_pitch_class_levels="G:1.000,B:0.380,D:0.600",
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
                guitar_probe_pitch_class_levels="D:1.000,F#:0.100,A:0.650",
                guitar_melodic_probe_pitch_class_levels="D:1.000,F#:0.100,A:0.650",
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
                guitar_probe_pitch_class_levels="A:1.000,C#:0.050,E:0.700",
                guitar_melodic_probe_pitch_class_levels="A:1.000,C#:0.050,E:0.700",
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
                guitar_probe_pitch_class_levels="C:1.000,D#:0.420,G:0.900",
                guitar_melodic_probe_pitch_class_levels="C:1.000,D#:0.420,G:0.900",
            ),
            row(
                status="chord_miss",
                recording_id="source_primary_rescue",
                expected_chords="F#",
                guitar_chord="Gm=Gm7",
                guitar_raw_chord="F#=F#maj7=F#add9",
                guitar_smoothed_chord="F#=F#maj7=F#add9",
                guitar_pitch_classes="F#,G,A,A#",
                guitar_cells="F#3:1.00,G3:0.74,A2:0.38,A#3:0.39",
                guitar_analysis_pitch_classes="F#,G,A,A#",
                guitar_analysis_cells="F#3:1.00,G3:0.61,A2:0.32,A#3:0.35",
                guitar_smoothed_pitch_classes="F#,G,A,A#",
                raw_pitch_class_levels="F#:1.000,G:0.244,A:0.259,A#:0.495,C#:0.415",
                guitar_probe_pitch_class_levels="F#:1.000,G:0.737,A:0.385,A#:0.389,C#:0.299",
                guitar_melodic_probe_pitch_class_levels="F#:1.000,G:0.573,A:0.481,A#:0.512,C#:0.424",
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
        assert "guitar chord recovery rows=5" in output
        assert (
            "evidence classes analysis_full_tone_label_gap=2 "
            "raw_quality_gap=2 raw_exact_not_displayed=1"
            in output
        )
        assert "evidence sources raw=3 analysis=2" in output
        assert "guitar_pitch_classes root+fifth=3" in output
        assert "guitar_analysis_pitch_classes root+fifth=3" in output
        assert "guitar_smoothed_pitch_classes root+fifth=3" in output
        assert "visible+analysis root+fifth=2" in output
        assert "visible_and_analysis expected=G got=Gpow" in output
        assert "raw=1/0.38/0.6" in output
        combined_output = output.split("visible+analysis root+fifth=2", 1)[1]
        assert "minor_root_fifth expected=Cm got=C" in combined_output
        assert "wrong_fifth" not in combined_output
        assert "internal-probe same-root promotion simulation" in output
        assert "test-raw-profile same-root promotion simulation" in output
        assert "floor=max(anchor*0.020,0.005) recover=2 same_root_pow=1 protected_false=0" in output
        assert "labels<=5=2/0" in output
        assert "zero_false labels<=5 recover=2 mode=any_power" in output
        assert (
            "bounded visible_and_analysis labels=1 expected=G got=Gpow raw=1/0.38/0.6"
            in output
        )
        assert (
            "protected protected_power_false expected=G got=Gpow=G promoted=Gm"
            not in output
        )
        assert "ranked same-root promotion opportunities" in output
        ranked = output.split("ranked same-root promotion opportunities", 1)[1]
        assert "best_zero_false" in ranked
        assert "recover=2 same_root_pow=1" in ranked
        assert "labels<=5" in ranked
        assert "protected_false=0" in ranked
        assert "ranked source-primary rescue opportunities" in output
        source_ranked = output.split("ranked source-primary rescue opportunities", 1)[1]
        assert "best_zero_false raw-chord-primary" in source_ranked
        assert "recover=1" in source_ranked
        assert (
            "source_primary_rescue expected=F# got=Gm=Gm7 rescued=F# raw=1/0.495/0.415"
            in source_ranked
        )
        limited = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--examples", "2", "--limit", "1"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert "internal-probe same-root promotion simulation" in limited.stdout
        assert limited.stdout.count("    visible_and_analysis expected=G got=Gpow") == 18
        assert limited.stdout.count("      bounded visible_and_analysis labels=1") == 18
        assert "ranked source-primary rescue opportunities" in limited.stdout
    print("test_analyze_guitar_chord_recovery: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
