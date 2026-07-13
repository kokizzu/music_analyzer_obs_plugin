#!/usr/bin/env python3
import contextlib
import csv
import os
import tempfile
import wave
from pathlib import Path

import generate_cocochorales_fixture
import prepare_cocochorales_musicnet_fixture


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
    if generate_cocochorales_fixture.main(["generate_cocochorales_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_prepare(root, output, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_COCOCHORALES_ROOT": str(root),
            "COCOCHORALES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_COCOCHORALES_PREPARE_PIECES": str(required_pieces),
        }
    ):
        return prepare_cocochorales_musicnet_fixture.main(
            ["prepare_cocochorales_musicnet_fixture.py", str(output)]
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


def silence_wav(path):
    with wave.open(str(path), "rb") as audio:
        params = audio.getparams()
    frame_bytes = params.nchannels * params.sampwidth
    with wave.open(str(path), "wb") as audio:
        audio.setparams(params)
        audio.writeframes(b"\0" * params.nframes * frame_bytes)


def test_prepare_cocochorales_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "cocochorales"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("CocoChorales-to-MusicNet preparation failed")
        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("prepared layout should contain 20 WAV/CSV pairs")
        if wav_peak(wavs[0]) < 0.05:
            raise AssertionError("prepared audio should contain summed stem signal")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 12:
            raise AssertionError("prepared label file should contain score MIDI note rows")
        instruments = {row["instrument"] for row in rows}
        notes = {row["note"] for row in rows}
        if len(instruments) < 4 or len(notes) < 3:
            raise AssertionError("prepared labels should preserve multiple parts and notes")


def test_prepare_cocochorales_fixture_sums_stems_not_mix():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "cocochorales"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        for mix_path in root.glob("train/*/mixture.wav"):
            silence_wav(mix_path)

        if run_prepare(root, output) != 0:
            raise AssertionError("CocoChorales-to-MusicNet preparation failed")

        wavs = sorted((output / "train_data").glob("*.wav"))
        if len(wavs) != 20:
            raise AssertionError("prepared layout should contain 20 WAV files")
        if wav_peak(wavs[0]) < 0.05:
            raise AssertionError("prepared audio should keep summed stem signal when source mix is silent")


def test_prepare_cocochorales_fixture_requires_score_midi():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "cocochorales"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        (root / "train" / "cocochorales_fixture_00001" / "score.mid").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when a selected piece has no score MIDI")


def main():
    test_prepare_cocochorales_fixture_writes_musicnet_shape()
    test_prepare_cocochorales_fixture_sums_stems_not_mix()
    test_prepare_cocochorales_fixture_requires_score_midi()
    print("test_prepare_cocochorales_musicnet_fixture: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
