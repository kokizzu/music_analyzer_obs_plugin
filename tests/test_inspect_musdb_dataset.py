#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import generate_musdb_fixture
import inspect_musdb_dataset


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
            "MUSIC_ANALYZER_MUSDB_ROOT": str(root),
            "MUSDB_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_MUSDB_REQUIRED_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_MUSDB_MIN_AUDIO_SECONDS": str(min_audio_seconds),
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_musdb_dataset.main()


def test_complete_musdb_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        if generate_musdb_fixture.main(["generate_musdb_fixture.py", str(root)]) != 0:
            raise AssertionError("fixture generation failed")
        if run_with_env(root) != 0:
            raise AssertionError("complete MUSDB-shaped fixture should pass")


def test_missing_stem_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        if generate_musdb_fixture.main(["generate_musdb_fixture.py", str(root)]) != 0:
            raise AssertionError("fixture generation failed")
        (root / "train" / "fixture_track_001" / "vocals.wav").unlink()
        if run_with_env(root) == 0:
            raise AssertionError("MUSDB-shaped fixture with a missing stem should fail")


def test_too_short_audio_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        if generate_musdb_fixture.main(["generate_musdb_fixture.py", str(root)]) != 0:
            raise AssertionError("fixture generation failed")
        if run_with_env(root, min_audio_seconds=2.0) == 0:
            raise AssertionError("MUSDB-shaped fixture with too-short stems should fail")


def main():
    test_complete_musdb_shape_passes()
    test_missing_stem_fails()
    test_too_short_audio_fails()
    print("test_inspect_musdb_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
