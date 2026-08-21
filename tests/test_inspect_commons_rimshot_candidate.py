#!/usr/bin/env python3
"""Unit tests for the Commons Rimshot candidate verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_commons_rimshot_candidate.py"
SPEC = importlib.util.spec_from_file_location("inspect_commons_rimshot_candidate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CommonsRimshotCandidateTests(unittest.TestCase):
    def test_render_records_source_verification_but_no_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.wav"
            with wave.open(str(path), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(100)
                output.writeframes(b"\0\0" * 100)
            old_sha1 = MODULE.EXPECTED_SHA1
            old_seconds = MODULE.EXPECTED_SECONDS
            try:
                MODULE.EXPECTED_SHA1 = MODULE.sha1(path)
                MODULE.EXPECTED_SECONDS = 1.0
                rendered = "\n".join(MODULE.render(path))
            finally:
                MODULE.EXPECTED_SHA1 = old_sha1
                MODULE.EXPECTED_SECONDS = old_seconds
        self.assertIn("sha1_verified=1", rendered)
        self.assertIn("source_labelled=1", rendered)
        self.assertIn("expected_rolls=4", rendered)
        self.assertIn("temporal_annotations=0", rendered)


if __name__ == "__main__":
    unittest.main()
