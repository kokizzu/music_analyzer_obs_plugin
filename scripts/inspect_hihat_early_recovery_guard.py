#!/usr/bin/env python3
"""Print the temporal hi-hat guard with stable line numbers for repair review."""

from pathlib import Path


def main() -> None:
    path = Path("tests/check_hihat_early_recovery_guard.py")
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{line_number:4d}: {line}")


if __name__ == "__main__":
    main()
