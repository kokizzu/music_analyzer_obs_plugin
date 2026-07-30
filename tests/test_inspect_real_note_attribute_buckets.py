#!/usr/bin/env python3

from __future__ import annotations

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

    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1" in result.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in result.stdout
    assert "row_confusion:piano/electronic->guitar" not in result.stdout
    assert "debug_score_state" in result.stdout
    assert "scored_owner=1" in result.stdout
    assert "debug_conf" in result.stdout
    assert "partial2" in result.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in targeted.stdout
    assert "sample keyboard_1: status=ownership_miss source=piano/electronic" in targeted.stdout
    assert "scores(b/k/g/v/o)=0.000/0.100/0.700/0.000/0.000" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in sample_only.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" not in sample_only.stdout
    assert "sample reed_1: status=hit source=other/acoustic" in sample_only.stdout
    assert "scores(b/k/g/v/o)=0.000/0.000/0.200/0.000/0.800" in sample_only.stdout
    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1 examples=keyboard_1" in misses_only.stdout
    assert "hit:other/acoustic->other" not in misses_only.stdout
    assert "debug_conf" not in misses_only.stdout
    assert dumped.stdout.startswith("sample_id\tstatus\tfamily\t")
    assert "debug_score_state" in dumped.stdout.splitlines()[0]
    assert "debug_delta" in dumped.stdout.splitlines()[0]
    assert "miss_reason" in dumped.stdout.splitlines()[0]
    assert "expected_row_exact_level" in dumped.stdout.splitlines()[0]
    assert "expected_row_visual_exact_level" in dumped.stdout.splitlines()[0]
    assert "visual_strongest_row_pitch_level" in dumped.stdout.splitlines()[0]
    assert "expected_visual_pitch_row_count" in dumped.stdout.splitlines()[0]
    assert "bass_score" in dumped.stdout.splitlines()[0]
    assert "partial2" in dumped.stdout.splitlines()[0]
    assert "visual_first_row" in dumped.stdout.splitlines()[0]
    assert "buffer_visual_strongest_row" in dumped.stdout.splitlines()[0]
    assert "piano_visual_level" in dumped.stdout.splitlines()[0]
    assert "\nkeyboard_1\townership_miss\tpiano\telectronic\tC4" in dumped.stdout
    assert "\tguitar\tpiano\tC4\tguitar\t" in dumped.stdout
    assert "\t0.00\t1.00\t0.60\t0.00\t0.00\t0.00\t0.00\t0.35\t0.95\t" in dumped.stdout
    assert "\tscored_owner\t0\t0\townership\t" in dumped.stdout
    assert "\townership\t0.600\t0.600\t0\t1.000\t1.000\t0\t2\t2\t" in dumped.stdout
    assert "\t0.02\t\t1.00\t0.60\t0.10\t0.05\t0.02\t" in dumped.stdout
    assert "reed_1" not in dumped.stdout
    assert "\nreed_1\thit\tother\tacoustic\tA4" in family_filtered.stdout
    assert "keyboard_1" not in family_filtered.stdout
    assert "\nkeyboard_1\townership_miss\tpiano\telectronic\tC4" in miss_reason_filtered.stdout
    assert "reed_1" not in miss_reason_filtered.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in row_filtered.stdout
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
    print("test_inspect_real_note_attribute_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
