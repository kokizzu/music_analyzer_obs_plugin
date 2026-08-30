#!/usr/bin/env python3
"""Manage a resumable external-only MedleyDB sample archive download."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = Path(os.environ.get(
    "MUSIC_ANALYZER_FIXTURE_CACHE", "/media/kyz/sshflashtor/InstrumentSamples/build-cache"
))
DESTINATION = CACHE_ROOT / "medleydb_sample"
ARCHIVE = DESTINATION / "MedleyDB_Sample.tar.gz"
URL = "https://zenodo.org/record/1438309/files/MedleyDB_Sample.tar.gz?download=1"
PID_FILE = REPO_ROOT / "build" / "medleydb_sample_download.pid"
LOG_FILE = REPO_ROOT / "build" / "medleydb_sample_download.log"


def download() -> int:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        offset = ARCHIVE.stat().st_size if ARCHIVE.is_file() else 0
        headers = {"User-Agent": "music-analyzer-fixture-fetch/1"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(URL, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                if offset and response.status != 206:
                    ARCHIVE.unlink(missing_ok=True)
                    offset = 0
                mode = "ab" if offset else "wb"
                with ARCHIVE.open(mode) as output:
                    while chunk := response.read(1024 * 1024):
                        output.write(chunk)
            print(f"archive={ARCHIVE}", flush=True)
            print(f"bytes={ARCHIVE.stat().st_size}", flush=True)
            return 0
        except TimeoutError:
            if attempt == 3:
                raise
            print(f"retry={attempt + 1}", flush=True)
            time.sleep(2**attempt)
    return 1


def process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def start() -> int:
    if PID_FILE.is_file():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            pid = 0
        if pid and process_running(pid):
            print(f"status=running pid={pid}")
            return 0
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), "download"],
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    PID_FILE.write_text(f"{process.pid}\n", encoding="utf-8")
    print(f"status=started pid={process.pid} log={LOG_FILE}")
    return 0


def status() -> int:
    pid = 0
    if PID_FILE.is_file():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    print(f"status={'running' if pid and process_running(pid) else 'complete'}" + (f" pid={pid}" if pid else ""))
    if ARCHIVE.is_file():
        print(f"archive-bytes={ARCHIVE.stat().st_size}")
    if LOG_FILE.is_file():
        lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-12:]:
            print(line)
    return 0


def stop() -> int:
    if not PID_FILE.is_file():
        print("status=not-running")
        return 0
    pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    if process_running(pid):
        os.kill(pid, 15)
        print(f"status=stopped pid={pid}")
    else:
        print("status=not-running")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("download", "start", "status", "stop"))
    args = parser.parse_args()
    if args.command == "download":
        raise SystemExit(download())
    if args.command == "start":
        raise SystemExit(start())
    if args.command == "status":
        raise SystemExit(status())
    raise SystemExit(stop())
