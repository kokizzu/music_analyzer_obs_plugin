#!/usr/bin/env python3
"""Print the final diagnostics from retained parallel drum regression logs."""

from pathlib import Path


def main() -> None:
    paths = set(Path("build").glob("test-*-drum*.log"))
    paths.update(Path("build").glob("test-drum*.log"))
    for path in sorted(paths):
        print(f"== {path} ==")
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-30:]:
            print(line)


if __name__ == "__main__":
    main()
