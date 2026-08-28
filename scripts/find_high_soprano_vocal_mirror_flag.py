#!/usr/bin/env python3
"""Locate the compile-time control for the measured soprano vocal mirror."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEEDLE = "kEnableMeasuredHighSopranoVocalMirror"


def main() -> None:
    for path in sorted((ROOT / "src").glob("*")):
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if NEEDLE in line:
                print(f"{path.relative_to(ROOT)}:{number}: {line}")


if __name__ == "__main__":
    main()
