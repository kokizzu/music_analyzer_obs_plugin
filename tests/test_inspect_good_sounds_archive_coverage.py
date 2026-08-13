#!/usr/bin/env python3
"""Regression coverage for the read-only Good Sounds archive inventory."""

from __future__ import annotations

import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_good_sounds_archive_coverage.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_name:
        temp = pathlib.Path(temp_name)
        database = temp / "good_sounds.sqlite"
        connection = sqlite3.connect(database)
        connection.executescript(
            """
            CREATE TABLE sounds (id INTEGER PRIMARY KEY, instrument TEXT, dynamics TEXT);
            CREATE TABLE takes (id INTEGER PRIMARY KEY, sound_id INTEGER, filename TEXT, semitone INTEGER);
            INSERT INTO sounds VALUES (1, 'violin', 'mf');
            INSERT INTO sounds VALUES (2, 'sax-tenor', 'mf');
            INSERT INTO takes VALUES (11, 1, 'violin.flac', 60);
            INSERT INTO takes VALUES (12, 2, 'missing.flac', 60);
            """
        )
        connection.close()
        archive = temp / "good-sounds.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.write(database, "good_sounds.sqlite")
            output.writestr("sound_files/violin.flac", b"not decoded by the inventory")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(archive), "--top", "4"],
            check=True,
            capture_output=True,
            text=True,
        )
    if "available=1" not in result.stdout or "missing_audio=1" not in result.stdout:
        raise AssertionError(result.stdout)
    if "other/violin samples=1 distinct_notes=1" not in result.stdout:
        raise AssertionError(result.stdout)
    print("test_inspect_good_sounds_archive_coverage: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
