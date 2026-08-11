#!/usr/bin/env python3

from __future__ import annotations

import csv
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_good_sounds_bass_misses.py"
HEADER = [
    "status",
    "detected_expected_row",
    "sample_id",
    "family",
    "expected_note",
    "expected_midi",
    "buffer",
    "first_row",
    "debug_midi",
    "debug_owner",
    "raw_expected_ratio",
]


def row(**values: str) -> dict[str, str]:
    result = {field: "" for field in HEADER}
    result.update(values)
    return result


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, delimiter="\t")
            writer.writeheader()
            writer.writerows(
                [
                    row(status="hit", detected_expected_row="1", sample_id="bass_hit", family="bass", expected_note="E2", expected_midi="40", buffer="0", first_row="bass", debug_midi="40", debug_owner="bass", raw_expected_ratio="0.9"),
                    row(status="ownership_miss", detected_expected_row="0", sample_id="bass_low", family="bass", expected_note="A2", expected_midi="45", buffer="0", first_row="piano", debug_midi="45", debug_owner="piano", raw_expected_ratio="0.4"),
                    row(status="ownership_miss", detected_expected_row="0", sample_id="bass_upper", family="bass", expected_note="E4", expected_midi="64", buffer="0", first_row="other", debug_midi="64", debug_owner="other", raw_expected_ratio="0.7"),
                    row(status="ownership_miss", detected_expected_row="0", sample_id="bass_above", family="bass", expected_note="F4", expected_midi="65", buffer="0", first_row="guitar", debug_midi="65", debug_owner="guitar", raw_expected_ratio="0.8"),
                    row(status="hit", detected_expected_row="1", sample_id="other_hit", family="other", expected_note="C4", expected_midi="60", buffer="0", first_row="other", debug_midi="60", debug_owner="other", raw_expected_ratio="0.9"),
                ]
            )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    output = result.stdout
    assert "Good Sounds bass expected-row misses: 3/4 (75.0%)" in output, output
    assert "default range <= 52: 1/3 (33.3%)" in output, output
    assert "current upper-recovery 53-64: 1/3 (33.3%)" in output, output
    assert "above current recovery > 64: 1/3 (33.3%)" in output, output
    assert "bass_above\tF4 (65)\townership_miss" in output, output
    print("test_inspect_good_sounds_bass_misses: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
