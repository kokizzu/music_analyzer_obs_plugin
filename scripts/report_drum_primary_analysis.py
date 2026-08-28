#!/usr/bin/env python3
"""Report running drum primary replays and the latest debug-output summaries."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def running_workers() -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "analyzer_drum_samples" in command:
            matches.append((entry.name, command))
    return matches


def main() -> int:
    workers = running_workers()
    print(f"active_drum_primary_workers={len(workers)}")
    for pid, command in workers:
        print(f"pid={pid} command={command}")
    for path in sorted(BUILD.glob("*_primary_debug.out")):
        print(f"## {path.relative_to(ROOT)} exists={path.exists()}")
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-16:]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
