#!/usr/bin/env python3
"""Stop only the resumable IDMT-SMT-Bass importer, preserving its partial archive."""

from __future__ import annotations

import os
import pathlib
import signal


def main() -> int:
    stopped: list[str] = []
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "import_idmt_bass_archive.py" not in command and "IDMT-SMT-BASS.zip.part" not in command:
            continue
        os.kill(int(proc.name), signal.SIGTERM)
        stopped.append(proc.name)
    print("stopped import pids: " + (", ".join(stopped) if stopped else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
