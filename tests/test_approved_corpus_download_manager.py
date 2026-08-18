#!/usr/bin/env python3
"""Exercise persisted terminal states for detached corpus jobs."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "scripts" / "start_approved_corpus_downloads.sh"
REPORT = ROOT / "scripts" / "report_approved_corpus_downloads.sh"


def wait_for_status(status_file: Path) -> None:
    deadline = time.monotonic() + 3.0
    while not status_file.exists():
        if time.monotonic() >= deadline:
            raise AssertionError(f"timed out waiting for {status_file}")
        time.sleep(0.01)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        fake_make = root / "fake-make"
        fake_make.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  succeeds) exit 0 ;;\n"
            "  fails) exit 7 ;;\n"
            "  *) exit 64 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake_make.chmod(0o755)
        build = root / "build"
        for target, expected in (("succeeds", "SUCCEEDED"), ("fails", "FAILED(exit=7)")):
            subprocess.run(["sh", str(START), str(fake_make), str(build), target], check=True)
            status = build / "corpus-download-jobs" / f"{target}.status"
            wait_for_status(status)
            report = subprocess.run(
                ["sh", str(REPORT), str(build), target], check=True, capture_output=True, text=True
            ).stdout
            assert report.startswith(f"{expected} target={target}"), report
    print("test_approved_corpus_download_manager: success and failure states passed")


if __name__ == "__main__":
    main()
