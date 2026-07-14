#!/usr/bin/env python3
import contextlib
import csv
import os
import tempfile
import wave
from pathlib import Path

import generate_synthsod_fixture
import prepare_synthsod_musicnet_fixture


@contextlib.contextmanager
def patched_env(values):
    previous = {}
    missing = object()
    for key, value in values.items():
        previous[key] = os.environ.get(key, missing)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def write_fixture(root):
    if generate_synthsod_fixture.main(["generate_synthsod_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_prepare(root, output, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_SYNTHSOD_ROOT": str(root / "SynthSOD-data"),
            "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT": str(root / "SynthSOD-aligned-scores"),
            "SYNTHSOD_PATH": None,
            "SYNTHSOD_SCORES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SYNTHSOD_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_SYNTHSOD_PREPARE_PIECES": str(required_pieces),
        }
    ):
        return prepare_synthsod_musicnet_fixture.main(["prepare_synthsod_musicnet_fixture.py", str(output)])


def wav_peak(path):
    with wave.open(str(path), "rb") as audio:
        raw = audio.readframes(audio.getnframes())
    peak = 0
    for offset in range(0, len(raw), 2):
        value = int.from_bytes(raw[offset : offset + 2], "little", signed=True)
        peak = max(peak, abs(value))
    return peak


def test_prepare_synthsod_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("SynthSOD-to-MusicNet preparation failed")

        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("SynthSOD layout should contain 20 WAV/CSV pairs")
        if wav_peak(wavs[0]) <= 0:
            raise AssertionError("SynthSOD audio should contain summed source signal")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 16:
            raise AssertionError("SynthSOD label file should contain aligned score note rows")
        if len({row["instrument"] for row in rows}) < 4:
            raise AssertionError("SynthSOD labels should preserve source instrument IDs")
        if len({int(row["note"]) % 12 for row in rows}) < 3:
            raise AssertionError("SynthSOD labels should preserve chord pitch classes")


def test_prepare_synthsod_fixture_requires_sources():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        (root / "SynthSOD-data" / "SYNTHSOD_001" / "Close Mic" / "Violin_1.wav").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when a selected piece has missing source audio")


def main():
    test_prepare_synthsod_fixture_writes_musicnet_shape()
    test_prepare_synthsod_fixture_requires_sources()
    print("test_prepare_synthsod_musicnet_fixture: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
