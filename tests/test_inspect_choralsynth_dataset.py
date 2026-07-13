#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import generate_choralsynth_fixture
import inspect_choralsynth_dataset


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


def run_with_env(root, required_pieces=20, min_audio_seconds=1.0):
    with patched_env(
        {
            "MUSIC_ANALYZER_CHORALSYNTH_ROOT": str(root),
            "CHORALSYNTH_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_CHORALSYNTH_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_CHORALSYNTH_MIN_AUDIO_SECONDS": str(min_audio_seconds),
            "MUSIC_ANALYZER_CHORALSYNTH_MIN_VOICES": "4",
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_choralsynth_dataset.main()


def test_complete_choralsynth_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        if run_with_env(root) != 0:
            raise AssertionError("complete ChoralSynth-shaped fixture should pass")


def test_missing_score_midi_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        (root / "01_Fixture_Chorale" / "score.midi").unlink()
        if run_with_env(root) == 0:
            raise AssertionError("ChoralSynth-shaped fixture with missing score MIDI should fail")


def test_missing_voice_audio_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        for audio in (root / "01_Fixture_Chorale" / "voices").glob("*.wav"):
            audio.unlink()
        if run_with_env(root) == 0:
            raise AssertionError("ChoralSynth-shaped fixture with missing voice audio should fail")


def test_too_short_readable_audio_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_fixture(root)
        if run_with_env(root, min_audio_seconds=3.0) == 0:
            raise AssertionError("ChoralSynth-shaped fixture with too-short audio should fail")


def main():
    test_complete_choralsynth_shape_passes()
    test_missing_score_midi_fails()
    test_missing_voice_audio_fails()
    test_too_short_readable_audio_fails()
    print("test_inspect_choralsynth_dataset: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
