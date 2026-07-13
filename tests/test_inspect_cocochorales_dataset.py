#!/usr/bin/env python3
import contextlib
import os
import tempfile
from pathlib import Path

import generate_cocochorales_fixture
import inspect_cocochorales_dataset


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
    if generate_cocochorales_fixture.main(["generate_cocochorales_fixture.py", str(root)]) != 0:
        raise AssertionError("fixture generation failed")


def run_inspector(root, required_pieces=20):
    with patched_env(
        {
            "MUSIC_ANALYZER_COCOCHORALES_ROOT": str(root),
            "COCOCHORALES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES": str(required_pieces),
        }
    ):
        return inspect_cocochorales_dataset.main()


def test_complete_cocochorales_shape_passes():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "cocochorales"
        write_fixture(root)
        if run_inspector(root) != 0:
            raise AssertionError("complete CocoChorales-shaped fixture should pass")


def test_incomplete_cocochorales_shape_fails():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "cocochorales"
        write_fixture(root)
        (root / "train" / "cocochorales_fixture_00001" / "score.mid").unlink()
        if run_inspector(root) == 0:
            raise AssertionError("fixture missing one score MIDI should fail")


def test_dataset_root_child_detection():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "CocoChorales"
        write_fixture(root)
        with patched_env(
            {
                "MUSIC_ANALYZER_DATASET_ROOT": temp,
                "MUSIC_ANALYZER_COCOCHORALES_ROOT": None,
                "COCOCHORALES_PATH": None,
                "MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES": "20",
            }
        ):
            if inspect_cocochorales_dataset.main() != 0:
                raise AssertionError("generic dataset root with CocoChorales child should pass")


def main():
    test_complete_cocochorales_shape_passes()
    test_incomplete_cocochorales_shape_fails()
    test_dataset_root_child_detection()
    print("test_inspect_cocochorales_dataset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
