#!/usr/bin/env python3
"""Regression checks for external sample-build directory migration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "migrate_sample_build_directories.py"
SPEC = importlib.util.spec_from_file_location("migrate_sample_build_directories", MODULE_PATH)
assert SPEC and SPEC.loader
MIGRATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATE)


class SampleBuildMigrationTest(unittest.TestCase):
    def test_migrates_sample_directories_but_not_tooling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            store = root / "external" / "InstrumentSamples"
            build.mkdir()
            store.mkdir(parents=True)
            source = build / "guitar_samples"
            source.mkdir()
            (source / "clip.wav").write_bytes(b"sample audio")
            android = build / "android-sdk"
            android.mkdir()
            (android / "tool").write_bytes(b"tooling")

            self.assertEqual(MIGRATE.migrate(build, store), 0)
            self.assertTrue(source.is_symlink())
            self.assertEqual((source / "clip.wav").read_bytes(), b"sample audio")
            self.assertTrue((store / "build-cache" / "guitar_samples").is_dir())
            self.assertTrue(android.is_dir())
            self.assertFalse(android.is_symlink())

    def test_refuses_to_overwrite_existing_external_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            store = root / "external" / "InstrumentSamples"
            build.mkdir()
            store.mkdir(parents=True)
            source = build / "real_sample_sources"
            source.mkdir()
            (source / "audio.wav").write_bytes(b"source")
            destination = store / "build-cache" / source.name
            destination.mkdir(parents=True)

            with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                MIGRATE.migrate(build, store)
            self.assertTrue(source.is_dir())
            self.assertFalse(source.is_symlink())


if __name__ == "__main__":
    unittest.main()
