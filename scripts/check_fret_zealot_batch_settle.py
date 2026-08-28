#!/usr/bin/env python3
"""Guard legacy Fret Zealot batches against early SDK callback advancement."""

from pathlib import Path
import sys


SOURCE = Path("android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java")


def require(text: str, needle: str, message: str) -> bool:
    if needle in text:
        return True
    print(f"FAIL: {message}")
    return False


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    ok = True
    ok &= require(
            text,
            "private static final long LEGACY_BATCH_SETTLE_MILLIS = 750L;",
            "legacy batches must use the hardware-safe settle interval")
    ok &= text.count("finishScaleFrameBatch(completed, batchId), LEGACY_BATCH_SETTLE_MILLIS);") == 2
    if not ok:
        print("FAIL: callback and fallback paths must wait for the same settle interval")
    ok &= require(
            text,
            "private static final long LEGACY_FRAME_SETTLE_MILLIS = 300L;",
            "a completed logical frame must remain in flight through final LED settle")
    if "LEGACY_BATCH_FALLBACK_MILLIS" in text:
        print("FAIL: callback and fallback must not use different batch timings")
        ok = False
    if ok:
        print("Fret Zealot legacy batch pacing: passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
