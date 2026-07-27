#!/usr/bin/env python3
"""Inspect guitar chord primary-label ordering from exported attribute rows."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re


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
CELL_RE = re.compile(r"([A-G]#?)(?:-?\d+)?:([-+0-9.eE]+)")


def split_components(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [item for item in re.split(r"[=/]", value) if item and item != "--"]


def chord_root(label: str) -> str:
    if len(label) >= 2 and label[1] == "#":
        return label[:2]
    return label[:1]


def chord_quality(label: str) -> str:
    root = chord_root(label)
    return label[len(root) :]


def parse_plain(label: str) -> tuple[int, bool] | None:
    root_name = chord_root(label)
    if root_name not in NOTE_TO_PC:
        return None
    quality = chord_quality(label)
    if quality == "":
        return NOTE_TO_PC[root_name], False
    if quality == "m":
        return NOTE_TO_PC[root_name], True
    return None


def is_power_for_root(label: str, root: int) -> bool:
    return label == f"{PC_TO_NOTE[root % 12]}pow"


def parse_cells(value: str) -> dict[int, float]:
    levels: dict[int, float] = {}
    for match in CELL_RE.finditer(value or ""):
        note = match.group(1)
        if note not in NOTE_TO_PC:
            continue
        try:
            level = float(match.group(2))
        except ValueError:
            continue
        pc = NOTE_TO_PC[note]
        levels[pc] = max(levels.get(pc, 0.0), level)
    return levels


def primary_component(value: str) -> str:
    components = split_components(value)
    return components[0] if components else "--"


def pitch_classes(value: str) -> set[int]:
    if not value or value == "--":
        return set()
    return {NOTE_TO_PC[item] for item in value.split(",") if item in NOTE_TO_PC}


def chord_tones(root: int, minor: bool) -> set[int]:
    return {root % 12, (root + (3 if minor else 4)) % 12, (root + 7) % 12}


def component_score(
    label: str,
    display: set[int],
    analysis: set[int],
    display_levels: dict[int, float],
    analysis_levels: dict[int, float],
) -> float:
    parsed = parse_plain(label)
    if parsed is None:
        return -1.0
    root, minor = parsed
    tones = chord_tones(root, minor)
    display_tones = len(tones & display)
    analysis_tones = len(tones & analysis)
    if display_tones < 2 or analysis_tones < 2:
        return -1.0
    third = (root + (3 if minor else 4)) % 12
    opposite = (root + (4 if minor else 3)) % 12
    level = lambda pc: max(display_levels.get(pc % 12, 0.0), analysis_levels.get(pc % 12, 0.0))
    root_level = level(root)
    third_level = level(third)
    fifth_level = level(root + 7)
    anchor = min(root_level, fifth_level)
    opposite_level = level(opposite)
    if anchor < 0.08:
        return -1.0
    if third_level < max(0.012, anchor * 0.018) and display_tones + analysis_tones < 5:
        return -1.0
    if opposite_level >= max(0.18, anchor * 0.55) and opposite_level > third_level * 1.35:
        return -1.0
    return display_tones * 1.15 + analysis_tones * 0.85 + anchor * 0.55 + third_level * 0.35


def expected_labels(value: str) -> set[str]:
    return set(split_components(value))


def confidence_value(row: dict[str, str], field: str) -> str:
    value = row.get(field, "")
    return value if value else "--"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--examples", type=int, default=12)
    args = parser.parse_args()

    with args.path.open(newline="", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    chord_rows = [row for row in rows if row.get("expected_chords", "--") not in ("", "--")]
    for field in ("guitar_chord", "guitar_raw_chord", "guitar_smoothed_chord"):
        primary_hits = 0
        later_hits = 0
        misses = 0
        for row in chord_rows:
            expected = expected_labels(row.get("expected_chords", ""))
            components = split_components(row.get(field, ""))
            if components and components[0] in expected:
                primary_hits += 1
            elif expected & set(components):
                later_hits += 1
            else:
                misses += 1
        print(
            f"{field}:",
            f"primary={primary_hits}/{len(chord_rows)}",
            f"later={later_hits}",
            f"miss={misses}",
        )

    relationship_buckets: collections.Counter[str] = collections.Counter()
    raw_rescues = []
    smoothed_rescues = []
    both_rescues = []
    for row in chord_rows:
        expected = expected_labels(row.get("expected_chords", ""))
        displayed_primary = primary_component(row.get("guitar_chord", ""))
        raw_primary = primary_component(row.get("guitar_raw_chord", ""))
        smoothed_primary = primary_component(row.get("guitar_smoothed_chord", ""))
        displayed_hit = displayed_primary in expected
        raw_hit = raw_primary in expected
        smoothed_hit = smoothed_primary in expected
        relationship_buckets[
            f"display{int(displayed_hit)}_raw{int(raw_hit)}_smooth{int(smoothed_hit)}"
        ] += 1
        if not displayed_hit and raw_hit:
            raw_rescues.append(row)
        if not displayed_hit and smoothed_hit:
            smoothed_rescues.append(row)
        if not displayed_hit and raw_hit and smoothed_hit:
            both_rescues.append(row)

    if relationship_buckets:
        print(
            "candidate primary relationships:",
            " ".join(
                f"{key}={relationship_buckets[key]}" for key in sorted(relationship_buckets)
            ),
        )
        print(
            "candidate primary rescues:",
            f"raw={len(raw_rescues)}",
            f"smoothed={len(smoothed_rescues)}",
            f"both={len(both_rescues)}",
        )

        def print_rescue_examples(title: str, rescue_rows: list[dict[str, str]]) -> None:
            if not rescue_rows:
                return
            print(title)
            for row in rescue_rows[: args.examples]:
                print(
                    f"  expected={row.get('expected_chords')}",
                    f"display={primary_component(row.get('guitar_chord', ''))}",
                    f"raw={primary_component(row.get('guitar_raw_chord', ''))}",
                    f"smoothed={primary_component(row.get('guitar_smoothed_chord', ''))}",
                    "conf="
                    f"d:{confidence_value(row, 'guitar_chord_confidence')}/"
                    f"r:{confidence_value(row, 'guitar_raw_chord_confidence')}/"
                    f"s:{confidence_value(row, 'guitar_smoothed_chord_confidence')}",
                    pathlib.Path(row.get("audio_path", "")).name,
                )

        print_rescue_examples("raw primary rescue examples", raw_rescues)
        print_rescue_examples("smoothed primary rescue examples", smoothed_rescues)

    primary_misses = []
    expected_later = []
    score_gaps: list[float] = []
    likely_promotable = []
    cpp_promotable = []

    for row in chord_rows:
        expected = expected_labels(row.get("expected_chords", ""))
        components = split_components(row.get("guitar_chord", ""))
        if not components or components[0] in expected:
            continue
        primary_misses.append(row)
        if not expected & set(components):
            continue
        expected_later.append(row)

        display = pitch_classes(row.get("guitar_pitch_classes", ""))
        analysis = pitch_classes(row.get("guitar_analysis_pitch_classes", ""))
        display_levels = parse_cells(row.get("guitar_cells", ""))
        analysis_levels = parse_cells(row.get("guitar_analysis_cells", ""))
        primary_score = component_score(
            components[0], display, analysis, display_levels, analysis_levels
        )
        best_expected_score = max(
            component_score(label, display, analysis, display_levels, analysis_levels)
            for label in expected
        )
        score_gaps.append(best_expected_score - primary_score)
        if best_expected_score >= primary_score + 0.02:
            likely_promotable.append((best_expected_score - primary_score, row, components[0]))

        primary_plain = parse_plain(components[0])
        for label in sorted(expected & set(components)):
            parsed = parse_plain(label)
            if parsed is None:
                continue
            root, minor = parsed
            score = component_score(label, display, analysis, display_levels, analysis_levels)
            if score < 0.0:
                continue
            if any(is_power_for_root(component, root) for component in components):
                score += 0.72
            same_root_opposite = (
                primary_plain is not None
                and primary_plain[0] == root
                and primary_plain[1] != minor
            )
            different_root = primary_plain is None or primary_plain[0] != root
            has_power = any(is_power_for_root(component, root) for component in components)
            required_margin = (
                0.20
                if primary_plain is None
                else 0.18
                if has_power and different_root
                else 0.04
                if same_root_opposite
                else 0.48
            )
            if score >= primary_score + required_margin:
                cpp_promotable.append((score - primary_score, required_margin, row, components[0], label))
                break

    print(
        "guitar_primary_order:",
        f"rows={len(chord_rows)}",
        f"primary_misses={len(primary_misses)}",
        f"expected_later={len(expected_later)}",
        f"score_promotable={len(likely_promotable)}",
        f"cpp_promotable={len(cpp_promotable)}",
    )
    if score_gaps:
        buckets = collections.Counter()
        for gap in score_gaps:
            if gap >= 0.48:
                buckets[">=0.48"] += 1
            elif gap >= 0.18:
                buckets[">=0.18"] += 1
            elif gap >= 0.04:
                buckets[">=0.04"] += 1
            elif gap >= 0.0:
                buckets[">=0"] += 1
            else:
                buckets["<0"] += 1
        print("score_gap_buckets:", " ".join(f"{key}={value}" for key, value in buckets.items()))

    for gap, row, primary in sorted(likely_promotable, reverse=True)[: args.examples]:
        print(
            f"  gap={gap:.3f}",
            f"expected={row.get('expected_chords')}",
            f"primary={primary}",
            f"label={row.get('guitar_chord')}",
            f"pc={row.get('guitar_pitch_classes')}",
            f"analysis={row.get('guitar_analysis_pitch_classes')}",
            pathlib.Path(row.get("audio_path", "")).name,
        )
    if cpp_promotable:
        print("cpp-style promotable expected-later rows")
        for gap, margin, row, primary, label in sorted(
            cpp_promotable, key=lambda item: item[0], reverse=True
        )[: args.examples]:
            print(
                f"  gap={gap:.3f}",
                f"margin={margin:.3f}",
                f"promote={label}",
                f"expected={row.get('expected_chords')}",
                f"primary={primary}",
                f"label={row.get('guitar_chord')}",
                pathlib.Path(row.get("audio_path", "")).name,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
