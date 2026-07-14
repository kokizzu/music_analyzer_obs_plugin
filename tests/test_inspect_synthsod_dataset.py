#!/usr/bin/env python3
import contextlib
import os
import tempfile
from pathlib import Path

import generate_synthsod_fixture
import inspect_synthsod_dataset


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
    if generate_synthsod_fixture.main(["generate_synthsod_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_inspector(root, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_SYNTHSOD_ROOT": str(root / "SynthSOD-data"),
            "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT": str(root / "SynthSOD-aligned-scores"),
            "SYNTHSOD_PATH": None,
            "SYNTHSOD_SCORES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SYNTHSOD_REQUIRED_PIECES": str(required_pieces),
        }
    ):
        return inspect_synthsod_dataset.main()


def test_synthsod_fixture_accepts_documented_layout():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        write_fixture(root)
        if run_inspector(root) != 0:
            raise AssertionError("SynthSOD inspector should accept generated documented layout")


def test_synthsod_fixture_requires_enough_entries():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        write_fixture(root)
        if run_inspector(root, required_pieces=21) == 0:
            raise AssertionError("SynthSOD inspector should enforce required piece count")


def test_synthsod_fixture_requires_source_audio():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        write_fixture(root)
        (root / "SynthSOD-data" / "SYNTHSOD_001" / "Close Mic" / "Violin_1.wav").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("SynthSOD inspector should reject missing source audio")


def test_synthsod_fixture_requires_aligned_score():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "synthsod"
        write_fixture(root)
        (root / "SynthSOD-aligned-scores" / "SYNTHSOD_001.txt").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("SynthSOD inspector should reject missing aligned score text")


def main():
    test_synthsod_fixture_accepts_documented_layout()
    test_synthsod_fixture_requires_enough_entries()
    test_synthsod_fixture_requires_source_audio()
    test_synthsod_fixture_requires_aligned_score()
    print("test_inspect_synthsod_dataset: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
