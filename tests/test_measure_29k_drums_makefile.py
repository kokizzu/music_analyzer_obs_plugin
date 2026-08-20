#!/usr/bin/env python3
"""Keep the independent 29k primary-label audit reproducible."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAKEFILE = (ROOT / "Makefile").read_text(encoding="utf-8")


def require(needle: str) -> None:
    if needle not in MAKEFILE:
        raise AssertionError(f"expected `{needle}` in Makefile")


def main() -> int:
    require("SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS ?=")
    require("MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1")
    require("analyze-29k-drums-primary-attribute-rows: measure-29k-drums")
    require("find-29k-drum-primary-attribute-patterns: $(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)")
    require("find-cached-protected-drum-primary-attribute-patterns: scripts/find_drum_attribute_patterns.py")
    require("CACHED_PROTECTED_DRUM_PRIMARY_PATTERN_REPORT ?=")
    require("scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows")
    require("$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)")
    require("DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS ?=")
    print("test_measure_29k_drums_makefile: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
