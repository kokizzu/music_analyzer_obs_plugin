#!/usr/bin/env python3
"""Regression guard for legacy Fret Zealot whole-frame settling."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def require(contents: str, expected: str) -> None:
    if expected not in contents:
        raise AssertionError(f"missing required Fret Zealot frame-settle behavior: {expected}")


def main() -> int:
    contents = SOURCE.read_text(encoding="utf-8")
    require(contents, "LEGACY_FRAME_SETTLE_MILLIS")
    require(contents, "scheduleScaleFrameSettle(completed)")
    require(contents, "completeScaleFrame(completed, settleId)")
    require(contents, "handler.postDelayed(")

    finish_start = contents.index("    private void finishScaleFrame(ScaleFrame completed)")
    finish_end = contents.index("    private void scheduleScaleFrameSettle", finish_start)
    finish_body = contents[finish_start:finish_end]
    if "startScaleFrame(queued" in finish_body:
        raise AssertionError("queued scale frame must wait for physical frame settling")
    if "scheduleScaleFrameSettle(completed);" not in finish_body:
        raise AssertionError("completed legacy frame must enter a physical settle phase")

    complete_start = contents.index("    private void completeScaleFrame(ScaleFrame completed, int settleId)")
    complete_end = contents.index("    private void startScaleFrame", complete_start)
    complete_body = contents[complete_start:complete_end]
    require(complete_body, "committedScaleFrame = completed;")
    require(complete_body, "startScaleFrame(queued, false, reconcileWholeBoard);")
    print("check_fret_zealot_frame_settle: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"check_fret_zealot_frame_settle: {error}", file=sys.stderr)
        raise SystemExit(1)
