#!/usr/bin/env python3
"""Report whether the dedicated URMP real-audio test binary is still running."""

from pathlib import Path


def main() -> None:
    matches: list[tuple[str, str]] = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            command = (process / "cmdline").read_bytes().replace(b"\0", b" ").decode()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue
        if "analyzer_urmp" in command or "test-analyzer-urmp" in command:
            matches.append((process.name, command))
    if not matches:
        print("analyzer_urmp: no running process")
        return
    for pid, command in matches:
        print(f"analyzer_urmp: pid={pid} command={command}")


if __name__ == "__main__":
    main()
