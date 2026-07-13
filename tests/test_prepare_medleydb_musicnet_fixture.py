#!/usr/bin/env python3
import contextlib
import csv
import os
import tempfile
import wave
from pathlib import Path

import generate_medleydb_fixture
import prepare_medleydb_musicnet_fixture


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
    if generate_medleydb_fixture.main(["generate_medleydb_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_prepare(root, output, required_tracks=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_MEDLEYDB_ROOT": str(root / "MedleyDB"),
            "MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT": str(root / "Annotations"),
            "MEDLEYDB_PATH": None,
            "MEDLEYDB_ANNOTATIONS_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_MEDLEYDB_REQUIRED_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_MEDLEYDB_REQUIRED_MELODY_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_MEDLEYDB_PREPARE_TRACKS": str(required_tracks),
        }
    ):
        return prepare_medleydb_musicnet_fixture.main(
            ["prepare_medleydb_musicnet_fixture.py", str(output)]
        )


def wav_peak(path):
    with wave.open(str(path), "rb") as audio:
        data = audio.readframes(audio.getnframes())
        width = audio.getsampwidth()
        if width != 2:
            raise AssertionError("expected 16-bit fixture WAV")
        peak = 0
        for offset in range(0, len(data), width):
            value = int.from_bytes(data[offset : offset + width], "little", signed=True)
            peak = max(peak, abs(value))
        return peak / 32768.0


def test_prepare_medleydb_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "medleydb"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("MedleyDB-to-MusicNet preparation failed")

        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("prepared layout should contain 20 WAV/CSV pairs")
        if wav_peak(wavs[0]) < 0.05:
            raise AssertionError("prepared audio should contain summed stem signal")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 4:
            raise AssertionError("prepared label file should contain melody-F0 note rows")
        if len({row["note"] for row in rows}) < 3:
            raise AssertionError("prepared labels should preserve melody pitch changes")


def test_prepare_medleydb_fixture_requires_melody_annotations():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "medleydb"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        (root / "Annotations" / "Artist_Song01_MELODY1.csv").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when selected melody F0 is missing")


def main():
    test_prepare_medleydb_fixture_writes_musicnet_shape()
    test_prepare_medleydb_fixture_requires_melody_annotations()
    print("test_prepare_medleydb_musicnet_fixture: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
