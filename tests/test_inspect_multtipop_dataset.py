#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import generate_multtipop_fixture
import inspect_multtipop_dataset


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


def run_with_env(root, required_segments=20, require_audio=False):
    with patched_env(
        {
            "MUSIC_ANALYZER_MULTTIPOP_ROOT": str(root),
            "MULTTIPOP_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_MULTTIPOP_REQUIRED_SEGMENTS": str(required_segments),
            "MUSIC_ANALYZER_MULTTIPOP_MIN_NOTE_PARTS": "2",
            "MUSIC_ANALYZER_MULTTIPOP_MIN_PITCH_CLASSES": "2",
            "MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO": "1" if require_audio else None,
            "MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT": None,
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_multtipop_dataset.main()


def test_complete_multtipop_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_multtipop_fixture.write_fixture(str(root), segment_count=20, write_audio=False)
        if run_with_env(root) != 0:
            raise AssertionError("complete MulTTiPop-shaped fixture should pass")


def test_incomplete_multtipop_shape_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_multtipop_fixture.write_fixture(str(root), segment_count=1, write_audio=False)
        if run_with_env(root, required_segments=2) == 0:
            raise AssertionError("incomplete MulTTiPop-shaped fixture should fail")


def test_audio_required_mode_checks_local_audio():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_multtipop_fixture.write_fixture(str(root), segment_count=20, write_audio=False)
        if run_with_env(root, required_segments=20, require_audio=True) == 0:
            raise AssertionError("audio-required MulTTiPop fixture without audio should fail")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        generate_multtipop_fixture.write_fixture(str(root), segment_count=20, write_audio=True)
        if run_with_env(root, required_segments=20, require_audio=True) != 0:
            raise AssertionError("audio-required MulTTiPop fixture with audio should pass")


def main():
    test_complete_multtipop_shape_passes()
    test_incomplete_multtipop_shape_fails()
    test_audio_required_mode_checks_local_audio()
    print("test_inspect_multtipop_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
