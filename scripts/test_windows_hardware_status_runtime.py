#!/usr/bin/env python3
"""Exercise the Windows hardware-only status contract under Wine."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "windows-x64"
PORTABLE = BUILD / "portable"


def main() -> int:
    env = dict(os.environ)
    env.update(
        {
            "WINEPREFIX": str(BUILD / "wine-test-prefix"),
            "WINEDEBUG": "-all",
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
        }
    )
    for name in ("MusicAnalyzer", "HalfMusicAnalyzer"):
        result = subprocess.run(
            [
                "wine",
                str(PORTABLE / f"{name}.exe"),
                "--hardware-only",
                "--hardware-root",
                "G",
                "--require-midi",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        if result.returncode != 1:
            raise SystemExit(f"{name}: expected missing-required-device exit 1, got {result.returncode}\n{result.stdout}")
        expected_status = "Windows hardware probe: midi=not-found litejam=not-found fret-zealot=not-found"
        if expected_status not in result.stdout:
            raise SystemExit(f"{name}: missing probe status\n{result.stdout}")
        print(f"{name}: required-device failure/status passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
