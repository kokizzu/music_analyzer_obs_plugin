#!/usr/bin/env python3
"""Locate local URMP datasets without downloading or modifying anything."""

from pathlib import Path


ROOTS = (Path.home() / "Downloads", Path.home() / "Music", Path.home() / "datasets", Path.home() / "go/src")
SKIP_NAMES = {".cache", ".config", ".local", "node_modules", "build", ".git"}


def main() -> None:
    matches: set[Path] = set()
    for root in ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            relative_parts = path.relative_to(root).parts
            if any(part in SKIP_NAMES or part.startswith(".") for part in relative_parts):
                continue
            if "urmp" in path.name.lower() and path.is_dir():
                matches.add(path)
    if not matches:
        print("locate_urmp_fixture: no local URMP directory found in standard data locations")
        return
    for path in sorted(matches):
        print(path)


if __name__ == "__main__":
    main()
