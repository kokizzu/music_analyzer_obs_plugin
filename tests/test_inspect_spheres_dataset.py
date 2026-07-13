#!/usr/bin/env python3
import contextlib
import io
import os
import struct
import tempfile
import wave
from pathlib import Path

import inspect_spheres_dataset


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


def write_audio_marker(path, seconds=1.0):
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 8000
    frame_count = int(sample_rate * seconds)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"".join(struct.pack("<h", 0) for _ in range(frame_count)))


def create_complete_spheres_shape(root):
    for piece in ("Mozart_Symphony_No_40", "Tchaikovsky_Romeo_And_Juliet"):
        for folder in ("Stereo Mix", "Main L"):
            write_audio_marker(root / piece / folder / "Violin_I.wav")
            write_audio_marker(root / piece / folder / "Cello.wav")


def run_with_env(root, required_pieces=2, required_folders=2, min_audio_files=2, min_audio_seconds=0.5):
    with patched_env(
        {
            "MUSIC_ANALYZER_SPHERES_ROOT": str(root),
            "SPHERES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SPHERES_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_SPHERES_REQUIRED_RECONSTRUCTABLE_FOLDERS": str(required_folders),
            "MUSIC_ANALYZER_SPHERES_REQUIRED_SOURCE_FOLDERS": "1",
            "MUSIC_ANALYZER_SPHERES_MIN_AUDIO_FILES_PER_FOLDER": str(min_audio_files),
            "MUSIC_ANALYZER_SPHERES_MIN_AUDIO_SECONDS": str(min_audio_seconds),
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_spheres_dataset.main()


def test_complete_spheres_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        create_complete_spheres_shape(root)
        if run_with_env(root) != 0:
            raise AssertionError("complete Spheres-shaped fixture should pass")


def test_incomplete_spheres_shape_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_audio_marker(root / "Mozart_Symphony_No_40" / "Stereo Mix" / "Violin_I.wav")
        write_audio_marker(root / "Mozart_Symphony_No_40" / "Main L" / "Cello.wav")
        if run_with_env(root) == 0:
            raise AssertionError("incomplete Spheres-shaped fixture should fail")


def test_too_short_spheres_audio_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        create_complete_spheres_shape(root)
        for path in root.rglob("*.wav"):
            write_audio_marker(path, seconds=0.1)
        if run_with_env(root) == 0:
            raise AssertionError("too-short Spheres-shaped audio should fail")


def main():
    test_complete_spheres_shape_passes()
    test_incomplete_spheres_shape_fails()
    test_too_short_spheres_audio_fails()
    print("test_inspect_spheres_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
