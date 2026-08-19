#!/usr/bin/env python3
"""Report the state of the resumable BabySlakh download."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive = args.archive
    state_dir = archive.parent
    part = archive.with_name(archive.name + ".part")

    if archive.is_file():
        print(f"state=downloaded size_bytes={archive.stat().st_size}")
        return 0
    service = subprocess.run(
        ["systemctl", "--user", "is-active", "--quiet", "music-analyzer-babyslakh-download.service"],
        check=False,
    )
    print("state=running" if service.returncode == 0 else "state=not_running")
    details = subprocess.run(
        [
            "systemctl", "--user", "show", "music-analyzer-babyslakh-download.service",
            "--property=ActiveState", "--property=SubState", "--property=ExecMainStatus", "--property=MainPID",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    main_pid = 0
    for line in details.stdout.splitlines():
        print(f"service_{line}")
        if line.startswith("MainPID="):
            main_pid = int(line.partition("=")[2] or "0")
    if main_pid:
        try:
            command = Path(f"/proc/{main_pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8").strip()
        except OSError:
            command = ""
        if command:
            print(f"service_command={command}")
        try:
            children = Path(f"/proc/{main_pid}/task/{main_pid}/children").read_text(encoding="utf-8").split()
        except OSError:
            children = []
        for child in children:
            try:
                command = Path(f"/proc/{child}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8").strip()
            except OSError:
                command = ""
            print(f"service_child_pid={child} command={command or 'unavailable'}")
        try:
            environment = Path(f"/proc/{main_pid}/environ").read_bytes().split(b"\0")
        except OSError:
            environment = []
        for variable in (b"http_proxy=", b"https_proxy=", b"HTTP_PROXY=", b"HTTPS_PROXY="):
            if any(item.startswith(variable) for item in environment):
                print(f"service_proxy_env={variable[:-1].decode('ascii')}:present")
    if part.is_file():
        partial_stat = part.stat()
        print(f"partial_bytes={partial_stat.st_size}")
        print(f"allocated_bytes={partial_stat.st_blocks * 512}")
    else:
        print("partial_bytes=0")
        print("allocated_bytes=0")
    journal = subprocess.run(
        [
            "journalctl", "--user", "--unit=music-analyzer-babyslakh-download.service",
            "--no-pager", "--output=cat", "--lines=8",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    for line in journal.stdout.splitlines():
        print(f"service_journal={line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
