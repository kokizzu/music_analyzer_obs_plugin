#!/usr/bin/env python3
"""Report CIFS mount and SMB TCP reachability without mutating the system."""

from pathlib import Path
import shutil
import socket
import subprocess


MOUNTPOINT = Path("/media/kyz/aigenshared")
HOST = "192.168.1.132"
PORT = 445


def command(args: list[str], timeout: float) -> tuple[int, str]:
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return 124, str(error)
    return result.returncode, (result.stdout + result.stderr).strip()


def main() -> int:
    findmnt_code, findmnt_output = command(
        ["findmnt", "-T", str(MOUNTPOINT), "-o", "SOURCE,TARGET,FSTYPE"], 5
    )
    print(f"findmnt_exit={findmnt_code}")
    print(f"findmnt={findmnt_output or '(none)'}")

    stat_code, stat_output = command(["stat", "-c", "%F", str(MOUNTPOINT)], 5)
    print(f"mountpoint_stat_exit={stat_code}")
    print(f"mountpoint_stat={stat_output or '(none)'}")

    try:
        with socket.create_connection((HOST, PORT), timeout=3):
            print(f"tcp_{PORT}=reachable host={HOST}")
    except OSError as error:
        print(f"tcp_{PORT}=unreachable host={HOST} error={error}")

    print(f"smbclient={shutil.which('smbclient') or 'missing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
