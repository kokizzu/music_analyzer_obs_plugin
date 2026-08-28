#!/usr/bin/env python3
"""Report progress for the full real-note ownership attribute export."""

from __future__ import annotations

import pathlib


OUTPUT = pathlib.Path("build/real_note_full_mix_attributes.tsv")


def main() -> int:
    processes: list[str] = []
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "collect_real_note_full_mix_attributes.py" in command or "analyzer_real_note_samples" in command:
            processes.append(f"pid={proc.name} {command}")
    print("active collectors:")
    print("\n".join(processes) if processes else "none")
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8", errors="replace") as handle:
            lines = sum(1 for _ in handle)
        print(f"attribute bytes: {OUTPUT.stat().st_size}")
        print(f"attribute lines: {lines}")
    else:
        print("attribute file: absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
