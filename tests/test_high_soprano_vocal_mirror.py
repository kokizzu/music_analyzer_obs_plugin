#!/usr/bin/env python3
"""Guard the measured high-soprano full-mix vocal display recovery."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "src" / "analyzer.hpp").read_text(encoding="utf-8")
SOURCE = (ROOT / "src" / "analyzer.cpp").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"test_high_soprano_vocal_mirror: {message}")


def main() -> int:
    require("kEnableMeasuredHighSopranoVocalMirror = true" in HEADER,
            "measured high-soprano mirror must stay enabled")
    require("debug.owner == InstrumentKind::Keyboard && debug.midi >= 77 && debug.midi <= 78" in SOURCE,
            "mirror must remain restricted to keyboard-owned F5/F#5 candidates")
    require("debug.adjacent_upper_ratio >= 0.032f && debug.local_noise_level >= 0.122f" in SOURCE and
            "debug.pitch_confidence <= 0.814f" in SOURCE,
            "mirror must retain its measured cross-choir profile")
    require("ownership.vocal[note_index] = true" in SOURCE and
            "ownership.vocal_candidates.push_back" in SOURCE,
            "qualified candidates must be displayed in the vocal row")
    require("if constexpr (kEnableMeasuredHighSopranoVocalMirror)" in SOURCE and
            "mirror_measured_high_soprano_vocal_candidates(ownership);" in SOURCE,
            "enabled switch must invoke the bounded mirror")
    print("test_high_soprano_vocal_mirror: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
