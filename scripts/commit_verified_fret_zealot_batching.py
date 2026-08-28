#!/usr/bin/env python3
"""Commit only the verified Fret Zealot bounded-batching fix."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTROLLER = "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"
ANDROID_CHECK = "tests/check_android_project.py"


def run(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=ROOT, input=input_text, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result


def stage_android_check() -> None:
    base = run("git", "show", f"HEAD:{ANDROID_CHECK}").stdout
    current = (ROOT / ANDROID_CHECK).read_text(encoding="utf-8")
    old_first = '''    require("ScaleFrame" in fret_zealot_sdk_controller and
            "writeScaleFrameDelta" in fret_zealot_sdk_controller and
            "STRING_COUNT" in fret_zealot_sdk_controller and
            "FRET_COUNT" in fret_zealot_sdk_controller,
            "Fret Zealot root changes must calculate a non-blinking LED delta")
'''
    new_first = '''    require("ScaleFrame" in fret_zealot_sdk_controller and
            "flushNextScaleFrameBatch" in fret_zealot_sdk_controller and
            "LEGACY_SCALE_COMMANDS_PER_FLUSH = 12" in fret_zealot_sdk_controller and
            "STRING_COUNT" in fret_zealot_sdk_controller and
            "FRET_COUNT" in fret_zealot_sdk_controller and
            "queuedScaleFrameRequiresReconciliation" in fret_zealot_sdk_controller and
            "activeScaleFrameReconcilesWholeBoard" in fret_zealot_sdk_controller and
            "activeScaleFrameClearsNonTargets" in fret_zealot_sdk_controller,
            "Fret Zealot AUTO root changes must use bounded target and stale-clear batches")
'''
    old_second = '''    require("writeScaleFrameDelta" in fret_zealot_sdk_controller and
            "if (target.lit[string][fret]" in fret_zealot_sdk_controller and
            "if (current.lit[string][fret] && !target.lit[string][fret])" in fret_zealot_sdk_controller,
            "Fret Zealot must light new notes before turning obsolete notes off")
    require("writeScaleFrameReconciliation" in fret_zealot_sdk_controller and
            "Reassert every target pixel." in fret_zealot_sdk_controller,
            "A stable Fret Zealot AUTO root must replay every scale pixel")
    require("activeScaleFrameRequiresClearPass" in fret_zealot_sdk_controller and
            "writeScaleFrameNonTargetClear" in fret_zealot_sdk_controller and
            "The target LEDs are now all present." in fret_zealot_sdk_controller,
            "Fret Zealot AUTO scale replacement must clear obsolete LEDs only after target LEDs settle")
    require("activeScaleFrameRequiresTargetReassert" in fret_zealot_sdk_controller and
            "writeScaleFrameReconciliation(completed);" in fret_zealot_sdk_controller and
            "must not commit a partial new scale" in fret_zealot_sdk_controller,
            "Fret Zealot scale reconciliation must reassert target LEDs before stale clears")
    require("boolean boardReset = false;" in fret_zealot_sdk_controller and
            "activeScaleFrameRequiresClearPass = !boardReset;" in fret_zealot_sdk_controller,
            "Fret Zealot must skip stale-pixel clears after its session reset")
'''
    new_second = '''    require("activeScaleFramePhase == 0" in fret_zealot_sdk_controller and
            "boolean needsTarget" in fret_zealot_sdk_controller and
            "boolean needsClear" in fret_zealot_sdk_controller,
            "Fret Zealot must light new notes before turning obsolete notes off")
    require("sdk.set_all((byte) 0, (byte) 0, (byte) 0" in fret_zealot_sdk_controller and
            "commands < LEGACY_SCALE_COMMANDS_PER_FLUSH" in fret_zealot_sdk_controller and
            "sdk.sendCommandFlush(() -> onScaleFrameFlushed(target))" in fret_zealot_sdk_controller,
            "Fret Zealot AUTO root changes must pace every target and stale-clear batch")
'''
    if base.count(old_first) != 1 or base.count(old_second) != 1:
        raise RuntimeError("HEAD Android guard layout changed; refusing to stage a broad test diff")
    staged = base.replace(old_first, new_first).replace(old_second, new_second)
    if new_first not in current or new_second not in current:
        raise RuntimeError("working Android guard does not contain the verified bounded-batch assertions")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as before_file:
        before_file.write(base)
        before = Path(before_file.name)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as after_file:
        after_file.write(staged)
        after = Path(after_file.name)
    try:
        diff = run("git", "diff", "--no-index", str(before), str(after), check=False)
        if diff.returncode not in (0, 1) or not diff.stdout:
            raise RuntimeError(diff.stderr or "unable to construct Android guard staging patch")
        patch = diff.stdout.replace(f"a{before}", f"a/{ANDROID_CHECK}")
        patch = patch.replace(f"b{after}", f"b/{ANDROID_CHECK}")
        run("git", "apply", "--cached", input_text=patch)
    finally:
        before.unlink(missing_ok=True)
        after.unlink(missing_ok=True)


def main() -> int:
    staged_before = run("git", "diff", "--cached", "--name-only").stdout.splitlines()
    if staged_before not in ([], [CONTROLLER]):
        raise RuntimeError("index contains unrelated staged work; refusing to mix this fix")
    if not staged_before:
        run("git", "add", "--", CONTROLLER)
    stage_android_check()
    staged = run("git", "diff", "--cached", "--name-only").stdout.splitlines()
    expected = {CONTROLLER, ANDROID_CHECK}
    if set(staged) != expected:
        raise RuntimeError(f"unexpected staged paths: {staged}")
    run("git", "commit", "-m", "Pace Fret Zealot auto-root LED updates")
    print("committed Fret Zealot bounded batching")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
