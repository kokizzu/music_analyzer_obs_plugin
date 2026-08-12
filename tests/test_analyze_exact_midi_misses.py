#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_exact_midi_misses.py"


def test_reports_sample_level_octave_misses() -> None:
    header = "\t".join(("sample_id", "family", "source", "expected_note", "expected_midi", "bass_notes", "other_notes", "raw_local_best_midi", "raw_expected_rank", "raw_expected_ratio"))
    rows = [
        "\t".join(("flute-a", "other", "flute", "C4", "60", "", "C5:0.8", "72", "2", "0.12")),
        "\t".join(("flute-a", "other", "flute", "C4", "60", "", "C3:0.4", "72", "2", "0.12")),
        "\t".join(("bass-a", "bass", "electric", "E2", "40", "E2:0.9", "", "40", "1", "1")),
        "\t".join(("bass-b", "bass", "electric", "A2", "45", "A1:0.7", "", "57", "3", "0.08")),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        path.write_text("\n".join((header, *rows, "")))
        output = subprocess.check_output([sys.executable, str(SCRIPT), str(path)], text=True)
    assert "exact-midi misses 2" in output
    assert "by family other=1 bass=1" in output
    assert "expected-row same-pitch-class MIDI offset +12=1 -12=1" in output
    assert "raw local-best MIDI offset +12=2" in output
    assert "flute-a expected=C4/60" in output
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        path.write_text("\n".join((header, *rows, "")))
        filtered = subprocess.check_output(
            [sys.executable, str(SCRIPT), str(path), "--same-pc-offset", "-12"], text=True
        )
    assert "traits bass-b expected=A2/45" in filtered
    assert "traits flute-a" not in filtered


if __name__ == "__main__":
    test_reports_sample_level_octave_misses()
    print("test_analyze_exact_midi_misses: ok")
