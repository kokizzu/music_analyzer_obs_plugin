#!/usr/bin/env python3
"""Locate source, Make, and script references for the GAPS guitar replay."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".cpp", ".hpp", ".py", ".sh", ".mk", ""}
SKIP = {".git", "build"}


def eligible(path: Path) -> bool:
    return path.suffix in SUFFIXES or path.name == "Makefile"


def main() -> int:
    matches: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP for part in path.parts) or not path.is_file() or not eligible(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "gaps" in text.lower():
            matches.append(path)
    print(f"gaps_reference_files={len(matches)}")
    for path in matches:
        print(path.relative_to(ROOT))
    print("gaps_make_targets")
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.startswith(("\t", "#", " ")) and "gaps" in line.lower():
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
