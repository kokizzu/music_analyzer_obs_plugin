#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_real_note_misses.py"


def run_log(text: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "misses.err"
        path.write_text(text)
        return subprocess.check_output([sys.executable, str(SCRIPT), str(path)], text=True)


def test_summarizes_full_mix_offsets_and_sources() -> None:
    output = run_log(
        "\n".join(
            [
                "  buffer 0 expected=D6 row_label=-- row_conf=0 row_grid=no any_grid=no amb=D#6:1.00 bass=--[--] keys=--[--] guitar=--[--] vocal=--[--] other=--[--]",
                "guitar_acoustic_010-086-075 guitar/acoustic D6: expected detected note, got label `--`",
                "  buffer 0 expected=C#5 row_label=-- row_conf=0 row_grid=no any_grid=no amb=G4:0.37,G#6:1.00 bass=--[--] keys=--[--] guitar=--[--] vocal=--[--] other=--[--]",
                "guitar_electronic_022-073-127 guitar/electronic C#5: expected detected note, got label `--`",
            ]
        )
    )
    if "misses 2" not in output:
        raise AssertionError(output)
    if "guitar/acoustic=1" not in output or "guitar/electronic=1" not in output:
        raise AssertionError(output)
    if "D6->D#6=1" not in output or "C#5->G#6=1" not in output:
        raise AssertionError(output)
    if "+1=1" not in output or "-5=1" not in output:
        raise AssertionError(output)


def test_counts_expected_pitch_seen_in_any_grid() -> None:
    output = run_log(
        "  buffer 0 expected=A5 row_label=-- row_conf=0 row_grid=no any_grid=no "
        "amb=C#7:0.31,A5:0.52 bass=--[--] keys=--[--] guitar=--[--] vocal=--[--] other=--[--]\n"
        "guitar_electronic_022-081-050 guitar/electronic A5: expected detected note, got label `--`\n"
    )
    if "expected present in verbose grids 1/1" not in output:
        raise AssertionError(output)


if __name__ == "__main__":
    test_summarizes_full_mix_offsets_and_sources()
    test_counts_expected_pitch_seen_in_any_grid()
    print("test_analyze_real_note_misses: ok")
