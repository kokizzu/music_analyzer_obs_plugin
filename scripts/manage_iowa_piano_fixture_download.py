#!/usr/bin/env python3
"""Run the Iowa Piano fixture download outside a short interactive command window."""

import os
import signal
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PID_PATH = BUILD / "iowa_piano_fixture_download.pid"
LOG_PATH = BUILD / "iowa_piano_fixture_download.log"
PREPARE = ROOT / "scripts" / "prepare_iowa_piano_midrange_fixtures.py"


def running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    stat = Path("/proc") / str(pid) / "stat"
    return not stat.is_file() or stat.read_text(encoding="utf-8").split()[2] != "Z"


def read_pid() -> int | None:
    try:
        return int(PID_PATH.read_text(encoding="ascii").strip())
    except (FileNotFoundError, ValueError):
        return None


def show_tail() -> None:
    if not LOG_PATH.is_file():
        return
    for line in LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[-12:]:
        print(line)


def start() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    pid = read_pid()
    if pid is not None and running(pid):
        print(f"status=running pid={pid}")
        return 0
    PID_PATH.unlink(missing_ok=True)
    with LOG_PATH.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, str(PREPARE), "apply"], cwd=ROOT,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    PID_PATH.write_text(f"{process.pid}\n", encoding="ascii")
    print(f"status=started pid={process.pid} log={LOG_PATH}")
    return 0


def status() -> int:
    pid = read_pid()
    if pid is not None and running(pid):
        print(f"status=running pid={pid}")
        show_tail()
        return 0
    PID_PATH.unlink(missing_ok=True)
    print("status=complete")
    show_tail()
    return 0


def stop() -> int:
    pid = read_pid()
    if pid is not None and running(pid):
        os.killpg(pid, signal.SIGTERM)
        print(f"status=stopped pid={pid}")
    else:
        print("status=not-running")
    PID_PATH.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "status", "stop"}:
        raise SystemExit("usage: manage_iowa_piano_fixture_download.py start|status|stop")
    if sys.argv[1] == "start":
        raise SystemExit(start())
    if sys.argv[1] == "status":
        raise SystemExit(status())
    raise SystemExit(stop())
