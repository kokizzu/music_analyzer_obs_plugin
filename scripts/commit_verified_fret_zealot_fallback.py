#!/usr/bin/env python3
"""Stage and commit only the verified Fret Zealot callback-fallback fix."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MESSAGE = "Recover stalled Fret Zealot LED batches"


def git(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=check,
    )


def replace_once(text: str, old: str, new: str, path: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"expected one matching block in {path}")
    return text.replace(old, new)


def desired_files() -> dict[str, str]:
    controller_path = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"
    controller = git("show", f"HEAD:{controller_path}").stdout
    controller = replace_once(
        controller,
        "    private static final long LEGACY_FRAME_SETTLE_MILLIS = 250L;\n",
        "    private static final long LEGACY_FRAME_SETTLE_MILLIS = 250L;\n"
        "    // Some first-generation boards apply the packet but never deliver the\n"
        "    // corresponding SDK callback. This fallback must be slower than the normal\n"
        "    // callback path, and is guarded so it cannot advance a later batch twice.\n"
        "    private static final long LEGACY_BATCH_FALLBACK_MILLIS = 750L;\n",
        controller_path,
    )
    controller = replace_once(
        controller,
        "    private int activeScaleFrameCursor;\n",
        "    private int activeScaleFrameCursor;\n"
        "    private int activeScaleFrameBatchId;\n",
        controller_path,
    )
    controller = replace_once(
        controller,
        "        activeScaleFrameCursor = 0;\n"
        "    }\n\n"
        "    private void onScaleFrameFlushed(ScaleFrame completed) {\n"
        "        handler.postDelayed(() -> finishScaleFrame(completed), LEGACY_FRAME_SETTLE_MILLIS);\n"
        "    }\n",
        "        activeScaleFrameCursor = 0;\n"
        "        ++activeScaleFrameBatchId;\n"
        "    }\n\n"
        "    private void onScaleFrameFlushed(ScaleFrame completed, int batchId) {\n"
        "        handler.postDelayed(\n"
        "                () -> finishScaleFrameBatch(completed, batchId), LEGACY_FRAME_SETTLE_MILLIS);\n"
        "    }\n\n"
        "    private void scheduleScaleFrameBatchFallback(ScaleFrame completed, int batchId) {\n"
        "        handler.postDelayed(\n"
        "                () -> finishScaleFrameBatch(completed, batchId), LEGACY_BATCH_FALLBACK_MILLIS);\n"
        "    }\n\n"
        "    private void finishScaleFrameBatch(ScaleFrame completed, int batchId) {\n"
        "        if (!active || closing || activeScaleFrame != completed || batchId != activeScaleFrameBatchId) {\n"
        "            return;\n"
        "        }\n"
        "        // Invalidate both the callback and fallback for this batch before a\n"
        "        // subsequent batch can be submitted.\n"
        "        ++activeScaleFrameBatchId;\n"
        "        finishScaleFrame(completed);\n"
        "    }\n",
        controller_path,
    )
    controller = replace_once(
        controller,
        "            sdk.sendCommandFlush(() -> onScaleFrameFlushed(target));\n"
        "            return;\n",
        "            int batchId = ++activeScaleFrameBatchId;\n"
        "            sdk.sendCommandFlush(() -> onScaleFrameFlushed(target, batchId));\n"
        "            scheduleScaleFrameBatchFallback(target, batchId);\n"
        "            return;\n",
        controller_path,
    )
    controller = replace_once(
        controller,
        "            if (commands > 0) {\n"
        "                sdk.sendCommandFlush(() -> onScaleFrameFlushed(target));\n"
        "                return true;\n",
        "            if (commands > 0) {\n"
        "                int batchId = ++activeScaleFrameBatchId;\n"
        "                sdk.sendCommandFlush(() -> onScaleFrameFlushed(target, batchId));\n"
        "                scheduleScaleFrameBatchFallback(target, batchId);\n"
        "                return true;\n",
        controller_path,
    )

    android_check_path = "tests/check_android_project.py"
    android_check = git("show", f"HEAD:{android_check_path}").stdout
    android_check = replace_once(
        android_check,
        "    require(\"LEGACY_FRAME_SETTLE_MILLIS = 250L\" in fret_zealot_sdk_controller and\n"
        "            \"handler.postDelayed(() -> finishScaleFrame(completed)\" in fret_zealot_sdk_controller and\n"
        "            \"activeScaleFrame != completed\" in fret_zealot_sdk_controller,\n",
        "    require(\"LEGACY_FRAME_SETTLE_MILLIS = 250L\" in fret_zealot_sdk_controller and\n"
        "            \"finishScaleFrameBatch(completed, batchId)\" in fret_zealot_sdk_controller and\n"
        "            \"batchId != activeScaleFrameBatchId\" in fret_zealot_sdk_controller and\n"
        "            \"activeScaleFrame != completed\" in fret_zealot_sdk_controller,\n",
        android_check_path,
    )
    android_check = replace_once(
        android_check,
        "    require(\"sdk.set_all((byte) 0, (byte) 0, (byte) 0\" in fret_zealot_sdk_controller and\n"
        "            \"commands < LEGACY_SCALE_COMMANDS_PER_FLUSH\" in fret_zealot_sdk_controller and\n"
        "            \"sdk.sendCommandFlush(() -> onScaleFrameFlushed(target))\" in fret_zealot_sdk_controller,\n",
        "    require(\"sdk.set_all((byte) 0, (byte) 0, (byte) 0\" in fret_zealot_sdk_controller and\n"
        "            \"commands < LEGACY_SCALE_COMMANDS_PER_FLUSH\" in fret_zealot_sdk_controller and\n"
        "            \"sdk.sendCommandFlush(() -> onScaleFrameFlushed(target, batchId))\" in fret_zealot_sdk_controller and\n"
        "            \"scheduleScaleFrameBatchFallback(target, batchId)\" in fret_zealot_sdk_controller,\n",
        android_check_path,
    )
    return {
        controller_path: controller,
        android_check_path: android_check,
    }


def make_patch(path: str, desired: str, temporary_directory: Path) -> str:
    base = git("show", f"HEAD:{path}").stdout
    temporary_directory.mkdir(parents=True, exist_ok=True)
    before = temporary_directory / "before"
    after = temporary_directory / "after"
    before.write_text(base, encoding="utf-8")
    after.write_text(desired, encoding="utf-8")
    result = subprocess.run(
        ["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/", str(before), str(after)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip())
    patch = result.stdout
    patch = patch.replace(f"a/{str(before).lstrip('/')}", f"a/{path}")
    patch = patch.replace(f"b/{str(after).lstrip('/')}", f"b/{path}")
    return patch


def main() -> int:
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        print("refusing to alter a non-empty index", file=sys.stderr)
        return 1
    desired = desired_files()
    with tempfile.TemporaryDirectory(prefix="fz-fallback-stage-") as directory:
        temporary_directory = Path(directory)
        patches = [make_patch(path, content, temporary_directory / str(index))
                   for index, (path, content) in enumerate(desired.items())]
    patch = "".join(patches)
    result = git("apply", "--cached", "--whitespace=nowarn", input_text=patch, check=False)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    git("diff", "--cached", "--check")
    result = git("commit", "-m", MESSAGE, check=False)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
