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


def run_logs(*texts: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for index, text in enumerate(texts):
            path = pathlib.Path(tmp) / f"misses-{index}.err"
            path.write_text(text)
            paths.append(path)
        return subprocess.check_output(
            [sys.executable, str(SCRIPT), *(str(path) for path in paths)],
            text=True,
        )


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
    if "examples guitar/electronic: guitar_electronic_022-081-050 A5" not in output:
        raise AssertionError(output)


def test_aggregates_multiple_shard_logs() -> None:
    output = run_logs(
        "\n".join(
            [
                "  buffer 0 expected=E4 row_label=-- row_conf=0 row_grid=no any_grid=no amb=F4:0.33 bass=--[--] keys=--[--] guitar=--[--] vocal=--[--] other=--[--]",
                "piano_acoustic_001-064-100 piano/acoustic E4: expected detected note, got label `--`",
            ]
        ),
        "\n".join(
            [
                "  buffer 0 expected=A3 row_label=-- row_conf=0 row_grid=no any_grid=yes amb=-- bass=--[--] keys=--[--] guitar=A3[ A3:0.70] vocal=--[--] other=--[--] own=A3:guitar/conf=0.70/bkvo=0,0,0.7,0,0/spec=1/pitch=0.8/per=0.7/harm=0.4/fit=0.1/cent=0.2/slope=0.1/noise=0.2/partials=1,0.3,0.1,0.02,0.01",
                "piano_electronic_002-057-100 piano/electronic A3: expected-row ownership missing first-row=guitar row-label=`--`",
            ]
        ),
    )
    if "misses 1" not in output:
        raise AssertionError(output)
    if "piano/acoustic=1" not in output:
        raise AssertionError(output)
    if "E4->F4=1" not in output:
        raise AssertionError(output)
    if "ownership misses 1" not in output:
        raise AssertionError(output)
    if "ownership by source piano/electronic=1" not in output:
        raise AssertionError(output)
    if "ownership first rows guitar=1" not in output:
        raise AssertionError(output)
    if "ownership expected owner candidates guitar=1" not in output:
        raise AssertionError(output)
    if "ownership expected source owner candidates piano/electronic->guitar=1" not in output:
        raise AssertionError(output)
    if "ownership expected owner paths guitar=1" not in output:
        raise AssertionError(output)


def test_summarizes_full_mix_ownership_misses() -> None:
    output = run_log(
        "\n".join(
            [
                "  buffer 0 expected=E4 row_label=-- row_conf=0 row_grid=no any_grid=yes amb=-- bass=--[--] keys=--[--] guitar=E4[ E4:0.74] vocal=--[--] other=--[--]",
                "piano_acoustic_001-064-100 piano/acoustic E4: expected-row ownership missing first-row=guitar row-label=`--`",
                "  buffer 0 expected=A3 row_label=-- row_conf=0 row_grid=no any_grid=yes amb=A3:0.65 bass=--[--] keys=--[--] guitar=--[--] vocal=--[--] other=--[--]",
                "other_flute_001-057-100 other/flute A3: expected-row ownership missing first-row=amb row-label=`--`",
            ]
        )
    )
    if "misses 0" not in output:
        raise AssertionError(output)
    if "ownership misses 2" not in output:
        raise AssertionError(output)
    if "piano/acoustic=1" not in output or "other/flute=1" not in output:
        raise AssertionError(output)
    if "ownership first rows guitar=1 amb=1" not in output:
        raise AssertionError(output)
    if (
        "ownership expected source pitch rows piano/acoustic->guitar=1 other/flute->amb=1"
        not in output
    ):
        raise AssertionError(output)
    if "ownership expected pitch rows guitar=1 amb=1" not in output:
        raise AssertionError(output)
    if "ownership expected row paths guitar=1 amb=1" not in output:
        raise AssertionError(output)
    if "ownership source row paths piano/acoustic:guitar=1 other/flute:amb=1" not in output:
        raise AssertionError(output)
    if "piano/acoustic->guitar=1" not in output or "other/flute->amb=1" not in output:
        raise AssertionError(output)
    if "E4->E4=1" not in output or "A3->A3=1" not in output:
        raise AssertionError(output)
    if "ownership expected present in verbose grids 2/2" not in output:
        raise AssertionError(output)
    if "ownership examples piano/acoustic->guitar: piano_acoustic_001-064-100 E4" not in output:
        raise AssertionError(output)
    if "other/flute->amb: other_flute_001-057-100 A3" not in output:
        raise AssertionError(output)


if __name__ == "__main__":
    test_summarizes_full_mix_offsets_and_sources()
    test_counts_expected_pitch_seen_in_any_grid()
    test_aggregates_multiple_shard_logs()
    test_summarizes_full_mix_ownership_misses()
    print("test_analyze_real_note_misses: ok")
