#!/usr/bin/env python3
"""Report whether large optional audio fixtures are kept outside the repository."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = (
    "build/InstrumentSamples",
    "build/DrumSamples",
    "build/drum_samples_spread",
    "build/real_note_samples",
    "build/external_prepared_multitrack",
)


def main() -> None:
    for relative in FIXTURES:
        path = ROOT / relative
        if not path.exists() and not path.is_symlink():
            print(f"{relative}: absent")
            continue
        if not path.is_symlink():
            print(f"{relative}: local")
            continue
        print(f"{relative}: symlink -> {path.resolve()}")


if __name__ == "__main__":
    main()
