#!/usr/bin/env python3
"""Guard the Android Fret Zealot AUTO-root recovery contract."""

from pathlib import Path
import sys


SOURCE = Path(__file__).resolve().parents[1] / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java"
REQUIRED = (
    "private byte[] fretZealotAutoRecoveryPacket;",
    "private final Runnable replayStableFretZealotPacket;",
    "scheduleFretZealotAutoRecovery(packet);",
    "fretZealot.sendPacket(packet, true);",
    "Arrays.equals(fretZealotAutoRecoveryPacket, lastFretZealotPacket)",
    "handler.removeCallbacks(replayStableFretZealotPacket);",
)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    missing = [fragment for fragment in REQUIRED if fragment not in source]
    if missing:
        for fragment in missing:
            print(f"missing Fret Zealot AUTO recovery guard: {fragment}")
        return 1
    print("fret-zealot-auto-recovery: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
