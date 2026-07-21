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
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "bass_label",
    "piano_label",
    "guitar_label",
    "vocal_label",
    "other_label",
    "global_chord",
    "keyboard_chord",
    "guitar_chord",
    "other_chord",
    "rms",
    "low",
    "mid",
    "high",
    "drum_expected",
    "drum_active",
    "drum_level",
    "drum_active_list",
    "kick_level",
    "snare_level",
    "hihat_level",
    "crash_level",
    "tom_level",
    "ride_level",
    "rim_level",
    "kick_trigger",
    "snare_trigger",
    "hihat_trigger",
    "crash_trigger",
    "tom_trigger",
    "ride_trigger",
    "rim_trigger",
    "kick_threshold",
    "snare_threshold",
    "hihat_threshold",
    "crash_threshold",
    "tom_threshold",
    "ride_threshold",
    "rim_threshold",
    "transient",
    "onset",
    "kick_body",
    "snare_body",
    "tom_body",
    "snare_crack",
    "upper_tom",
    "body_shape",
]


def row(**overrides: str) -> list[str]:
    values = {name: "" for name in HEADER}
    values.update(
        {
            "program": "1",
            "program_name": "Test Program",
            "note": "C4",
            "midi": "60",
            "path": "sample.wav",
            "window_ms": "100",
            "detected_expected_row": "1",
            "detected_anywhere": "1",
            "expected_level": "1.0",
            "bass_level": "0.0",
            "piano_level": "1.0",
            "guitar_level": "0.0",
            "vocal_level": "0.0",
            "other_level": "0.0",
            "amb_level": "0.0",
            "bass_label": "--",
            "piano_label": "C4",
            "guitar_label": "--",
            "vocal_label": "--",
            "other_label": "--",
            "global_chord": "--",
            "keyboard_chord": "--",
            "guitar_chord": "--",
            "other_chord": "--",
            "rms": "0.1",
            "low": "0.2",
            "mid": "0.7",
            "high": "0.1",
            "drum_active_list": "--",
            "kick_level": "0.0",
            "snare_level": "0.0",
            "hihat_level": "0.0",
            "crash_level": "0.0",
            "tom_level": "0.0",
            "ride_level": "0.0",
            "rim_level": "0.0",
            "kick_trigger": "0.0",
            "snare_trigger": "0.0",
            "hihat_trigger": "0.0",
            "crash_trigger": "0.0",
            "tom_trigger": "0.0",
            "ride_trigger": "0.0",
            "rim_trigger": "0.0",
            "transient": "1.0",
            "onset": "2.0",
        }
    )
    values.update(overrides)
    return [values[name] for name in HEADER]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "attributes.tsv"
        rows = [
            row(kind="note", status="hit", family="piano", expected_family="piano"),
            row(
                kind="note",
                status="ownership_miss",
                family="guitar",
                expected_family="guitar",
                detected_expected_row="0",
                expected_level="0.0",
                piano_level="0.0",
                other_level="1.0",
                piano_label="--",
                other_label="C4",
            ),
            row(
                kind="drum",
                status="miss",
                family="drum",
                expected_family="snare",
                drum_expected="snare",
                drum_active="0",
                drum_level="0.2",
                drum_active_list="kick",
                kick_level="0.8",
                snare_level="0.2",
            ),
        ]
        path.write_text("\t".join(HEADER) + "\n" + "\n".join("\t".join(item) for item in rows) + "\n")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "summarize_instrument_sample_attributes.py"),
                str(path),
                "--top",
                "4",
                "--examples",
                "3",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        output = result.stdout
        assert "rows 3" in output
        assert "note status guitar:ownership_miss=1 piano:hit=1" in output
        assert "note ownership_miss:guitar count 1" in output
        assert "drum miss:snare count 1" in output
    print("test_summarize_instrument_sample_attributes: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
