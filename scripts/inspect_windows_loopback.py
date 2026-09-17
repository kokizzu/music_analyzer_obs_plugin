#!/usr/bin/env python3
"""Print the Windows loopback capture implementation and its standalone call sites."""

from pathlib import Path


def print_file(path: Path) -> None:
    print(f"[{path}]")
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        print(f"{number:4}: {line}")


def main() -> int:
    print_file(Path("src/windows_loopback.hpp"))
    print_file(Path("src/standalone.cpp"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
