#!/usr/bin/env python3

from __future__ import annotations

import csv
import io
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        columns = [
            "status",
            "family",
            "source",
            "first_row",
            "visual_first_row",
            "sample_id",
            "expected_note",
            "buffer",
            "row_label",
            "row_grid",
            "any_grid",
            "buffer_strongest_row",
            "buffer_visual_strongest_row",
            "debug_note",
            "debug_owner",
            "expected_midi",
            "debug_midi",
            "debug_conf",
            "bass_score",
            "keyboard_score",
            "guitar_score",
            "vocal_score",
            "other_score",
            "spectral_level",
            "pitch_confidence",
            "periodicity",
            "fit_error",
            "centroid",
            "slope",
            "noise",
            "partial1",
            "partial2",
            "partial3",
            "partial4",
            "partial5",
            "bass_level",
            "guitar_level",
            "piano_level",
            "vocal_level",
            "other_level",
            "amb_level",
            "bass_visual_level",
            "guitar_visual_level",
            "piano_visual_level",
            "vocal_visual_level",
            "other_visual_level",
            "amb_visual_level",
            "bass_notes",
            "guitar_notes",
            "piano_notes",
            "vocal_notes",
            "other_notes",
            "amb_notes",
            "bass_visual_notes",
            "guitar_visual_notes",
            "piano_visual_notes",
            "vocal_visual_notes",
            "other_visual_notes",
            "amb_visual_notes",
        ]
        keyboard_row = [
            "ownership_miss",
            "piano",
            "electronic",
            "guitar",
            "piano",
            "keyboard_1",
            "C4",
            "0",
            "--",
            "no",
            "yes",
            "guitar",
            "piano",
            "C4",
            "guitar",
            "60",
            "60",
            "0.75",
            "0.00",
            "0.10",
            "0.70",
            "0.00",
            "0.00",
            "1.00",
            "0.80",
            "0.74",
            "0.05",
            "0.20",
            "0.10",
            "0.02",
            "1.00",
            "0.60",
            "0.10",
            "0.05",
            "0.02",
            "0.00",
            "1.00",
            "0.60",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.35",
            "0.95",
            "0.00",
            "0.00",
            "0.00",
            "",
            "C4:1.00,C5:0.20",
            "C4:0.60,E4:0.20",
            "",
            "",
            "",
            "",
            "C4:1.00,C5:0.20",
            "C4:0.60,E4:0.20",
            "",
            "",
            "",
        ]
        reed_row = [
            "hit",
            "other",
            "acoustic",
            "other",
            "other",
            "reed_1",
            "A4",
            "0",
            "A4",
            "yes",
            "yes",
            "other",
            "other",
            "A4",
            "other",
            "69",
            "69",
            "0.85",
            "0.00",
            "0.00",
            "0.20",
            "0.00",
            "0.80",
            "1.00",
            "0.90",
            "0.80",
            "0.08",
            "0.21",
            "0.12",
            "0.01",
            "1.00",
            "0.30",
            "0.20",
            "0.04",
            "0.01",
            "0.00",
            "0.20",
            "0.00",
            "0.00",
            "0.80",
            "0.00",
            "0.00",
            "0.20",
            "0.00",
            "0.00",
            "0.80",
            "0.00",
            "",
            "",
            "",
            "",
            "A4:0.80,A5:0.20",
            "",
            "",
            "",
            "",
            "",
            "A4:0.80,A5:0.20",
            "",
        ]
        keyboard_visual_row = [
            "hit",
            "piano",
            "electronic",
            "piano",
            "piano",
            "keyboard_visual_1",
            "E4",
            "0",
            "E4",
            "yes",
            "yes",
            "guitar",
            "guitar",
            "E4",
            "guitar",
            "64",
            "64",
            "0.82",
            "0.00",
            "0.62",
            "0.78",
            "0.00",
            "0.00",
            "1.00",
            "0.82",
            "0.78",
            "0.04",
            "0.24",
            "0.08",
            "0.02",
            "1.00",
            "0.52",
            "0.22",
            "0.08",
            "0.03",
            "0.00",
            "0.90",
            "0.72",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.70",
            "1.00",
            "0.00",
            "0.00",
            "0.00",
            "",
            "E3:0.20,E4:0.90",
            "E4:0.72,G4:0.20",
            "",
            "",
            "",
            "",
            "E3:0.20,E4:0.90",
            "",
            "",
            "",
            "",
        ]
        other_octave_row = [
            "hit",
            "other",
            "acoustic",
            "other",
            "other",
            "other_octave_1",
            "A4",
            "0",
            "A4",
            "yes",
            "yes",
            "other",
            "other",
            "A5",
            "other",
            "69",
            "81",
            "0.83",
            "0.00",
            "0.00",
            "0.10",
            "0.00",
            "0.90",
            "1.00",
            "0.88",
            "0.82",
            "0.07",
            "0.22",
            "0.11",
            "0.02",
            "1.00",
            "0.34",
            "0.18",
            "0.05",
            "0.01",
            "0.00",
            "0.20",
            "0.00",
            "0.00",
            "0.80",
            "0.00",
            "0.00",
            "0.20",
            "0.00",
            "0.00",
            "0.80",
            "0.00",
            "",
            "",
            "",
            "",
            "A5:0.80",
            "",
            "",
            "",
            "",
            "",
            "A5:0.80",
            "",
        ]
        empty_debug_row = [
            "hit",
            "bass",
            "electric",
            "bass",
            "bass",
            "bass_empty_debug",
            "E2",
            "0",
            "E2",
            "yes",
            "yes",
            "bass",
            "bass",
            "",
            "",
            "40",
            "",
            "",
            "0.90",
            "0.05",
            "0.05",
            "0.00",
            "0.00",
            "1.00",
            "0.70",
            "0.80",
            "0.04",
            "0.10",
            "0.02",
            "0.01",
            "1.00",
            "0.50",
            "0.20",
            "0.05",
            "0.02",
            "1.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "1.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "E2:1.00",
            "",
            "",
            "",
            "",
            "",
            "E2:1.00",
            "",
            "",
            "",
            "",
            "",
        ]
        path.write_text(
            "\t".join(columns)
            + "\n"
            + "\t".join(keyboard_row)
            + "\n"
            + "\t".join(reed_row)
            + "\n"
            + "\t".join(keyboard_visual_row)
            + "\n"
            + "\t".join(other_octave_row)
            + "\n"
            + "\t".join(empty_debug_row)
            + "\n"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        targeted = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "hit:other/acoustic->other",
                "--sample-id",
                "keyboard_1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        sample_only = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--sample-id",
                "reed_1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        misses_only = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--misses-only",
                "--summary-only",
                "--examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        rows_alias = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--misses-only",
                "--summary-only",
                "--rows",
                "0",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        dumped = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--misses-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        empty_debug_default_dump = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--sample-id",
                "bass_empty_debug",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        empty_debug_included_dump = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--include-empty-debug",
                "--sample-id",
                "bass_empty_debug",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        family_filtered = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--family",
                "other",
                "--source",
                "acoustic",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        miss_reason_filtered = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--miss-reason",
                "ownership",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        row_filtered = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--summary-only",
                "--first-row",
                "other",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        row_confusion = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "row_confusion:piano/electronic->guitar",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        visual_row_confusion = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "visual_row_confusion:piano/electronic->guitar",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        visual_row_confusion_dump = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--bucket",
                "visual_row_confusion:piano/electronic->guitar",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        visual_row_confusion_auto = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket-status",
                "visual_row_confusion",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        octave_displacement = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "octave_displacement:other/acoustic->+12",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        octave_displacement_dump = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--dump-rows",
                "--bucket",
                "octave_displacement:other/acoustic->+12",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        octave_displacement_auto = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket-status",
                "octave_displacement",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        weak_expected = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "weak_expected_row:other/acoustic->lit_octave@4",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        weak_expected_auto = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket-status",
                "weak_expected_row",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        weak_visual_expected = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_real_note_attribute_buckets.py"),
                str(path),
                "--bucket",
                "weak_visual_expected_row:piano/electronic->absent@4",
                "--summary-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1" in result.stdout
    assert "hit:other/acoustic->other rows=2 samples=2" in result.stdout
    assert "row_confusion:piano/electronic->guitar" not in result.stdout
    assert "debug_score_state" in result.stdout
    assert "scored_owner=1" in result.stdout
    assert "debug_conf" in result.stdout
    assert "partial2" in result.stdout
    assert "hit:other/acoustic->other rows=2 samples=2" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in targeted.stdout
    assert "sample keyboard_1: status=ownership_miss source=piano/electronic" in targeted.stdout
    assert "scores(b/k/g/v/o)=0.000/0.100/0.700/0.000/0.000" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in sample_only.stdout
    assert "hit:other/acoustic->other rows=2 samples=2" not in sample_only.stdout
    assert "sample reed_1: status=hit source=other/acoustic" in sample_only.stdout
    assert "scores(b/k/g/v/o)=0.000/0.000/0.200/0.000/0.800" in sample_only.stdout
    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1 examples=keyboard_1" in misses_only.stdout
    assert "hit:other/acoustic->other" not in misses_only.stdout
    assert "debug_conf" not in misses_only.stdout
    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1 examples=" in rows_alias.stdout
    assert "examples=keyboard_1" not in rows_alias.stdout
    assert dumped.stdout.startswith("sample_id\tstatus\tfamily\t")
    assert "debug_score_state" in dumped.stdout.splitlines()[0]
    assert "debug_delta" in dumped.stdout.splitlines()[0]
    assert "miss_reason" in dumped.stdout.splitlines()[0]
    assert "expected_row_exact_level" in dumped.stdout.splitlines()[0]
    assert "expected_first_score_ratio" in dumped.stdout.splitlines()[0]
    assert "first_expected_score_margin" in dumped.stdout.splitlines()[0]
    assert "expected_strongest_pitch_level_ratio" in dumped.stdout.splitlines()[0]
    assert "expected_row_visual_exact_level" in dumped.stdout.splitlines()[0]
    assert "visual_strongest_row_pitch_level" in dumped.stdout.splitlines()[0]
    assert "expected_visual_strongest_pitch_level_ratio" in dumped.stdout.splitlines()[0]
    assert "expected_visual_pitch_row_count" in dumped.stdout.splitlines()[0]
    assert "expected_pitch_class" in dumped.stdout.splitlines()[0]
    assert "expected_octave" in dumped.stdout.splitlines()[0]
    assert "debug_pitch_class" in dumped.stdout.splitlines()[0]
    assert "debug_octave" in dumped.stdout.splitlines()[0]
    assert "bass_score" in dumped.stdout.splitlines()[0]
    assert "partial2" in dumped.stdout.splitlines()[0]
    assert "visual_first_row" in dumped.stdout.splitlines()[0]
    assert "buffer_visual_strongest_row" in dumped.stdout.splitlines()[0]
    assert "piano_visual_level" in dumped.stdout.splitlines()[0]
    assert "\nkeyboard_1\townership_miss\tpiano\telectronic\tC4" in dumped.stdout
    assert "bass_empty_debug" not in empty_debug_default_dump.stdout
    assert "\nbass_empty_debug\thit\tbass\telectric\tE2" in empty_debug_included_dump.stdout
    dumped_rows = list(csv.DictReader(io.StringIO(dumped.stdout), delimiter="\t"))
    assert len(dumped_rows) == 1
    keyboard_dump = dumped_rows[0]
    assert keyboard_dump["sample_id"] == "keyboard_1"
    assert keyboard_dump["first_row"] == "guitar"
    assert keyboard_dump["visual_first_row"] == "piano"
    assert keyboard_dump["debug_note"] == "C4"
    assert keyboard_dump["expected_pitch_class"] == "C"
    assert keyboard_dump["expected_pitch_class_index"] == "0"
    assert keyboard_dump["expected_octave"] == "4"
    assert keyboard_dump["debug_midi"] == "60"
    assert keyboard_dump["debug_pitch_class"] == "C"
    assert keyboard_dump["debug_pitch_class_index"] == "0"
    assert keyboard_dump["debug_octave"] == "4"
    assert keyboard_dump["debug_owner"] == "guitar"
    assert keyboard_dump["bass_score"] == "0.00"
    assert keyboard_dump["keyboard_score"] == "0.10"
    assert keyboard_dump["guitar_score"] == "0.70"
    assert keyboard_dump["spectral_level"] == "1.00"
    assert keyboard_dump["noise"] == "0.02"
    assert keyboard_dump["partial1"] == "1.00"
    assert keyboard_dump["partial2"] == "0.60"
    assert keyboard_dump["partial3"] == "0.10"
    assert keyboard_dump["partial4"] == "0.05"
    assert keyboard_dump["partial5"] == "0.02"
    assert keyboard_dump["debug_score_state"] == "scored_owner"
    assert keyboard_dump["debug_delta"] == "0"
    assert keyboard_dump["debug_abs_delta"] == "0"
    assert keyboard_dump["miss_reason"] == "ownership"
    assert keyboard_dump["expected_row_score"] == "0.100"
    assert keyboard_dump["first_row_score"] == "0.700"
    assert keyboard_dump["visual_first_row_score"] == "0.100"
    assert keyboard_dump["strongest_row_score"] == "0.700"
    assert keyboard_dump["visual_strongest_row_score"] == "0.100"
    assert keyboard_dump["expected_first_score_ratio"] == "0.143"
    assert keyboard_dump["expected_strongest_score_ratio"] == "0.143"
    assert keyboard_dump["expected_visual_first_score_ratio"] == "1.000"
    assert keyboard_dump["expected_visual_strongest_score_ratio"] == "1.000"
    assert keyboard_dump["first_expected_score_margin"] == "0.600"
    assert keyboard_dump["strongest_expected_score_margin"] == "0.600"
    assert keyboard_dump["visual_first_expected_score_margin"] == "0.000"
    assert keyboard_dump["visual_strongest_expected_score_margin"] == "0.000"
    assert keyboard_dump["expected_row_exact_level"] == "0.600"
    assert keyboard_dump["expected_row_pitch_level"] == "0.600"
    assert keyboard_dump["expected_row_pitch_delta"] == "0"
    assert keyboard_dump["strongest_row_exact_level"] == "1.000"
    assert keyboard_dump["strongest_row_pitch_level"] == "1.000"
    assert keyboard_dump["strongest_row_pitch_delta"] == "0"
    assert keyboard_dump["expected_strongest_pitch_level_ratio"] == "0.600"
    assert keyboard_dump["strongest_expected_pitch_level_margin"] == "0.400"
    assert keyboard_dump["expected_exact_row_count"] == "2"
    assert keyboard_dump["expected_pitch_row_count"] == "2"
    assert keyboard_dump["bass_level"] == "0.00"
    assert keyboard_dump["guitar_level"] == "1.00"
    assert keyboard_dump["piano_level"] == "0.60"
    assert keyboard_dump["piano_visual_level"] == "0.95"
    assert "reed_1" not in dumped.stdout
    assert "\nreed_1\thit\tother\tacoustic\tA4" in family_filtered.stdout
    assert "keyboard_1" not in family_filtered.stdout
    assert "\nkeyboard_1\townership_miss\tpiano\telectronic\tC4" in miss_reason_filtered.stdout
    assert "reed_1" not in miss_reason_filtered.stdout
    assert "hit:other/acoustic->other rows=2 samples=2" in row_filtered.stdout
    assert "ownership_miss:piano/electronic->guitar" not in row_filtered.stdout
    assert "row_confusion:piano/electronic->guitar rows=1 samples=1" in row_confusion.stdout
    assert "keyboard_visual_1" in row_confusion.stdout
    assert "ownership_miss:piano/electronic->guitar" not in row_confusion.stdout
    assert "visual_row_confusion:piano/electronic->guitar rows=1 samples=1" in visual_row_confusion.stdout
    assert "keyboard_visual_1" in visual_row_confusion.stdout
    assert "ownership_miss:piano/electronic->guitar" not in visual_row_confusion.stdout
    assert visual_row_confusion_dump.stdout.startswith("sample_id\tstatus\tfamily\t")
    assert "\nkeyboard_visual_1\thit\tpiano\telectronic\tE4" in visual_row_confusion_dump.stdout
    assert "keyboard_1" not in visual_row_confusion_dump.stdout
    assert "reed_1" not in visual_row_confusion_dump.stdout
    assert "visual_row_confusion:piano/electronic->guitar rows=1 samples=1" in visual_row_confusion_auto.stdout
    assert "ownership_miss:piano/electronic->guitar" not in visual_row_confusion_auto.stdout
    assert "octave_displacement:other/acoustic->+12 rows=1 samples=1" in octave_displacement.stdout
    assert octave_displacement_dump.stdout.startswith("sample_id\tstatus\tfamily\t")
    assert "debug_delta" in octave_displacement_dump.stdout.splitlines()[0]
    assert "\nother_octave_1\thit\tother\tacoustic\tA4" in octave_displacement_dump.stdout
    assert "\t12\t12\t" in octave_displacement_dump.stdout
    assert "reed_1" not in octave_displacement_dump.stdout
    assert "octave_displacement:other/acoustic->+12 rows=1 samples=1" in octave_displacement_auto.stdout
    assert "ownership_miss:piano/electronic->guitar" not in octave_displacement_auto.stdout
    assert "weak_expected_row:other/acoustic->lit_octave@4 rows=1 samples=1" in weak_expected.stdout
    assert "other_octave_1" in weak_expected.stdout
    assert "weak_expected_row:other/acoustic->lit_octave@4 rows=1 samples=1" in weak_expected_auto.stdout
    assert "weak_visual_expected_row:piano/electronic->absent@4 rows=1 samples=1" in weak_visual_expected.stdout
    assert "keyboard_visual_1" in weak_visual_expected.stdout
    print("test_inspect_real_note_attribute_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
