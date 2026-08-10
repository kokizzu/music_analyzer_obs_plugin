#!/usr/bin/env python3
"""Regression checks for the external instrument-sample store guard."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "configure_instrument_sample_store.py"
SPEC = importlib.util.spec_from_file_location("configure_instrument_sample_store", MODULE_PATH)
assert SPEC and SPEC.loader
STORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STORE)


class InstrumentSampleStoreTest(unittest.TestCase):
    def test_configure_creates_and_verifies_matching_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "external" / "InstrumentSamples"
            target.mkdir(parents=True)
            link = root / "build" / "InstrumentSamples"

            self.assertEqual(STORE.configure(link, target), 0)
            self.assertTrue(link.is_symlink())
            self.assertEqual(STORE.describe(link, target), 0)

    def test_configure_refuses_existing_directory_or_wrong_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "external" / "InstrumentSamples"
            target.mkdir(parents=True)
            link = root / "build" / "InstrumentSamples"
            link.mkdir(parents=True)
            self.assertEqual(STORE.configure(link, target), 1)

            link.rmdir()
            different = root / "different"
            different.mkdir()
            link.symlink_to(different, target_is_directory=True)
            self.assertEqual(STORE.configure(link, target), 1)


if __name__ == "__main__":
    unittest.main()
