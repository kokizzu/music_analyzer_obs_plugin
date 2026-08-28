#!/usr/bin/env python3
"""Guard the first AUTO Fret Zealot scale against estimator-churn starvation."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / (
    "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    method_start = source.index("    private void scheduleStableFretZealotPacket")
    method_end = source.index("    private void retryFretZealotAutoReconciliation", method_start)
    method = source[method_start:method_end]

    preserve = "boolean preserveInitialDeadline = fretZealotAutoInitialScalePending && !initialScale;"
    preserve_block = """if (preserveInitialDeadline) {
            // The board was cleared at connect time and needs a complete scale
            // even if the AUTO estimator is still revising. Keep the original
            // deadline but replace its payload with the newest root; otherwise
            // a busy song can postpone the first visible scale indefinitely.
            return;
        }"""
    require(preserve in method, "initial AUTO deadline preservation is missing")
    require(preserve_block in method, "initial AUTO replacement must return before rescheduling")
    require(
        method.index(preserve_block) < method.index("pendingFretZealotPacketChangedAtMillis"),
        "initial AUTO replacement must keep the original stability timestamp",
    )
    require(
        method.index(preserve_block) < method.index("handler.removeCallbacks(sendStableFretZealotPacket)"),
        "initial AUTO replacement must keep the original scheduled callback",
    )
    print("test_fret_zealot_initial_auto_scale: ok")


if __name__ == "__main__":
    main()
