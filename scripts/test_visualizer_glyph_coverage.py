#!/usr/bin/env python3
"""Check that common source/device-label punctuation has real bitmap glyphs."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "visualizer_renderer.cpp"


REQUIRED_LABELS = (
    "Speakers (USB Audio)",
    "USB-C [Output]",
    "Audio_Device #1",
    "What U Hear / Stereo Mix",
    "MIDI & Bluetooth @ 100%",
    "Line-in {rear} = active",
    "C:\\Music\\Input",
)
REQUIRED_PUNCTUATION = set("()[],{}_,;&@=$*^`\\|<>'\"")


def case_characters(text: str) -> set[str]:
    characters = set(re.findall(r"\tcase '([^'\\])':", text))
    apostrophe_case = "\tcase '" + "\\" + "'':"
    backslash_case = "\tcase '" + "\\\\" + "':"
    if apostrophe_case in text:
        characters.add("'")
    if backslash_case in text:
        characters.add("\\")
    return characters


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    cases = case_characters(text)
    missing = sorted(REQUIRED_PUNCTUATION - cases)
    if missing:
        raise SystemExit("missing bitmap glyph cases: " + " ".join(repr(char) for char in missing))
    for label in REQUIRED_LABELS:
        unsupported = sorted({char for char in label if ord(char) < 128 and not char.isalnum() and char != " " and char not in cases})
        if unsupported:
            raise SystemExit(f"label {label!r} contains unsupported glyphs: {unsupported!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
