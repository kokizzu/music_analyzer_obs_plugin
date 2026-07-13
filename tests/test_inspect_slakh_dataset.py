#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import generate_slakh_fixture
import inspect_slakh_dataset


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


def run_with_env(root, required_tracks=20, min_audio_seconds=1.0):
    with patched_env(
        {
            "MUSIC_ANALYZER_SLAKH_ROOT": str(root),
            "SLAKH_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_SLAKH_MIN_AUDIO_SECONDS": str(min_audio_seconds),
            "MUSIC_ANALYZER_SLAKH_MIN_STEMS": "4",
            "MUSIC_ANALYZER_SLAKH_REQUIRED_CLASSES": "piano,bass,guitar,drum",
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_slakh_dataset.main()


def write_fixture(root):
    if generate_slakh_fixture.main(["generate_slakh_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def test_complete_slakh_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        if run_with_env(root) != 0:
            raise AssertionError("complete Slakh-shaped fixture should pass")


def test_missing_midi_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        (root / "train" / "Track00001" / "all_src.mid").unlink()
        for midi in (root / "train" / "Track00001" / "MIDI").glob("*.mid"):
            midi.unlink()
        if run_with_env(root) == 0:
            raise AssertionError("Slakh-shaped fixture with missing MIDI should fail")


def test_missing_required_class_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        metadata = root / "train" / "Track00001" / "metadata.yaml"
        metadata.write_text(metadata.read_text(encoding="utf-8").replace("Guitar", "Plucked"), encoding="utf-8")
        if run_with_env(root) == 0:
            raise AssertionError("Slakh-shaped fixture with missing guitar class should fail")


def test_too_short_audio_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        if run_with_env(root, min_audio_seconds=2.0) == 0:
            raise AssertionError("Slakh-shaped fixture with too-short audio should fail")


def main():
    test_complete_slakh_shape_passes()
    test_missing_midi_fails()
    test_missing_required_class_fails()
    test_too_short_audio_fails()
    print("test_inspect_slakh_dataset: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
