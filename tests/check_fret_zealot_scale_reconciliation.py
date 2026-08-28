#!/usr/bin/env python3
"""Guard the non-blinking reconciliation path for legacy Fret Zealot LEDs."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    require("writeScaleFrameReconciliation" in source,
            "missing post-settle scale reconciliation")
    require("onScaleFrameFlushed" in source and "writeScaleFrameReconciliation(completed)" in source,
            "initial flush must schedule scale reconciliation")
    require("finishScaleFrame(completed)" in source,
            "reconciled frame must still commit through the normal completion path")
    require("if (!target.lit[string][fret])" in source,
            "reconciliation must preserve unlit cells without a board reset")
    require("sdk.set_all" in source and "needsInitialScaleReset" in source,
            "the full-board reset must remain connection-only")
    print("check_fret_zealot_scale_reconciliation: ok")


if __name__ == "__main__":
    main()
