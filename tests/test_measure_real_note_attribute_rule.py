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
        rows = [
            [
                "sample_id",
                "status",
                "family",
                "source",
                "first_row",
                "debug_owner",
                "debug_midi",
                "partial2",
                "partial3",
                "noise",
            ],
            ["keyboard_1", "hit", "piano", "electronic", "guitar", "guitar", "64", "0.58", "0.32", "0.01"],
            ["keyboard_2", "hit", "piano", "electronic", "piano", "piano", "64", "0.10", "0.02", "0.01"],
            ["guitar_1", "hit", "guitar", "electronic", "guitar", "guitar", "60", "0.39", "0.05", "0.03"],
            ["guitar_2", "hit", "guitar", "acoustic", "guitar", "guitar", "63", "0.27", "0.01", "0.02"],
        ]
        path.write_text("\n".join("\t".join(row) for row in rows) + "\n")

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "measure_real_note_attribute_rule.py"),
                str(path),
                "--condition",
                "debug_owner=guitar",
                "--condition",
                "debug_midi:52:64",
                "--condition",
                "partial3>=0.18",
                "--condition",
                "noise<=0.02",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "matched rows=1 samples=1" in result.stdout
    assert "examples keyboard_1" in result.stdout
    assert "piano/electronic/guitar rows=1 samples=1" in result.stdout
    assert "guitar/electronic/guitar" not in result.stdout
    print("test_measure_real_note_attribute_rule: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
