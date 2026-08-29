#!/usr/bin/env python3
"""Run the long URMP attribute export without risking a partial cache."""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PID_PATH = BUILD / "urmp_profile_replay.pid"
LOG_PATH = BUILD / "urmp_profile_replay.log"
REPORT = ROOT / "scripts" / "report_urmp_other_recovery_profile.py"


def process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    stat_path = Path("/proc") / str(pid) / "stat"
    if stat_path.is_file():
        fields = stat_path.read_text(encoding="utf-8").split()
        return len(fields) > 2 and fields[2] != "Z"
    return True


def read_pid() -> int | None:
    try:
        return int(PID_PATH.read_text(encoding="ascii").strip())
    except (FileNotFoundError, ValueError):
        return None


def show_log_tail() -> None:
    if not LOG_PATH.is_file():
        return
    lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-12:]:
        print(line)


def start() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    pid = read_pid()
    if pid is not None and process_running(pid):
        print(f"status=running pid={pid}")
        return 0
    PID_PATH.unlink(missing_ok=True)
    with LOG_PATH.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(REPORT)],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    PID_PATH.write_text(f"{process.pid}\n", encoding="ascii")
    print(f"status=started pid={process.pid} log={LOG_PATH}")
    return 0


def status() -> int:
    pid = read_pid()
    if pid is not None and process_running(pid):
        print(f"status=running pid={pid}")
        show_log_tail()
        return 0
    if pid is not None:
        PID_PATH.unlink(missing_ok=True)
    print("status=complete")
    show_log_tail()
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "status"}:
        raise SystemExit("usage: manage_urmp_profile_replay.py start|status")
    return start() if sys.argv[1] == "start" else status()


if __name__ == "__main__":
    raise SystemExit(main())
