#!/usr/bin/env python3
"""Stop only duplicate MAESTRO subset preparers started by this workflow."""

from __future__ import annotations

import os
import signal
from pathlib import Path


def main() -> int:
    ours = os.getpid()
    stopped: list[str] = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == ours:
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if "scripts/prepare_maps_piano_samples.py" not in command or "maestro_real_samples" not in command:
            continue
        try:
            os.kill(int(proc.name), signal.SIGTERM)
            stopped.append(proc.name)
        except ProcessLookupError:
            pass
    print(f"stop_maestro_real_subset_writers: stopped={','.join(stopped) or '0'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
