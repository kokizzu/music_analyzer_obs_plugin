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
OWNERSHIP_RE = re.compile(
    r"^(?P<sample>\S+) (?P<family>[^/\s]+)/(?P<source>\S+) "
    r"(?P<expected>[A-G]#?\d): expected-row ownership missing first-row=(?P<row>\S+)"
)
BUFFER_RE = re.compile(r"^\s+buffer (?P<buffer>\d+) expected=(?P<expected>[A-G]#?\d) .*")
NOTE_LEVEL_RE = re.compile(r"(?P<note>[A-G]#?\d):(?P<level>[0-9.]+)")
ROW_GRID_RE = re.compile(r"\b(?P<row>bass|keys|guitar|vocal|other)=[^\[]*\[(?P<grid>[^\]]*)\]")
AMB_RE = re.compile(r"\bamb=(?P<grid>.*?)\s+bass=")
ROW_NAME = {
    "amb": "amb",
    "bass": "bass",
    "keys": "piano",
    "guitar": "guitar",
    "vocal": "vocals",
    "other": "other",
}
ROW_ORDER = {
    "bass": 0,
    "piano": 1,
    "guitar": 2,
    "vocals": 3,
    "other": 4,
    "amb": 5,
}


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


def expected_pitch_rows(expected: str, row_notes: dict[str, list[tuple[str, float]]]) -> list[str]:
    expected_pitch = pitch_name(expected)
    rows = []
    for row, notes in row_notes.items():
        level = max((level for detected, level in notes if pitch_name(detected) == expected_pitch), default=0.0)
        if level > 0.0:
            rows.append((row, level))
    rows.sort(key=lambda item: (-item[1], ROW_ORDER.get(item[0], 99), item[0]))
    return [row for row, _level in rows]


def collapsed_row_path(expected: str, buffers) -> tuple[str, ...]:
    path = []
    for _buffer_expected, _detected_notes, row_notes in buffers:
        rows = expected_pitch_rows(expected, row_notes)
        if not rows:
            continue
        token = "+".join(rows)
        if not path or path[-1] != token:
            path.append(token)
    return tuple(path)


def format_row_path(path: tuple[str, ...]) -> str:
    return ">".join(path) if path else "none"


def parse_records(paths: list[pathlib.Path]):
    example_limit = 3
    failures = []
    ownership = []
    for path in paths:
        pending_buffers = []
        for line in path.read_text(errors="replace").splitlines():
            buffer_match = BUFFER_RE.match(line)
            if buffer_match:
                detected_notes = [
                    (match.group("note"), float(match.group("level")))
                    for match in NOTE_LEVEL_RE.finditer(line)
                ]
                row_notes: dict[str, list[tuple[str, float]]] = collections.defaultdict(list)
                amb_match = AMB_RE.search(line)
                if amb_match:
                    row_notes["amb"].extend(
                        (match.group("note"), float(match.group("level")))
                        for match in NOTE_LEVEL_RE.finditer(amb_match.group("grid"))
                    )
                for row_match in ROW_GRID_RE.finditer(line):
                    row = ROW_NAME[row_match.group("row")]
                    row_notes[row].extend(
                        (match.group("note"), float(match.group("level")))
                        for match in NOTE_LEVEL_RE.finditer(row_match.group("grid"))
                    )
                pending_buffers.append((buffer_match.group("expected"), detected_notes, row_notes))
                continue

            fail_match = FAIL_RE.match(line)
            if not fail_match:
                ownership_match = OWNERSHIP_RE.match(line)
                if not ownership_match:
                    continue
                ownership.append((ownership_match.groupdict(), pending_buffers))
                pending_buffers = []
                continue
            failures.append((fail_match.groupdict(), pending_buffers))
            pending_buffers = []

    return failures, ownership, example_limit


