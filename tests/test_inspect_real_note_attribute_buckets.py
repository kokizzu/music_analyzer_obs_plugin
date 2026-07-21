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
        path.write_text(
            "\t".join(
                [
                    "status",
                    "family",
                    "source",
                    "first_row",
                    "sample_id",
                    "debug_note",
                    "expected_midi",
                    "debug_midi",
                    "debug_conf",
                    "partial2",
                ]
            )
            + "\n"
            + "\t".join(
                [
                    "ownership_miss",
                    "piano",
                    "electronic",
                    "guitar",
                    "keyboard_1",
                    "C4",
                    "60",
                    "60",
                    "0.75",
                    "0.60",
                ]
            )
            + "\n"
            + "\t".join(
                [
                    "hit",
                    "other",
                    "acoustic",
                    "other",
                    "reed_1",
                    "A4",
                    "69",
                    "69",
                    "0.85",
                    "0.30",
                ]
            )
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

    assert "ownership_miss:piano/electronic->guitar rows=1 samples=1" in result.stdout
    assert "hit:other/acoustic->other rows=1 samples=1" in result.stdout
    assert "debug_conf" in result.stdout
    assert "partial2" in result.stdout
    print("test_inspect_real_note_attribute_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
