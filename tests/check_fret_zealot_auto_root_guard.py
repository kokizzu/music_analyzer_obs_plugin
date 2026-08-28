#!/usr/bin/env python3
"""Prevent AUTO-root changes from regressing to partial Fret Zealot deltas."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANAGER = (ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java").read_text()
CONTROLLER = (ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java").read_text()


def require(source: str, needle: str) -> None:
    if needle not in source:
        raise AssertionError(f"missing required Fret Zealot AUTO-root guard: {needle}")


def forbid(source: str, needle: str) -> None:
    if needle in source:
        raise AssertionError(f"obsolete oversized Fret Zealot reconciliation remains: {needle}")


def main() -> int:
    require(MANAGER, "FRET_ZEALOT_AUTO_ROOT_STABLE_MILLIS = 1250")
    require(MANAGER, "pendingFretZealotPacket")
    require(MANAGER, "handler.postDelayed(sendStableFretZealotPacket, FRET_ZEALOT_AUTO_ROOT_STABLE_MILLIS)")
    require(MANAGER, "fretZealot.sendPacket(packet, true)")
    require(MANAGER, "fretZealot.sendPacket(packet, false)")
    require(CONTROLLER, "void sendPacket(byte[] packet, boolean reconcileWholeBoard)")
    require(CONTROLLER, "LEGACY_SCALE_COMMANDS_PER_FLUSH = 12")
    require(CONTROLLER, "flushNextScaleFrameBatch")
    require(CONTROLLER, "commands < LEGACY_SCALE_COMMANDS_PER_FLUSH")
    require(CONTROLLER, "LEGACY_BATCH_SETTLE_MILLIS = 750L")
    require(CONTROLLER, "scheduleScaleFrameBatchFallback(target, batchId)")
    require(CONTROLLER, "batchId != activeScaleFrameBatchId")
    require(CONTROLLER, "activeScaleFrameReconcilesWholeBoard")
    require(CONTROLLER, "activeScaleFrameClearsNonTargets")
    require(CONTROLLER, "activeScaleFramePhase == 0")
    require(CONTROLLER, "boolean needsClear")
    forbid(CONTROLLER, "activeScaleFrameRequiresTargetReassert")
    forbid(CONTROLLER, "writeScaleFrameReconciliation")
    print("fret_zealot_auto_root_guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
