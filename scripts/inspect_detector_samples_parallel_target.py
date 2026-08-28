#!/usr/bin/env python3
"""Print the Makefile recipe for the aggregate detector sample gate."""

from pathlib import Path


TARGET = "test-detector-samples-parallel:"


def main() -> None:
    lines = Path("Makefile").read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(TARGET):
            for context_line in lines[index:index + 32]:
                print(context_line)
            return
    raise SystemExit(f"Makefile target not found: {TARGET[:-1]}")


if __name__ == "__main__":
    main()
