#!/usr/bin/env python3
"""Regression checks for the detached SCMS download launcher."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "start_scms_dataset_download.sh"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        pid_file = root / "download.pid"
        log_file = root / "download.log"
        result = subprocess.run(
            ["sh", str(SCRIPT), "--status", "--pid-file", str(pid_file), "--log-file", str(log_file)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        assert "not running" in result.stdout
        pid_file.write_text("999999\n", encoding="utf-8")
        result = subprocess.run(
            ["sh", str(SCRIPT), "--status", "--pid-file", str(pid_file), "--log-file", str(log_file)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        assert "not running" in result.stdout
        assert not pid_file.exists()
        archive_part = root / "Saraga-Carnatic-Melody-Synth.zip.part"
        archive_part.write_bytes(b"fixture")
        result = subprocess.run(
            [
                "sh", str(SCRIPT), "--status", "--pid-file", str(pid_file),
                "--log-file", str(log_file), "--archive-part", str(archive_part),
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        assert "archive_part logical_bytes=7" in result.stdout
        assert "allocated_bytes=" in result.stdout
    print("test_start_scms_dataset_download: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
