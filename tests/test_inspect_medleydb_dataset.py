#!/usr/bin/env python3
import contextlib
import io
import os
import tempfile
from pathlib import Path

import inspect_medleydb_dataset


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


def write_empty(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def create_medleydb_shape(root, annotation_root, count):
    for index in range(1, count + 1):
        track_id = f"Artist_Song{index:02d}"
        track_dir = root / track_id
        write_empty(track_dir / f"{track_id}_MIX.wav")
        write_empty(track_dir / f"{track_id}_STEM_01.wav")
        write_empty(track_dir / "stems" / f"{track_id}_STEM_02.wav")
        write_empty(annotation_root / f"{track_id}_MELODY1.csv")


def run_with_env(root, annotation_root, required_tracks, required_melody_tracks):
    with patched_env(
        {
            "MUSIC_ANALYZER_MEDLEYDB_ROOT": str(root),
            "MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT": str(annotation_root),
            "MUSIC_ANALYZER_MEDLEYDB_REQUIRED_TRACKS": str(required_tracks),
            "MUSIC_ANALYZER_MEDLEYDB_REQUIRED_MELODY_TRACKS": str(required_melody_tracks),
            "MUSIC_ANALYZER_MEDLEYDB_MIN_STEMS": "2",
            "MUSIC_ANALYZER_MEDLEYDB_ALLOW_NO_MELODY": None,
            "MEDLEYDB_PATH": None,
            "MEDLEYDB_ANNOTATIONS_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
        }
    ):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return inspect_medleydb_dataset.main()


def test_complete_medleydb_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        audio_root = temp_root / "MedleyDB"
        annotation_root = temp_root / "Annotations"
        create_medleydb_shape(audio_root, annotation_root, 20)
        if run_with_env(audio_root, annotation_root, 20, 20) != 0:
            raise AssertionError("complete MedleyDB-shaped fixture should pass")


def test_incomplete_medleydb_shape_fails():
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        audio_root = temp_root / "MedleyDB"
        annotation_root = temp_root / "Annotations"
        create_medleydb_shape(audio_root, annotation_root, 1)
        if run_with_env(audio_root, annotation_root, 2, 1) == 0:
            raise AssertionError("incomplete MedleyDB-shaped fixture should fail")


def main():
    test_complete_medleydb_shape_passes()
    test_incomplete_medleydb_shape_fails()
    print("test_inspect_medleydb_dataset: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
