#!/usr/bin/env python3
import contextlib
import csv
import os
import struct
import tempfile
import wave
from pathlib import Path

import generate_polyvocal_fixture
import prepare_polyvocal_musicnet_fixture


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
    if generate_polyvocal_fixture.main(["generate_polyvocal_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_prepare(root, output, required_pieces=20, require_source_audio=False):
    with patched_env(
        {
            "MUSIC_ANALYZER_POLYVOCAL_ROOT": str(root),
            "POLYVOCAL_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_POLYVOCAL_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_POLYVOCAL_PREPARE_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO": "1" if require_source_audio else None,
        }
    ):
        return prepare_polyvocal_musicnet_fixture.main(
            ["prepare_polyvocal_musicnet_fixture.py", str(output)]
        )


def overwrite_wav_with_silence(path):
    with wave.open(str(path), "rb") as audio:
        channels = audio.getnchannels()
        width = audio.getsampwidth()
        sample_rate = audio.getframerate()
        frames = audio.getnframes()
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(width)
        audio.setframerate(sample_rate)
        audio.writeframes(b"\0" * frames * channels * width)


def wav_peak(path):
    with wave.open(str(path), "rb") as audio:
        raw = audio.readframes(audio.getnframes())
    values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    return max((abs(value) for value in values), default=0)


def test_prepare_polyvocal_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("PolyVocal-to-MusicNet preparation failed")
        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("prepared layout should contain 20 WAV/CSV pairs")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 12:
            raise AssertionError("prepared label file should contain F0-derived note rows")
        instruments = {row["instrument"] for row in rows}
        notes = {row["note"] for row in rows}
        if len(instruments) < 4 or len(notes) < 4:
            raise AssertionError("prepared labels should preserve multiple voices and note classes")


def test_prepare_polyvocal_fixture_requires_f0_annotations():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        (root / "annotations" / "PV001_soprano.csv").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when a selected mix has missing F0 annotations")


def test_prepare_polyvocal_fixture_sums_source_audio_when_available():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        overwrite_wav_with_silence(root / "audiomixtures" / "PV001_satb.wav")
        if run_prepare(root, output, required_pieces=1, require_source_audio=True) != 0:
            raise AssertionError("PolyVocal source-audio preparation failed")
        if wav_peak(output / "train_data" / "1.wav") <= 0:
            raise AssertionError("prepared audio should come from summed source voices, not silent mix audio")


def test_points_to_notes_splits_gaps_and_notes():
    points = [(0.00, 261.625565), (0.05, 261.625565), (0.10, 261.625565), (0.40, 329.627557), (0.45, 329.627557)]
    notes = prepare_polyvocal_musicnet_fixture.points_to_notes(points, 97)
    if [(round(start, 2), round(end, 2), midi) for start, end, _, midi in notes] != [
        (0.00, 0.15, 60),
        (0.40, 0.50, 64),
    ]:
        raise AssertionError(f"unexpected note segmentation: {notes}")


def main():
    test_prepare_polyvocal_fixture_writes_musicnet_shape()
    test_prepare_polyvocal_fixture_requires_f0_annotations()
    test_prepare_polyvocal_fixture_sums_source_audio_when_available()
    test_points_to_notes_splits_gaps_and_notes()
    print("test_prepare_polyvocal_musicnet_fixture: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
