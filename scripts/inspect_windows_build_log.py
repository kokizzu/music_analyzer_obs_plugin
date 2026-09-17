#!/usr/bin/env python3
"""Print the current Windows standalone compiler log."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    candidates = sorted((REPO_ROOT / "build").glob("windows-x64/**/*.log"))
    if not candidates:
        raise SystemExit("no Windows build log found")
    for path in candidates:
        print(f"=== {path.relative_to(REPO_ROOT)} ===")
        print(path.read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    main()
