#!/usr/bin/env python3
"""Summarize analyzer_real_note_samples verbose miss logs."""

from __future__ import annotations

import collections
import pathlib
import re
import sys


NOTE_TO_PC = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}
PC_TO_NOTE = {value: key for key, value in NOTE_TO_PC.items()}

FAIL_RE = re.compile(
    r"^(?P<sample>\S+) (?P<family>[^/\s]+)/(?P<source>\S+) "
    r"(?P<expected>[A-G]#?\d): expected detected note"
)
BUFFER_RE = re.compile(r"^\s+buffer (?P<buffer>\d+) expected=(?P<expected>[A-G]#?\d) .*")
NOTE_LEVEL_RE = re.compile(r"(?P<note>[A-G]#?\d):(?P<level>[0-9.]+)")


def split_note(note: str) -> tuple[str, int]:
    if len(note) >= 2 and note[1] == "#":
        name = note[:2]
        octave = int(note[2:])
    else:
        name = note[:1]
        octave = int(note[1:])
    return name, octave


def note_number(note: str) -> int:
    name, octave = split_note(note)
    return (octave + 1) * 12 + NOTE_TO_PC[name]


def pitch_name(note: str) -> str:
    return split_note(note)[0]


def closest_pitch_offset(expected: str, detected: str) -> int:
    raw = note_number(detected) - note_number(expected)
    while raw > 6:
        raw -= 12
    while raw < -6:
        raw += 12
    return raw


def analyze(path: pathlib.Path) -> list[str]:
    failures = []
    pending_buffers = []
    for line in path.read_text(errors="replace").splitlines():
        buffer_match = BUFFER_RE.match(line)
        if buffer_match:
            detected_notes = [
                (match.group("note"), float(match.group("level")))
                for match in NOTE_LEVEL_RE.finditer(line)
            ]
            pending_buffers.append((buffer_match.group("expected"), detected_notes))
            continue

        fail_match = FAIL_RE.match(line)
        if not fail_match:
            continue
        failures.append((fail_match.groupdict(), pending_buffers))
        pending_buffers = []

    by_source: collections.Counter[str] = collections.Counter()
    expected_pitch: collections.Counter[str] = collections.Counter()
    strongest_pairs: collections.Counter[tuple[str, str]] = collections.Counter()
    closest_offsets: collections.Counter[int] = collections.Counter()
    missing_all_notes = 0
    expected_present_in_debug = 0

    for failure, buffers in failures:
        source = f"{failure['family']}/{failure['source']}"
        expected = failure["expected"]
        by_source[source] += 1
        expected_pitch[pitch_name(expected)] += 1

        strongest_note = ""
        strongest_level = 0.0
        expected_seen = False
        for _buffer_expected, detected_notes in buffers:
            for detected, level in detected_notes:
                if pitch_name(detected) == pitch_name(expected):
                    expected_seen = True
                if level > strongest_level:
                    strongest_level = level
                    strongest_note = detected
        if expected_seen:
            expected_present_in_debug += 1
        if strongest_note:
            strongest_pairs[(expected, strongest_note)] += 1
            closest_offsets[closest_pitch_offset(expected, strongest_note)] += 1
        else:
            missing_all_notes += 1

    lines = [f"analyze_real_note_misses: misses {len(failures)}"]
    if failures:
        lines.append("by source " + " ".join(f"{key}={value}" for key, value in by_source.most_common(12)))
        lines.append(
            "by expected pitch "
            + " ".join(f"{key}={value}" for key, value in sorted(expected_pitch.items()))
        )
        lines.append(
            "strongest detected "
            + " ".join(f"{expected}->{detected}={count}" for (expected, detected), count in strongest_pairs.most_common(12))
        )
        lines.append(
            "closest pitch offsets "
            + " ".join(f"{offset:+d}={count}" for offset, count in sorted(closest_offsets.items()))
        )
        lines.append(f"expected present in verbose grids {expected_present_in_debug}/{len(failures)}")
        if missing_all_notes:
            lines.append(f"no detected note levels {missing_all_notes}")
    return lines


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/real_note_full_mix_verbose.err")
    for line in analyze(path):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
