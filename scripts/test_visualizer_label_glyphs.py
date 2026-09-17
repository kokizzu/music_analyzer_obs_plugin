#!/usr/bin/env python3
"""Check that every character used by visible labels has a renderer glyph."""

from pathlib import Path
import re
import string
import sys


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "src" / "visualizer_renderer.cpp"


LABEL_CORPUS = (
    "MUSIC ANALYZER",
    "MUSIC ANALYZER FILTER",
    "MIC/AUX",
    "SPEAKER LOOPBACK",
    "1/3 SPEAKER MONITOR",
    "NO AUDIBLE INPUT 12.34",
    "RMS 0.02 LOW 85% MID 8% HIGH 7% AGE 0.55 DROP 0",
    "BASS DRUM SNARE HIHAT CRASH TOMS RIDE RIM",
    "BASS GUITAR KEYS VOCAL OTHERS ROOT SUSTAIN CHORD NOTES BPM",
    "C C# D D# E F F# G G# A A# B",
    "C7 Cm Cdim Caug Csus2 Dsus4 F#7",
    "1 1# 2 2# 3 4 4# 5 5# 6",
    "FRET-ZEALOT LITEJAM MPC/APC",
    "(INPUT) [OUTPUT] {AUTO} _ = + - * & @ $ ^ ` \\ | < > , ; : ' \" ? !",
)


def case_pattern(character: str) -> re.Pattern[str]:
    escaped = {
        "\\": r"\\",
        "'": r"\'",
    }.get(character, character)
    return re.compile(r"\bcase\s+'" + re.escape(escaped) + r"'\s*:")


def main() -> int:
    try:
        source = RENDERER.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"visualizer label glyphs: cannot read {RENDERER}: {exc}", file=sys.stderr)
        return 1

    required = set("".join(LABEL_CORPUS))
    required.update(string.digits)
    required.update(string.ascii_uppercase)
    required.update(string.punctuation)
    lower_case_labels = sorted(character for character in required if character.islower())
    has_case_normalization = bool(
        re.search(r"std::toupper|\btoupper\b|uppercase|lowercase_ascii", source)
        or ("'a'" in source and "'z'" in source and "'A'" in source)
    )
    if lower_case_labels and not has_case_normalization:
        printable = ", ".join(repr(character) for character in lower_case_labels)
        print(
            "visualizer label glyphs: lowercase labels have no visible case-normalization path: "
            + printable,
            file=sys.stderr,
        )
        return 1

    missing = sorted(
        character
        for character in required
        if not case_pattern(character).search(source)
        and not (
            character.islower()
            and has_case_normalization
            and case_pattern(character.upper()).search(source)
        )
    )
    if missing:
        printable = ", ".join(repr(character) for character in missing)
        print(f"visualizer label glyphs: missing explicit glyph cases: {printable}", file=sys.stderr)
        return 1

    corpus_count = len(set("".join(LABEL_CORPUS)))
    print(
        "visualizer label glyphs: ok "
        f"({corpus_count} label characters, {len(required)} total checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
