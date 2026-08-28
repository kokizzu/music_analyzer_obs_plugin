#!/usr/bin/env python3
"""Print the NSynth fixture importer for audit while adjusting its transfer safety."""

from pathlib import Path


SOURCE = Path(__file__).resolve().with_name("prepare_nsynth_acoustic_bass_fixture.py")


def main() -> None:
    for number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        print(f"{number:4}: {line}")


if __name__ == "__main__":
    main()
