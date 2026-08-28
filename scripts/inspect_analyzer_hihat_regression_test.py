#!/usr/bin/env python3
"""Print the focused analyzer regression test structure for reuse."""

from pathlib import Path


def main() -> None:
    print(Path("tests/analyzer_hihat_regression.cpp").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
