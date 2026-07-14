#!/usr/bin/env python3
import contextlib
import os
import tempfile
from pathlib import Path

import generate_prepared_multitrack_fixture
import inspect_prepared_multitrack_dataset


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
    if generate_prepared_multitrack_fixture.main(["generate_prepared_multitrack_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_inspector(root, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT": str(root),
            "PREPARED_MULTITRACK_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES": str(required_pieces),
        }
    ):
        return inspect_prepared_multitrack_dataset.main()


def test_prepared_multitrack_fixture_accepts_manifest_layout():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "prepared"
        write_fixture(root)
        if run_inspector(root) != 0:
            raise AssertionError("prepared multitrack inspector should accept generated manifest layout")


def test_prepared_multitrack_fixture_requires_enough_entries():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "prepared"
        write_fixture(root)
        if run_inspector(root, required_pieces=21) == 0:
            raise AssertionError("prepared multitrack inspector should enforce required piece count")


def test_prepared_multitrack_fixture_requires_source_audio():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "prepared"
        write_fixture(root)
        (root / "audio" / "PMT001" / "violin.wav").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("prepared multitrack inspector should reject missing source audio")


def test_prepared_multitrack_fixture_requires_note_rows():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "prepared"
        write_fixture(root)
        (root / "annotations" / "PMT001" / "violin.csv").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("prepared multitrack inspector should reject missing note rows")


def main():
    test_prepared_multitrack_fixture_accepts_manifest_layout()
    test_prepared_multitrack_fixture_requires_enough_entries()
    test_prepared_multitrack_fixture_requires_source_audio()
    test_prepared_multitrack_fixture_requires_note_rows()
    print("test_inspect_prepared_multitrack_dataset: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
