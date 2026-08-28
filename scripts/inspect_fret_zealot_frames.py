#!/usr/bin/env python3
"""Print ScaleFrame lifecycle code from the Android Fret Zealot controller."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path("android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java")
TERMS = (
    "startScaleFrame",
    "finishScaleFrame",
    "queuedScaleFrame",
    "writeScaleFrameDelta",
    "writeScaleFrameReconciliation",
    "activeScaleFrameRequires",
)


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if any(term in line for term in TERMS)]
    print(f"fret_zealot_frames source={SOURCE} matches={len(matches)}")
    emitted: set[int] = set()
    for index in matches:
        for line_index in range(max(0, index - 8), min(len(lines), index + 18)):
            if line_index in emitted:
                continue
            emitted.add(line_index)
            print(f"{line_index + 1}: {lines[line_index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
