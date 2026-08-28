#!/usr/bin/env python3
"""Stop only duplicate low-note shadow fixture checks started by this repository."""

import os
from pathlib import Path
import signal
import subprocess


def main() -> int:
    result = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                            capture_output=True)
    needle = "scripts/check_real_note_low_electronic_piano_guitar_shadow.py"
    stopped = []
    for line in result.stdout.splitlines():
        if needle not in line:
            continue
        pid_text, _ = line.strip().split(maxsplit=1)
        pid = int(pid_text)
        if pid == os.getpid():
            continue
        os.kill(pid, signal.SIGTERM)
        stopped.append(pid)
    print("stopped low-note shadow checks: " + (", ".join(map(str, stopped)) if stopped else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
