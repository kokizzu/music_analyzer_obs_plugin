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
        executable = PORTABLE / f"{name}.exe"
        diagnostic_log = executable.with_suffix(".log")
        try:
            log_start = diagnostic_log.stat().st_size
        except OSError:
            log_start = 0
        result = subprocess.run(
            [
                "wine",
                str(executable),
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
        diagnostic_output = ""
        try:
            with diagnostic_log.open("r", encoding="utf-8", errors="replace") as stream:
                stream.seek(log_start)
                diagnostic_output = stream.read()
        except OSError:
            pass
        output = result.stdout + diagnostic_output
        if result.returncode != 1:
            raise SystemExit(f"{name}: expected missing-required-device exit 1, got {result.returncode}\n{output}")
        expected_status = "Windows hardware probe: midi=not-found litejam=not-found fret-zealot=not-found"
        if expected_status not in result.stdout:
            raise SystemExit(f"{name}: missing probe status\n{output}")
        print(f"{name}: required-device failure/status passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
