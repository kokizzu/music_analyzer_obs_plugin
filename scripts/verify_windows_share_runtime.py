#!/usr/bin/env python3
"""Run the signed Windows executables directly from the mounted share under Wine."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARE = Path("/media/kyz/aigenshared")
WINE_PREFIX = REPO_ROOT / "build/windows-x64/share-wine-test-prefix"
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
    diagnostic_log = executable.with_suffix(".log")
    try:
        log_start = diagnostic_log.stat().st_size
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
        with diagnostic_log.open("r", encoding="utf-8", errors="replace") as stream:
            stream.seek(log_start)
            diagnostic_output = stream.read()
    except OSError:
        pass
    if result.returncode != 0:
        raise SystemExit(
            f"{executable.name} {' '.join(arguments)} failed with {result.returncode}:\n"
            f"{result.stdout}{diagnostic_output}"
        )
    return result.stdout + diagnostic_output


def main() -> None:
    wine = shutil.which("wine")
    if wine is None:
        raise SystemExit("Wine is required for the mounted-share runtime check")
    if not SHARE.is_dir():
        raise SystemExit(f"mounted Windows share is unavailable: {SHARE}")

    for name in EXECUTABLES:
        executable = SHARE / name
        if not executable.is_file():
            raise SystemExit(f"missing deployed executable: {executable}")
        self_test = run(wine, executable, "--self-test")
        if "standalone self-test: ok" not in self_test:
            raise SystemExit(f"{name} did not report a successful self-test:\n{self_test}")
        hardware = run(wine, executable, "--hardware-only", "--hardware-root", "G")
        if "Windows hardware probe:" not in hardware:
            raise SystemExit(f"{name} did not reach the hardware probe:\n{hardware}")
        print(f"{name}: signed share self-test and hardware-only lifecycle passed")


if __name__ == "__main__":
    main()
