#!/usr/bin/env python3
"""Run the Windows hardware-only path under Wine without attached devices."""

import os
import signal
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTABLE = ROOT / "build" / "windows-x64" / "portable"


def main() -> int:
    for name in ("MusicAnalyzer.exe", "HalfMusicAnalyzer.exe"):
        executable = PORTABLE / name
        process = subprocess.Popen(
            ["wine", str(executable), "--hardware-only", "--hardware-root", "G", "--no-hardware"],
            cwd=PORTABLE,
            env={**os.environ, "WINEDEBUG": "-all"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            print(f"{name}: timed out")
            if stdout:
                print(stdout.rstrip())
            if stderr:
                print(stderr.rstrip())
            return 1
        result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
        if result.returncode != 0:
            print(f"{name}: failed with exit {result.returncode}")
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1
        print(f"{name}: hardware-only lifecycle passed")
    return 0


raise SystemExit(main())
