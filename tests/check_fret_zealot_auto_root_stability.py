#!/usr/bin/env python3
"""Guard AUTO-root debounce across an in-flight Fret Zealot LED frame."""

from pathlib import Path


SOURCE = Path("android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java")
TEXT = SOURCE.read_text(encoding="utf-8")


def require(needle: str, message: str) -> None:
    if needle not in TEXT:
        raise AssertionError(message + ": " + needle)


require("private long pendingFretZealotPacketChangedAtMillis;",
        "AUTO root must retain the time of its newest packet")
require("private void scheduleStableFretZealotPacket(byte[] packet, boolean initialScale)",
        "AUTO root packets must share one resettable scheduler")
require("pendingFretZealotPacketChangedAtMillis = SystemClock.uptimeMillis();",
        "A changed AUTO root must restart its stability window")
require("long remainingMillis = FRET_ZEALOT_AUTO_ROOT_STABLE_MILLIS",
        "Idle transport must still respect the newest root's debounce")
require("if (remainingMillis > 0) {",
        "A recently changed root must not be sent immediately after frame drain")
require("scheduleStableFretZealotPacketAfter(remainingMillis);",
        "The pending root must be retried after its remaining quiet period")
require("scheduleStableFretZealotPacket(packet, true);",
        "Initial AUTO scales must use the resettable scheduler")
require("scheduleStableFretZealotPacket(packet, false);",
        "Subsequent AUTO root changes must use the resettable scheduler")

print("check_fret_zealot_auto_root_stability: ok")
