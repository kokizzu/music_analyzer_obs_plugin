#!/usr/bin/env python3
import contextlib
import csv
import os
import struct
import tempfile
import wave
from pathlib import Path

import generate_slakh_fixture
import prepare_slakh_musicnet_fixture


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
    if generate_slakh_fixture.main(["generate_slakh_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def silence_wav(path):
    with wave.open(str(path), "rb") as audio:
        channels = audio.getnchannels()
        sample_width = audio.getsampwidth()
        sample_rate = audio.getframerate()
        frame_count = audio.getnframes()
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(sample_width)
        audio.setframerate(sample_rate)
        audio.writeframes(bytes(frame_count * channels * sample_width))


def wav_peak(path):
    with wave.open(str(path), "rb") as audio:
        if audio.getsampwidth() != 2:
            return 0.0
        data = audio.readframes(audio.getnframes())
    peak = 0.0
    for offset in range(0, len(data), 2):
        if offset + 2 > len(data):
            break
        peak = max(peak, abs(struct.unpack_from("<h", data, offset)[0]) / 32768.0)
    return peak


def run_prepare(root, output, required_tracks=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_SLAKH_ROOT": str(root),
            "SLAKH_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_SLAKH_PREPARE_TRACKS": str(required_tracks),
        }
    ):
        return prepare_slakh_musicnet_fixture.main(["prepare_slakh_musicnet_fixture.py", str(output)])


def test_prepare_slakh_fixture_writes_musicnet_shape():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "slakh"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        if run_prepare(root, output) != 0:
            raise AssertionError("Slakh-to-MusicNet preparation failed")
        wavs = sorted((output / "train_data").glob("*.wav"))
        labels = sorted((output / "train_labels").glob("*.csv"))
        if len(wavs) != 20 or len(labels) != 20:
            raise AssertionError("prepared layout should contain 20 WAV/CSV pairs")

        with open(labels[0], newline="", encoding="utf-8") as label_file:
            rows = list(csv.DictReader(label_file))
        if len(rows) < 12:
            raise AssertionError("prepared label file should contain MIDI note rows")
        instruments = {row["instrument"] for row in rows}
        notes = {row["note"] for row in rows}
        if len(instruments) < 3 or len(notes) < 3:
            raise AssertionError("prepared labels should preserve multiple instruments and notes")


def test_prepare_slakh_fixture_sums_stems_not_provided_mix():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "slakh"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        for mix in root.glob("*/*/mix.wav"):
            silence_wav(mix)
        if run_prepare(root, output) != 0:
            raise AssertionError("Slakh-to-MusicNet preparation failed with silent provided mixes")
        if wav_peak(output / "train_data" / "1.wav") < 0.05:
            raise AssertionError("prepared Slakh playback should be built from audible summed stems")


def test_prepare_slakh_fixture_requires_midi_notes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "slakh"
        output = Path(temp) / "musicnet"
        write_fixture(root)
        for midi in (root / "train" / "Track00001" / "MIDI").glob("*.mid"):
            midi.unlink()
        (root / "train" / "Track00001" / "all_src.mid").unlink()
        if run_prepare(root, output) == 0:
            raise AssertionError("preparation should fail when a selected track has no MIDI notes")


def main():
    test_prepare_slakh_fixture_writes_musicnet_shape()
    test_prepare_slakh_fixture_sums_stems_not_provided_mix()
    test_prepare_slakh_fixture_requires_midi_notes()
    print("test_prepare_slakh_musicnet_fixture: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
