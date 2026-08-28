#!/usr/bin/env python3
"""Show the Make recipes for the focused IDMT bass diagnostics."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def show_target(lines: list[str], target: str) -> None:
    for index, line in enumerate(lines):
        if line.startswith(f"{target}:"):
            print(f"{target} exists")
            for item in lines[index : index + 4]:
                print(item)
            return
    print(f"{target} is absent")


def main() -> int:
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    show_target(lines, "debug-idmt-bass-high-register-sample")
    show_target(lines, "test-idmt-bass-single-track")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
