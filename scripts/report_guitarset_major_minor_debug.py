#!/usr/bin/env python3
"""Summarize recorded GuitarSet major/minor misses from guarded debug output."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "guitarset_debug_windows.log"
PLAIN = re.compile(r"^[A-G](?:#)?m?$")
DEBUG = re.compile(r"^(.*?): expected chord `([^`]*)`, .*?guitar `([^`]*)`")
DETAIL = re.compile(
    r"^(.*?): expected chord `([^`]*)`, .*?guitar cells `([^`]*)`, .*?guitar `([^`]*)`, "
    r".*?guitar analysis cells `([^`]*)`, .*?guitar smooth cells `([^`]*)`$")
CELL = re.compile(r"([A-G]#?)-?\d+:([0-9.]+)")
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
        "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def labels(value: str) -> set[str]:
    return {part for part in value.split("=") if part and part != "--"}


def grid_levels(cells: str) -> list[float]:
    levels = [0.0] * 12
    for name, value in CELL.findall(cells):
        levels[NOTE[name]] = max(levels[NOTE[name]], float(value))
    return levels


def chord_tone_levels(chord: str, cells: str) -> tuple[float, float, float]:
    match = re.match(r"^([A-G]#?)(m?)$", chord)
    assert match
    root_name, minor = match.groups()
    root = NOTE[root_name]
    levels = grid_levels(cells)
    return levels[root], levels[(root + (3 if minor else 4)) % 12], levels[(root + 7) % 12]


def opposite_third_level(chord: str, cells: str) -> float:
    match = re.match(r"^([A-G]#?)(m?)$", chord)
    assert match
    root_name, minor = match.groups()
    return grid_levels(cells)[(NOTE[root_name] + (4 if minor else 3)) % 12]


def analysis_gate_result(chord: str, display_cells: str, analysis_cells: str) -> str:
    match = re.match(r"^([A-G]#?)(m?)$", chord)
    assert match
    root_name, minor = match.groups()
    root = NOTE[root_name]
    display = grid_levels(display_cells)
    analysis = grid_levels(analysis_cells)
    active = sum(level > 0.0 for level in analysis)
    display_active = sum(level > 0.0 for level in display)
    if active < 3 or active > 10:
        return f"analysis-pitch-classes={active}"
    if display_active > 7:
        return f"display-pitch-classes={display_active}"
    third = (root + (3 if minor else 4)) % 12
    opposite = (root + (4 if minor else 3)) % 12
    fifth = (root + 7) % 12
    display_tones = sum(display[pitch] > 0.0 for pitch in (root, third, fifth))
    compact_fifth = display_tones == 1 and display[fifth] > 0.0 and active <= 4 and display_active <= 2
    compact_root = display_tones == 1 and display[root] > 0.0 and active <= 6 and display_active <= 4
    if display_tones < 2 and not compact_fifth and not compact_root:
        return f"display-tones={display_tones}"
    strongest = max(analysis)
    anchor = min(analysis[root], analysis[fifth])
    if active > 8:
        if display[root] == 0.0:
            return "noisy-no-display-root"
        core = max(0.12, strongest * 0.10)
        if analysis[root] < core or analysis[fifth] < core:
            return "noisy-core-floor"
        third_floor = max(0.16, anchor * 0.30, strongest * 0.10)
        if analysis[third] < third_floor:
            return "noisy-third-floor"
        if analysis[opposite] >= max(0.10, analysis[third] * 0.80):
            return "noisy-opposite-third"
    else:
        if analysis[root] < max(0.060, strongest * 0.055) or analysis[fifth] < max(0.055, strongest * 0.050):
            return "core-floor"
        if analysis[third] < max(0.024, anchor * 0.045):
            return "third-floor"
        if analysis[opposite] >= max(0.12, anchor * 0.22) and analysis[opposite] >= analysis[third] * 1.30:
            return "opposite-third"
    if compact_fifth and (analysis[root] < 0.060 or analysis[third] < max(0.024, anchor * 0.045)
                          or analysis[fifth] < max(0.40, strongest * 0.40)):
        return "compact-fifth-floor"
    if compact_root and (analysis[root] < max(0.32, strongest * 0.32)
                         or analysis[third] < max(0.032, anchor * 0.050)
                         or analysis[fifth] < max(0.090, strongest * 0.085)):
        return "compact-root-floor"
    if display[(root - 1) % 12] > 0.0 and display[(root + 1) % 12] > 0.0 and analysis[third] < anchor * 0.12:
        return "adjacent-root-noise"
    return "passes"


def main() -> int:
    if not LOG.is_file():
        print("run make guitarset-debug-windows first", file=sys.stderr)
        return 1
    misses: list[str] = []
    analysis_complete_display_incomplete: list[str] = []
    display_complete_label_misses: list[str] = []
    expected_counts: Counter[str] = Counter()
    log_lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in log_lines:
        match = DEBUG.match(line)
        if not match:
            continue
        context, expected_text, actual_text = match.groups()
        expected = labels(expected_text)
        actual = labels(actual_text)
        for chord in sorted(expected):
            if not PLAIN.fullmatch(chord):
                continue
            expected_counts[chord] += 1
            if chord not in actual:
                misses.append(f"{context}: expected {chord}; guitar {actual_text}")
    for line in log_lines:
        match = DETAIL.match(line)
        if not match:
            continue
        context, expected_text, display_cells, actual_text, analysis_cells, smooth_cells = match.groups()
        actual = labels(actual_text)
        for chord in sorted(labels(expected_text)):
            if not PLAIN.fullmatch(chord) or chord in actual:
                continue
            display = chord_tone_levels(chord, display_cells)
            analysis = chord_tone_levels(chord, analysis_cells)
            smooth = chord_tone_levels(chord, smooth_cells)
            opposite = opposite_third_level(chord, analysis_cells)
            gate = analysis_gate_result(chord, display_cells, analysis_cells)
            detail = (f"{context}: expected {chord}; guitar {actual_text}; "
                      f"display r3f={display[0]:.2f}/{display[1]:.2f}/{display[2]:.2f}; "
                      f"analysis r3f={analysis[0]:.2f}/{analysis[1]:.2f}/{analysis[2]:.2f}; "
                      f"smooth r3f={smooth[0]:.2f}/{smooth[1]:.2f}/{smooth[2]:.2f}; "
                      f"analysis opposite3={opposite:.2f}; gate={gate}")
            if min(analysis) > 0.0 and min(display) == 0.0:
                analysis_complete_display_incomplete.append(detail)
            if min(display) > 0.0:
                display_complete_label_misses.append(detail)
    print(f"major/minor debug checks {sum(expected_counts.values())}")
    print(f"major/minor debug misses {len(misses)}")
    for chord, count in expected_counts.most_common():
        print(f"checks {chord} {count}")
    for line in misses[:20]:
        print(line)
    print(f"analysis-complete/display-incomplete major/minor misses {len(analysis_complete_display_incomplete)}")
    for line in analysis_complete_display_incomplete[:40]:
        print(line)
    print(f"display-complete label major/minor misses {len(display_complete_label_misses)}")
    for line in display_complete_label_misses[:40]:
        print(line)
    raw_lines = [line for line in log_lines if "raw profile" in line.lower() or "raw expected" in line.lower()]
    print(f"raw-profile diagnostic lines {len(raw_lines)}")
    for line in raw_lines[:40]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
