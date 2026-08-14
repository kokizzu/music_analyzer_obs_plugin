#!/usr/bin/env python3
"""Regression checks for Choral Singing Dataset archive inventory."""

from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_choral_singing_dataset_archive.py"
SPEC = importlib.util.spec_from_file_location("inspect_csd", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "csd.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("CSD/audio/soprano.wav", "audio")
            zipped.writestr("CSD/annotations/score.mid", "midi")
            zipped.writestr("README", "notes")
        files, roots, extensions = INSPECT.inventory(str(archive))
        assert files == ["CSD/annotations/score.mid", "CSD/audio/soprano.wav", "README"]
        assert roots == {"CSD": 2, "README": 1}
        assert extensions == {"mid": 1, "wav": 1, "(none)": 1}
    print("test_inspect_choral_singing_dataset_archive: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
