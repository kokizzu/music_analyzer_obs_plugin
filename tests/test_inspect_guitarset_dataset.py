#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import generate_guitarset_fixture
import inspect_guitarset_dataset


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


def run_with_env(root, required_excerpts=20, require_hex_audio=True):
    with patched_env(
        {
            "MUSIC_ANALYZER_GUITARSET_ROOT": str(root),
            "GUITARSET_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS": str(required_excerpts),
            "MUSIC_ANALYZER_GUITARSET_MIN_NOTE_ANNOTATIONS": "6",
            "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_ANNOTATIONS": "2",
            "MUSIC_ANALYZER_GUITARSET_MIN_NOTE_EVENTS": "12",
            "MUSIC_ANALYZER_GUITARSET_MIN_HEX_CHANNELS": "6",
            "MUSIC_ANALYZER_GUITARSET_REQUIRE_HEX_AUDIO": "1" if require_hex_audio else "0",
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_guitarset_dataset.main()


def test_complete_guitarset_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_guitarset_fixture.write_fixture(str(root), excerpt_count=20, write_audio=True)
        if run_with_env(root) != 0:
            raise AssertionError("complete GuitarSet-shaped fixture should pass")


def test_incomplete_guitarset_shape_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_guitarset_fixture.write_fixture(str(root), excerpt_count=1, write_audio=True)
        if run_with_env(root, required_excerpts=2) == 0:
            raise AssertionError("incomplete GuitarSet-shaped fixture should fail")


def test_hex_audio_required_mode_checks_local_audio():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_guitarset_fixture.write_fixture(str(root), excerpt_count=20, write_audio=False)
        if run_with_env(root, required_excerpts=20, require_hex_audio=True) == 0:
            raise AssertionError("GuitarSet fixture without audio should fail when hex audio is required")


def main():
    test_complete_guitarset_shape_passes()
    test_incomplete_guitarset_shape_fails()
    test_hex_audio_required_mode_checks_local_audio()
    print("test_inspect_guitarset_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
