#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def target_recipe(makefile: str, target: str) -> str:
    match = re.search(rf"^{re.escape(target)}:.*(?:\n\t.*)+", makefile, re.MULTILINE)
    assert match is not None, f"missing {target} target"
    return match.group(0)


def main() -> int:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    recipe = target_recipe(makefile, "measure-analyzer-patterns")
    expected = [
        "scripts/report_analyzer_attribute_patterns.py",
        "$(MAKE) find-instrument-owner-patterns",
        "$(MAKE) find-real-note-attribute-patterns",
        "$(MAKE) find-guitar-chord-mix-attribute-patterns",
        "$(MAKE) find-drum-attribute-patterns",
        "$(MEASURE_INSTRUMENT_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_PATTERN_ARGS)",
        "$(MEASURE_GUITAR_PATTERN_ARGS)",
        "$(MEASURE_DRUM_PATTERN_ARGS)",
    ]
    for text in expected:
        assert text in recipe, f"measure-analyzer-patterns does not include {text}"

    for variable in [
        "MEASURE_INSTRUMENT_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_PATTERN_ARGS",
        "MEASURE_GUITAR_PATTERN_ARGS",
        "MEASURE_DRUM_PATTERN_ARGS",
    ]:
        assert f"{variable} ?=" in makefile, f"missing overridable {variable}"

    print("test_measure_analyzer_patterns_makefile: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
