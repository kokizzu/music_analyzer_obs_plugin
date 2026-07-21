#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


HEADER = [
    "status",
    "detected",
    "detected_anywhere",
    "detected_expected_row",
    "first_row",
    "sample_id",
    "family",
    "nsynth_family",
    "source",
    "expected_note",
    "expected_midi",
    "buffer",
    "mode",
    "row_label",
    "row_conf",
    "row_grid",
    "any_grid",
    "buffer_strongest_row",
    "bass_level",
    "guitar_level",
    "piano_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "global_chord",
    "keyboard_chord",
    "guitar_chord",
    "other_chord",
    "rms",
    "low",
    "mid",
    "high",
    "kick",
    "snare",
    "hihat",
    "crash",
    "tom",
    "ride",
    "rim",
    "debug_note",
    "debug_midi",
    "debug_owner",
    "debug_conf",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
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


def row(**overrides: str) -> list[str]:
    values = {name: "" for name in HEADER}
    values.update(
        {
            "detected": "1",
            "detected_anywhere": "1",
            "detected_expected_row": "1",
            "mode": "full_mix",
            "row_conf": "1",
            "row_grid": "1",
            "any_grid": "1",
            "rms": "0.1",
            "low": "0.2",
            "mid": "0.3",
            "high": "0.4",
        }
    )
    values.update(overrides)
    return [values[name] for name in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(
                status="hit",
                first_row="piano",
                sample_id="keyboard_1",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="C4",
                expected_midi="60",
                buffer="0",
                debug_note="C4",
                debug_midi="60",
                debug_owner="piano",
                debug_conf="0.80",
                keyboard_score="0.70",
                guitar_score="0.10",
                vocal_score="0.02",
                other_score="0.05",
                pitch_confidence="0.90",
                periodicity="0.85",
                fit_error="0.05",
                noise="0.12",
                partial1="1.0",
                partial2="0.4",
                partial3="0.2",
                partial4="0.1",
            ),
            row(
                status="ownership_miss",
                detected_expected_row="0",
                first_row="guitar",
                sample_id="keyboard_2",
                family="piano",
                nsynth_family="keyboard",
                source="electronic",
                expected_note="E2",
                expected_midi="40",
                buffer="0",
                row_grid="0",
                debug_note="E2",
                debug_midi="40",
                debug_owner="guitar",
                debug_conf="0.56",
                keyboard_score="0.00",
                guitar_score="0.56",
                vocal_score="0.00",
                other_score="0.43",
                pitch_confidence="0.70",
                periodicity="0.71",
                fit_error="0.07",
                noise="0.54",
                partial1="1.0",
                partial2="0.54",
                partial3="0.13",
                partial4="0.17",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "summarize_real_note_attributes.py"), str(path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    assert "samples 2" in result.stdout
    assert "hit=1" in result.stdout
    assert "ownership_miss=1" in result.stdout
    assert "ownership_miss:piano/electronic->guitar=1" in result.stdout
    assert "debug medians ownership_miss:piano/electronic->guitar" in result.stdout
    print("test_summarize_real_note_attributes: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
