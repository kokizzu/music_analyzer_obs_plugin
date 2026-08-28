#!/usr/bin/env python3
"""Stage only the Fret Zealot final-frame settle regression fix."""

from __future__ import annotations

import argparse
import difflib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def staged_content(indexed: str) -> str:
    required = (
        "    private static final int LEGACY_SCALE_COMMANDS_PER_FLUSH = 12;\n",
        "    private int activeScaleFrameBatchId;\n",
        "        ++activeScaleFrameBatchId;\n",
        "        committedScaleFrame = completed;\n        activeScaleFrame = null;\n",
    )
    for marker in required:
        if marker not in indexed:
            raise RuntimeError(f"indexed controller no longer has expected marker: {marker!r}")

    result = indexed.replace(
        required[0],
        required[0]
        + "    // Preserve a complete physical legacy frame before an AUTO-root replacement.\n"
        + "    private static final long LEGACY_FRAME_SETTLE_MILLIS = 300L;\n",
        1,
    )
    result = result.replace(
        required[1], required[1] + "    private int activeScaleFrameSettleId;\n", 1
    )
    result = result.replace(
        required[2], required[2] + "        ++activeScaleFrameSettleId;\n", 1
    )
    completion = (
        "        scheduleScaleFrameSettle(completed);\n"
        "    }\n\n"
        "    private void scheduleScaleFrameSettle(ScaleFrame completed) {\n"
        "        int settleId = ++activeScaleFrameSettleId;\n"
        "        handler.postDelayed(\n"
        "                () -> completeScaleFrame(completed, settleId), LEGACY_FRAME_SETTLE_MILLIS);\n"
        "    }\n\n"
        "    private void completeScaleFrame(ScaleFrame completed, int settleId) {\n"
        "        if (!active || closing || activeScaleFrame != completed\n"
        "                || settleId != activeScaleFrameSettleId) {\n"
        "            return;\n"
        "        }\n"
    )
    return result.replace(required[3], completion + required[3], 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()
    indexed = subprocess.run(
        ["git", "show", f":{PATH}"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    candidate = staged_content(indexed)
    if args.mode == "plan":
        print("".join(difflib.unified_diff(
            indexed.splitlines(keepends=True),
            candidate.splitlines(keepends=True),
            fromfile=f"a/{PATH}", tofile=f"b/{PATH}", n=3,
        )), end="")
        return 0

    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=ROOT,
        check=True,
        input=candidate,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{PATH}"],
        cwd=ROOT,
        check=True,
    )
    print(f"staged only Fret Zealot final-frame settle fix: {PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
