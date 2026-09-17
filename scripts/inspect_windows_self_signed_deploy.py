#!/usr/bin/env python3
"""Print the mounted self-signed deployment helper for review."""

from __future__ import annotations

from pathlib import Path


PATH = Path(__file__).resolve().parent / "deploy_windows_self_signed.py"


def main() -> None:
    print(PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
