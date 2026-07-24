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
            "sample_id",
            "expected_note",
            "buffer",
            "row_label",
            "row_grid",
            "any_grid",
            "buffer_strongest_row",
            "debug_note",
            "debug_owner",
            "expected_midi",
            "debug_midi",
            "debug_conf",
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
        ]
        keyboard_row = [
            "ownership_miss",
            "piano",
            "electronic",
            "guitar",
            "keyboard_1",
            "C4",
            "0",
            "--",
            "no",
            "yes",
            "guitar",
            "C4",
            "guitar",
            "60",
            "60",
            "0.75",
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
        ]
        reed_row = [
            "hit",
            "other",
            "acoustic",
            "other",
            "reed_1",
            "A4",
            "0",
            "A4",
            "yes",
            "yes",
            "other",
            "A4",
            "other",
            "69",
            "69",
            "0.85",
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
        ]
        path.write_text("\t".join(columns) + "\n" + "\t".join(keyboard_row) + "\n" + "\t".join(reed_row) + "\n")

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

    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1" in result.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in result.stdout
    assert "debug_conf" in result.stdout
    assert "partial2" in result.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in targeted.stdout
    assert "sample keyboard_1: status=ownership_miss source=piano/electronic" in targeted.stdout
    assert "scores(b/k/g/v/o)=-/0.100/0.700/0.000/0.000" in targeted.stdout
    assert "ownership_miss:piano/electronic->guitar" not in sample_only.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" not in sample_only.stdout
    assert "sample reed_1: status=hit source=other/acoustic" in sample_only.stdout
    assert "scores(b/k/g/v/o)=-/0.000/0.200/0.000/0.800" in sample_only.stdout
    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1 examples=keyboard_1" in misses_only.stdout
    assert "hit:other/acoustic->other" not in misses_only.stdout
    assert "debug_conf" not in misses_only.stdout
    assert dumped.stdout.startswith("sample_id\tstatus\tfamily\t")
    assert "debug_delta" in dumped.stdout.splitlines()[0]
    assert "miss_reason" in dumped.stdout.splitlines()[0]
    assert "\nkeyboard_1\townership_miss\tpiano\telectronic\tC4" in dumped.stdout
    assert "\t0\t0\townership\t" in dumped.stdout
    assert "reed_1" not in dumped.stdout
    print("test_inspect_real_note_attribute_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
