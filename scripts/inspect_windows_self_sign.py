#!/usr/bin/env python3
"""Print the local self-signing helper for deployment review."""

from __future__ import annotations

from pathlib import Path


PATH = Path(__file__).resolve().parent / "windows_self_sign.py"


def main() -> None:
    print(PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
