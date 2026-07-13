#!/usr/bin/env python3
import contextlib
import os
import tempfile
from pathlib import Path

import generate_polyvocal_fixture
import inspect_polyvocal_dataset


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
    if generate_polyvocal_fixture.main(["generate_polyvocal_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_inspector(root, required_pieces=20, require_source_audio=False):
    with patched_env(
        {
            "MUSIC_ANALYZER_POLYVOCAL_ROOT": str(root),
            "POLYVOCAL_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_POLYVOCAL_REQUIRED_PIECES": str(required_pieces),
            "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO": "1" if require_source_audio else None,
        }
    ):
        return inspect_polyvocal_dataset.main()


def test_inspect_polyvocal_fixture_accepts_mtracks_layout():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        write_fixture(root)
        if run_inspector(root) != 0:
            raise AssertionError("polyvocal inspector should accept generated mtracks layout")


def test_inspect_polyvocal_fixture_requires_enough_entries():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        write_fixture(root)
        if run_inspector(root, required_pieces=21) == 0:
            raise AssertionError("polyvocal inspector should enforce required piece count")


def test_inspect_polyvocal_fixture_requires_f0_annotations():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        write_fixture(root)
        (root / "annotations" / "PV001_soprano.csv").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("polyvocal inspector should reject missing selected F0 annotations")


def test_inspect_polyvocal_fixture_can_require_source_audio():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "polyvocal"
        write_fixture(root)
        if run_inspector(root, require_source_audio=True) != 0:
            raise AssertionError("polyvocal inspector should accept generated source voice audio")
        (root / "voice_audio" / "PV001_soprano.wav").unlink()
        if run_inspector(root, require_source_audio=True) == 0:
            raise AssertionError("polyvocal inspector should reject missing required source voice audio")


def main():
    test_inspect_polyvocal_fixture_accepts_mtracks_layout()
    test_inspect_polyvocal_fixture_requires_enough_entries()
    test_inspect_polyvocal_fixture_requires_f0_annotations()
    test_inspect_polyvocal_fixture_can_require_source_audio()
    print("test_inspect_polyvocal_dataset: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
