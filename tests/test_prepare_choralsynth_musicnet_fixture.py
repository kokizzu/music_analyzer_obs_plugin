#!/usr/bin/env python3
import contextlib
import csv
import os
import tempfile
from pathlib import Path

import generate_choralsynth_fixture
import prepare_choralsynth_musicnet_fixture


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
    if generate_choralsynth_fixture.main(["generate_choralsynth_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_prepare(root, output, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_CHORALSYNTH_ROOT": str(root),
            "CHORALSYNTH_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_CHORALSYNTH_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_CHORALSYNTH_PREPARE_PIECES": str(required_pieces),
        }
    ):
        return prepare_choralsynth_musicnet_fixture.main(
            ["prepare_choralsynth_musicnet_fixture.py", str(output)]
        )


def test_prepare_choralsynth_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "choralsynth"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("ChoralSynth-to-MusicNet preparation failed")
        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("prepared layout should contain 20 WAV/CSV pairs")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 12:
            raise AssertionError("prepared label file should contain score MIDI note rows")
        instruments = {row["instrument"] for row in rows}
        notes = {row["note"] for row in rows}
        if len(instruments) < 4 or len(notes) < 3:
            raise AssertionError("prepared labels should preserve multiple voices and notes")


def test_prepare_choralsynth_fixture_requires_score_midi():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "choralsynth"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        (root / "01_Fixture_Chorale" / "score.midi").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when a selected piece has no score MIDI")


def main():
    test_prepare_choralsynth_fixture_writes_musicnet_shape()
    test_prepare_choralsynth_fixture_requires_score_midi()
    print("test_prepare_choralsynth_musicnet_fixture: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
