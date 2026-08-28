#!/usr/bin/env python3
"""Print the Fret Zealot controller and matching verification sources."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    Path("android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"),
    Path("scripts/measure_fret_zealot_update.sh"),
    Path("scripts/verify_fret_zealot_update.sh"),
)


def main() -> int:
    found = False
    for relative in PATHS:
        path = ROOT / relative
        if not path.is_file():
            continue
        found = True
        print(f"### {relative}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            print(f"{number:4}: {line}")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