def analyze_paths(paths: list[pathlib.Path]) -> list[str]:
    failures, ownership, example_limit = parse_records(paths)

    def summarize_records(records):
        by_source: collections.Counter[str] = collections.Counter()
        expected_pitch: collections.Counter[str] = collections.Counter()
        strongest_pairs: collections.Counter[tuple[str, str]] = collections.Counter()
        closest_offsets: collections.Counter[int] = collections.Counter()
        first_rows: collections.Counter[str] = collections.Counter()
        source_rows: collections.Counter[tuple[str, str]] = collections.Counter()
        expected_debug_rows: collections.Counter[str] = collections.Counter()
        expected_source_debug_rows: collections.Counter[tuple[str, str]] = collections.Counter()
        expected_row_paths: collections.Counter[tuple[str, ...]] = collections.Counter()
        expected_source_row_paths: collections.Counter[tuple[str, tuple[str, ...]]] = collections.Counter()
        source_examples: dict[str, list[str]] = collections.defaultdict(list)
        source_row_examples: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
        missing_all_notes = 0
        expected_present_in_debug = 0

        for record, buffers in records:
            source = f"{record['family']}/{record['source']}"
            expected = record["expected"]
            example = f"{record['sample']} {expected}"
            by_source[source] += 1
            expected_pitch[pitch_name(expected)] += 1
            if len(source_examples[source]) < example_limit:
                source_examples[source].append(example)
            if "row" in record:
                first_rows[record["row"]] += 1
                source_rows[(source, record["row"])] += 1
                key = (source, record["row"])
                if len(source_row_examples[key]) < example_limit:
                    source_row_examples[key].append(example)

            strongest_note = ""
            strongest_level = 0.0
            expected_seen = False
            expected_seen_rows = set()
            for _buffer_expected, detected_notes, row_notes in buffers:
                for detected, level in detected_notes:
                    if pitch_name(detected) == pitch_name(expected):
                        expected_seen = True
                    if level > strongest_level:
                        strongest_level = level
                        strongest_note = detected
                for row, notes in row_notes.items():
                    if any(pitch_name(detected) == pitch_name(expected) for detected, _level in notes):
                        expected_seen_rows.add(row)
            row_path = collapsed_row_path(expected, buffers)
            if row_path:
                expected_row_paths[row_path] += 1
                expected_source_row_paths[(source, row_path)] += 1
            if expected_seen:
                expected_present_in_debug += 1
            for row in sorted(expected_seen_rows):
                expected_debug_rows[row] += 1
                expected_source_debug_rows[(source, row)] += 1
            if strongest_note:
                strongest_pairs[(expected, strongest_note)] += 1
                closest_offsets[closest_pitch_offset(expected, strongest_note)] += 1
            else:
                missing_all_notes += 1
        return {
            "by_source": by_source,
            "expected_pitch": expected_pitch,
            "strongest_pairs": strongest_pairs,
            "closest_offsets": closest_offsets,
            "first_rows": first_rows,
            "source_rows": source_rows,
            "expected_debug_rows": expected_debug_rows,
            "expected_source_debug_rows": expected_source_debug_rows,
            "expected_row_paths": expected_row_paths,
            "expected_source_row_paths": expected_source_row_paths,
            "source_examples": source_examples,
            "source_row_examples": source_row_examples,
            "missing_all_notes": missing_all_notes,
            "expected_present_in_debug": expected_present_in_debug,
        }

    lines = [f"analyze_real_note_misses: misses {len(failures)}"]
    if failures:
        summary = summarize_records(failures)
        by_source = summary["by_source"]
        expected_pitch = summary["expected_pitch"]
        strongest_pairs = summary["strongest_pairs"]
        closest_offsets = summary["closest_offsets"]
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
        lines.append(
            f"expected present in verbose grids {summary['expected_present_in_debug']}/{len(failures)}"
        )
        example_parts = []
        for source, _count in by_source.most_common(6):
            examples = summary["source_examples"].get(source, [])
            if examples:
                example_parts.append(f"{source}: " + ", ".join(examples))
        if example_parts:
            lines.append("examples " + " | ".join(example_parts))
        if summary["missing_all_notes"]:
            lines.append(f"no detected note levels {summary['missing_all_notes']}")
    if ownership:
        summary = summarize_records(ownership)
        by_source = summary["by_source"]
        expected_pitch = summary["expected_pitch"]
        strongest_pairs = summary["strongest_pairs"]
        first_rows = summary["first_rows"]
        source_rows = summary["source_rows"]
        expected_debug_rows = summary["expected_debug_rows"]
        expected_source_debug_rows = summary["expected_source_debug_rows"]
        expected_row_paths = summary["expected_row_paths"]
        expected_source_row_paths = summary["expected_source_row_paths"]
        lines.append(f"analyze_real_note_misses: ownership misses {len(ownership)}")
        lines.append(
            "ownership by source "
            + " ".join(f"{key}={value}" for key, value in by_source.most_common(12))
        )
        lines.append(
            "ownership first rows "
            + " ".join(f"{key}={value}" for key, value in first_rows.most_common())
        )
        lines.append(
            "ownership source rows "
            + " ".join(
                f"{source}->{row}={count}"
                for (source, row), count in source_rows.most_common(12)
            )
        )
        if expected_debug_rows:
            lines.append(
                "ownership expected pitch rows "
                + " ".join(f"{row}={count}" for row, count in expected_debug_rows.most_common())
            )
        if expected_source_debug_rows:
            lines.append(
                "ownership expected source pitch rows "
                + " ".join(
                    f"{source}->{row}={count}"
                    for (source, row), count in expected_source_debug_rows.most_common(12)
                )
            )
        if expected_row_paths:
            lines.append(
                "ownership expected row paths "
                + " ".join(
                    f"{format_row_path(path)}={count}"
                    for path, count in expected_row_paths.most_common(12)
                )
            )
        if expected_source_row_paths:
            lines.append(
                "ownership source row paths "
                + " ".join(
                    f"{source}:{format_row_path(path)}={count}"
                    for (source, path), count in expected_source_row_paths.most_common(12)
                )
            )
        lines.append(
            "ownership by expected pitch "
            + " ".join(f"{key}={value}" for key, value in sorted(expected_pitch.items()))
        )
        lines.append(
            "ownership strongest detected "
            + " ".join(
                f"{expected}->{detected}={count}"
                for (expected, detected), count in strongest_pairs.most_common(12)
            )
        )
        lines.append(
            f"ownership expected present in verbose grids {summary['expected_present_in_debug']}/{len(ownership)}"
        )
        example_parts = []
        for (source, row), _count in source_rows.most_common(8):
            examples = summary["source_row_examples"].get((source, row), [])
            if examples:
                example_parts.append(f"{source}->{row}: " + ", ".join(examples))
        if example_parts:
            lines.append("ownership examples " + " | ".join(example_parts))
        if summary["missing_all_notes"]:
            lines.append(f"ownership no detected note levels {summary['missing_all_notes']}")
    return lines


def main() -> int:
    paths = [pathlib.Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = [pathlib.Path("build/real_note_full_mix_verbose.err")]
    for line in analyze_paths(paths):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
