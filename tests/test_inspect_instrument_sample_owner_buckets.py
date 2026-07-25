#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]

HEADER = [
    "kind",
    "status",
    "family",
    "expected_family",
    "program",
    "program_name",
    "note",
    "midi",
    "path",
    "window_ms",
    "detected_expected_row",
    "detected_anywhere",
    "display_note",
    "display_midi",
    "display_delta",
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_notes",
    "piano_notes",
    "guitar_notes",
    "vocal_notes",
    "other_notes",
    "amb_notes",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "raw_local_best_note",
    "debug_note",
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
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "debug_count",
    "debug_candidates",
]


def row(**overrides: str) -> list[str]:
    values = {field: "" for field in HEADER}
    values.update(
        {
            "kind": "note",
            "status": "hit",
            "program": "1",
            "program_name": "Program",
            "note": "C4",
            "midi": "60",
            "path": "sample.wav",
            "window_ms": "100",
            "detected_expected_row": "1",
            "detected_anywhere": "1",
            "display_note": "C4",
            "display_midi": "60",
            "display_delta": "0",
            "expected_level": "1.0",
            "bass_level": "0.0",
            "piano_level": "1.0",
            "guitar_level": "0.0",
            "vocal_level": "0.0",
            "other_level": "0.0",
            "amb_level": "0.0",
            "bass_notes": "",
            "piano_notes": "C4:1.00",
            "guitar_notes": "",
            "vocal_notes": "",
            "other_notes": "",
            "amb_notes": "",
            "raw_expected_ratio": "1.0",
            "raw_tuned_ratio": "1.0",
            "raw_tuned_abs_cent_offset": "0.0",
            "raw_expected_rank": "1",
            "raw_local_best_note": "C4",
            "debug_note": "C4",
            "debug_owner": "piano",
            "debug_conf": "0.8",
            "keyboard_score": "0.8",
            "guitar_score": "0.1",
            "vocal_score": "0.0",
            "other_score": "0.1",
            "spectral_level": "0.9",
            "pitch_confidence": "0.8",
            "periodicity": "0.7",
            "harmonicity": "0.6",
            "fit_error": "0.1",
            "centroid": "0.2",
            "slope": "0.3",
            "noise": "0.05",
            "partial2": "0.4",
            "partial3": "0.3",
            "partial4": "0.2",
            "partial5": "0.1",
            "debug_count": "1",
            "debug_candidates": "C4/piano/0.800/k0.800/g0.100/v0.000/o0.100",
        }
    )
    values.update(overrides)
    return [values[field] for field in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(family="piano", expected_family="piano", debug_owner="piano"),
            row(status="ownership_miss", family="guitar", expected_family="guitar", debug_owner="piano"),
            row(family="strings", expected_family="strings", debug_owner="other"),
            row(family="vocals", expected_family="vocals", debug_owner="vocals"),
            row(
                status="miss",
                family="synth",
                expected_family="synth",
                note="C2",
                midi="36",
                detected_expected_row="0",
                detected_anywhere="0",
                display_note="",
                display_midi="",
                display_delta="",
                raw_expected_rank="8",
                raw_tuned_abs_cent_offset="18",
                debug_note="",
                debug_owner="",
                debug_conf="",
                debug_count="2",
                debug_candidates="B2/amb/0.000/k0.000/g0.000/v0.000/o0.000,C#2/guitar/0.600/k0.000/g0.600/v0.000/o0.000",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_instrument_sample_owner_buckets.py"),
                str(path),
                "--top",
                "6",
                "--examples",
                "1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        output = result.stdout
        assert "note rows 5" in output
        assert "piano/owner_hit/piano=1" in output
        assert "guitar/owner_miss/piano=1" in output
        assert "owner_hit:strings->other rows=1" in output
        dumped = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_instrument_sample_owner_buckets.py"),
                str(path),
                "--dump-rows",
                "--misses-only",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert dumped.returncode == 0, dumped.stdout + dumped.stderr
        assert dumped.stdout.startswith("kind\tstatus\tfamily\t")
        header = dumped.stdout.splitlines()[0]
        assert "display_note" in header
        assert "piano_notes" in header
        assert "nearest_debug_note" in dumped.stdout.splitlines()[0]
        assert "miss_reason" in dumped.stdout.splitlines()[0]
        assert "\nnote\townership_miss\tguitar\tguitar\tProgram\tC4" in dumped.stdout
        assert "\tC4\t60\t0\t" in dumped.stdout
        assert "\tC4:1.00\t" in dumped.stdout
        assert "\townership\t" in dumped.stdout
        assert "\nnote\tmiss\tsynth\tsynth\tProgram\tC2" in dumped.stdout
        assert "\tweak_expected_rank\t" in dumped.stdout
        assert "\tnote\thit\tpiano\t" not in dumped.stdout
    print("test_inspect_instrument_sample_owner_buckets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
