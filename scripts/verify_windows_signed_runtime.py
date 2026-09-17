#!/usr/bin/env python3
"""Run the signed Windows bundle locally under Wine, including the hardware probe path."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "windows-x64-self-signed" / "portable"
WINE_PREFIX = ROOT / "build" / "windows-x64" / "signed-wine-test-prefix"
EXECUTABLES = ("MusicAnalyzer.exe", "HalfMusicAnalyzer.exe")


def run(wine: str, executable: Path, *arguments: str) -> str:
    environment = dict(os.environ)
    environment.update(
        {
            "WINEPREFIX": str(WINE_PREFIX),
            "WINEDEBUG": "-all",
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
        }
    )
    log_path = executable.with_suffix(".log")
    try:
        log_start = log_path.stat().st_size
    except OSError:
        log_start = 0
    result = subprocess.run(
        [wine, str(executable), *arguments],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
        timeout=30,
    )
    diagnostic_output = ""
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as stream:
            stream.seek(log_start)
            diagnostic_output = stream.read()
    except OSError:
        pass
    output = result.stdout + diagnostic_output
    if result.returncode != 0:
        raise SystemExit(f"{executable.name} {' '.join(arguments)} failed with {result.returncode}:\n{output}")
    return output


def main() -> int:
    wine = shutil.which("wine")
    if wine is None:
        raise SystemExit("Wine is required for the signed Windows runtime check")
    if not BUILD.is_dir():
        raise SystemExit(f"signed portable build is unavailable: {BUILD}")
    for name in EXECUTABLES:
        executable = BUILD / name
        if not executable.is_file():
            raise SystemExit(f"missing signed executable: {executable}")
        self_test = run(wine, executable, "--self-test")
        if "standalone self-test: ok" not in self_test:
            raise SystemExit(f"{name} signed self-test did not pass")
        hardware = run(wine, executable, "--hardware-only", "--hardware-root", "G")
        if "Windows hardware probe:" not in hardware:
            raise SystemExit(f"{name} signed hardware probe did not run")
        print(f"{name}: signed local self-test and hardware probe passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
