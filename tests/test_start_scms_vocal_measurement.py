#!/usr/bin/env python3
"""Regression checks for the detached SCMS vocal-measurement launcher."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "start_scms_vocal_measurement.sh"


def invoke(arguments: list[str], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/bin/sh", str(SCRIPT), *arguments], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False, env=environment)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        fake_bin = root / "bin"
        fake_bin.mkdir()
        captured = root / "make-arguments.txt"
        fake_make = fake_bin / "make"
        fake_make.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$MAKE_CAPTURE\"\n", encoding="utf-8")
        fake_make.chmod(fake_make.stat().st_mode | stat.S_IXUSR)
        environment = dict(os.environ, PATH=f"{fake_bin}:{os.environ['PATH']}", MAKE_CAPTURE=str(captured))
        pid = root / "measurement.pid"
        log = root / "measurement.log"
        status = invoke(["--status", "--pid-file", str(pid), "--log-file", str(log)], environment)
        assert status.returncode == 0 and "not running" in status.stdout
        started = invoke([
            "--pid-file", str(pid), "--log-file", str(log), "--workdir", str(root),
            "--limit", "1000", "--minimum-samples", "800",
        ], environment)
        assert started.returncode == 0 and "started" in started.stdout
        for _ in range(20):
            if captured.is_file():
                break
            time.sleep(0.02)
        assert captured.is_file()
        arguments = captured.read_text(encoding="utf-8")
        assert "SCMS_DATASET_SAMPLE_LIMIT=1000" in arguments
        assert "SCMS_DATASET_MIN_SAMPLES=800" in arguments
        assert "measure-scms-vocal-mix" in arguments
    print("test_start_scms_vocal_measurement: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
