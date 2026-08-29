#!/usr/bin/env python3
"""Print the existing bass attribute report implementation for reuse audits."""

from pathlib import Path


SOURCE = Path(__file__).with_name("report_full_mix_bass_attributes.py")


def main() -> None:
    print(SOURCE.read_text(), end="")


if __name__ == "__main__":
    main()
