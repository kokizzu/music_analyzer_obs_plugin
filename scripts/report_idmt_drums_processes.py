#!/usr/bin/env python3
"""Report running IDMT drum preparation and analyzer processes."""

from pathlib import Path


def main() -> None:
    matches = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            ).strip()
        except OSError:
            continue
        lowered = command.lower()
        if "idmt" in lowered or "analyzer_egmd" in lowered:
            matches.append((int(proc.name), command))
    if not matches:
        print("No running IDMT drum preparation or analyzer processes.")
        return
    for pid, command in sorted(matches):
        print(f"{pid}: {command}")


if __name__ == "__main__":
    main()
