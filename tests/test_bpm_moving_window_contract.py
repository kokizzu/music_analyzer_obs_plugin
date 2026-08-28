#!/usr/bin/env python3
"""Guard the OBS BPM contract against stale tracker fallbacks."""

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYZER = (ROOT / "src" / "analyzer.cpp").read_text()
HEADER = (ROOT / "src" / "analyzer.hpp").read_text()


def require(pattern: str, text: str, message: str) -> None:
    if not re.search(pattern, text, re.DOTALL):
        raise AssertionError(message)


def main() -> int:
    require(
        r"estimate_three_second_source_bpm\(float interval_seconds\).*?"
        r"constexpr float kWindowSeconds = 3\.0f;",
        ANALYZER,
        "BPM estimator must use a three-second window",
    )
    require(
        r"const float immediate_source_bpm = estimate_three_second_source_bpm\(interval_seconds\);"
        r".*?snapshot\.estimated_bpm = immediate_source_bpm;",
        ANALYZER,
        "every analysis hop must publish the freshly computed source-window BPM",
    )
    for fallback in [
        "kEnablePermissiveBeatTrackerFallback",
        "kEnablePhaseBeatTrackerConsensus",
        "kEnableHighTempoBeatTrackerFallback",
    ]:
        require(
            rf"constexpr bool {fallback} = false;",
            HEADER,
            f"{fallback} must stay disabled so it cannot replace the moving-window BPM",
        )
    print("test_bpm_moving_window_contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
