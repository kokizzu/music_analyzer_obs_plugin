#!/usr/bin/env python3
"""Report active processes belonging to the parallel real-world sample gate."""

from pathlib import Path


NEEDLES = (
    "real_world_samples_parallel",
    "analyzer_real_note_samples",
    "analyzer_drum_samples",
    "find_real_note_attribute_patterns",
)


def main() -> int:
    matches = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        except OSError:
            continue
        if any(needle in command for needle in NEEDLES):
            matches.append((int(entry.name), command))
    for pid, command in sorted(matches):
        print(f"{pid}: {command}")
    print(f"active real-world sample processes: {len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
