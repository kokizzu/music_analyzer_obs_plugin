#!/usr/bin/env python3
"""Show the HEAD and working high-soprano mirror implementation markers."""

from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PATHS = ("src/analyzer.hpp", "src/analyzer.cpp")
NEEDLES = (
    "kEnableMeasuredHighSopranoVocalMirror",
    "measured_high_soprano_vocal_mirror_supported",
    "adjacent_upper_ratio",
    "high-soprano",
)


def content_at_head(path: str) -> str:
    return subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def print_matches(label: str, path: str, content: str) -> None:
    print(f"=== {label} {path}")
    for number, line in enumerate(content.splitlines(), start=1):
        if any(needle in line for needle in NEEDLES):
            print(f"{number}: {line.strip()}")


def main() -> None:
    for path in PATHS:
        print_matches("HEAD", path, content_at_head(path))
        print_matches("WORKTREE", path, (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
