#!/usr/bin/env python3
"""Evaluate probe-only plain guitar chord recovery candidates."""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
from collections import Counter

from analyze_guitar_chord_recovery import (
    NOTE_TO_PC,
    expected_root,
    is_plain_major_or_minor,
    parse_cell_levels,
    split_labels,
)
from inspect_guitarset_attribute_buckets import derive_row as derive_guitarset_row


PC_TO_NOTE = {value: key for key, value in NOTE_TO_PC.items()}


def plain_label(root: int, minor: bool) -> str:
    return f"{PC_TO_NOTE[root % 12]}{'m' if minor else ''}"


def chord_tones(root: int, minor: bool) -> set[int]:
    return {root % 12, (root + (3 if minor else 4)) % 12, (root + 7) % 12}


def normalize(levels: dict[int, float]) -> dict[int, float]:
    peak = max(levels.values(), default=0.0)
    if peak <= 1.0e-9:
        return {}
    return {pitch_class: value / peak for pitch_class, value in levels.items()}


def detect_probe_only_plain(
    levels: dict[int, float],
    *,
    root_floor: float,
    third_floor: float,
    fifth_floor: float,
    opposite_margin: float,
    max_extra: int,
    extra_floor: float,
    min_gap: float,
) -> tuple[str, float, str]:
    levels = normalize(levels)
    if not levels:
        return "", 0.0, ""

    best: tuple[float, str, str] | None = None
    for root in range(12):
        for minor in (False, True):
            third = (root + (3 if minor else 4)) % 12
            opposite = (root + (4 if minor else 3)) % 12
            fifth = (root + 7) % 12
            root_level = levels.get(root, 0.0)
            third_level = levels.get(third, 0.0)
            fifth_level = levels.get(fifth, 0.0)
            opposite_level = levels.get(opposite, 0.0)
            if root_level < root_floor or third_level < third_floor or fifth_level < fifth_floor:
                continue
            if third_level < opposite_level * opposite_margin:
                continue
            extra = 0
            extra_sum = 0.0
            for pitch_class, level in levels.items():
                if pitch_class in {root, third, fifth}:
                    continue
                if level >= extra_floor:
                    extra += 1
                    extra_sum += level
            if extra > max_extra:
                continue
            anchor = min(root_level, fifth_level)
            score = root_level * 0.42 + third_level * 0.38 + fifth_level * 0.42
            score += min(root_level, third_level, fifth_level) * 0.50
            score += anchor * 0.22
            score -= opposite_level * 0.45 + extra_sum * 0.10
            label = plain_label(root, minor)
            detail = (
                f"{label} r/t/f/o={root_level:.3f}/{third_level:.3f}/"
                f"{fifth_level:.3f}/{opposite_level:.3f} extra={extra}"
            )
            if best is None or score > best[0]:
                best = (score, label, detail)

    if best is None:
        return "", 0.0, ""

    runner_up = 0.0
    for root in range(12):
        for minor in (False, True):
            label = plain_label(root, minor)
            if label == best[1]:
                continue
            third = (root + (3 if minor else 4)) % 12
            opposite = (root + (4 if minor else 3)) % 12
            fifth = (root + 7) % 12
            root_level = levels.get(root, 0.0)
            third_level = levels.get(third, 0.0)
            fifth_level = levels.get(fifth, 0.0)
            opposite_level = levels.get(opposite, 0.0)
            if root_level < root_floor or third_level < third_floor or fifth_level < fifth_floor:
                continue
            if third_level < opposite_level * opposite_margin:
                continue
            tones = chord_tones(root, minor)
            extra_sum = sum(level for pc, level in levels.items() if pc not in tones and level >= extra_floor)
            anchor = min(root_level, fifth_level)
            score = root_level * 0.42 + third_level * 0.38 + fifth_level * 0.42
            score += min(root_level, third_level, fifth_level) * 0.50
            score += anchor * 0.22
            score -= opposite_level * 0.45 + extra_sum * 0.10
            runner_up = max(runner_up, score)

    if best[0] < runner_up + min_gap:
        return "", 0.0, ""
    return best[1], best[0], best[2]


def expected_plain_labels(row: dict[str, str]) -> set[str]:
    return {label for label in split_labels(row.get("expected_chords", "")) if is_plain_major_or_minor(label)}


def simplified_expected_plain_labels(row: dict[str, str]) -> set[str]:
    labels = set(expected_plain_labels(row))
    for label in split_labels(row.get("expected_chords", "")):
        root = expected_root(label)
        if root is None:
            continue
        if re.match(r"^[A-G]#?(?:maj7|7|6|add9|9|maj9)$", label):
            labels.add(plain_label(root, False))
        elif re.match(r"^[A-G]#?(?:m7|m6|m9)$", label):
            labels.add(plain_label(root, True))
    return labels


def grid_empty(row: dict[str, str]) -> bool:
    return (
        int(float(row.get("guitar_pc_count", "0") or 0)) == 0
        and int(float(row.get("analysis_pc_count", "0") or 0)) == 0
        and int(float(row.get("smooth_pc_count", "0") or 0)) == 0
    )


def source_levels(row: dict[str, str], source: str) -> dict[int, float]:
    if source == "probe":
        return parse_cell_levels(row.get("guitar_probe_pitch_class_levels", ""))
    if source == "melodic":
        return parse_cell_levels(row.get("guitar_melodic_probe_pitch_class_levels", ""))
    if source == "raw":
        return parse_cell_levels(row.get("raw_pitch_class_levels", ""))
    raise ValueError(source)


def load_rows(paths: list[pathlib.Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", errors="replace") as handle:
            rows.extend(derive_guitarset_row(row) for row in csv.DictReader(handle, delimiter="\t"))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="+", type=pathlib.Path)
    parser.add_argument("--source", choices=("probe", "melodic", "raw"), default="probe")
    parser.add_argument("--root-floor", type=float, default=0.28)
    parser.add_argument("--third-floor", type=float, default=0.32)
    parser.add_argument("--fifth-floor", type=float, default=0.24)
    parser.add_argument("--opposite-margin", type=float, default=1.50)
    parser.add_argument("--max-extra", type=int, default=2)
    parser.add_argument("--extra-floor", type=float, default=0.34)
    parser.add_argument("--min-gap", type=float, default=0.20)
    parser.add_argument("--include-non-empty", action="store_true")
    parser.add_argument("--show", type=int, default=16)
    args = parser.parse_args()

    rows = load_rows(args.path)
    gated_rows = [row for row in rows if args.include_non_empty or grid_empty(row)]

    recoveries: list[tuple[dict[str, str], str, str]] = []
    simplified: list[tuple[dict[str, str], str, str]] = []
    false_candidates: list[tuple[dict[str, str], str, str]] = []
    neutral: list[tuple[dict[str, str], str, str]] = []
    status_counts: Counter[str] = Counter()

    for row in gated_rows:
        levels = source_levels(row, args.source)
        label, _score, detail = detect_probe_only_plain(
            levels,
            root_floor=args.root_floor,
            third_floor=args.third_floor,
            fifth_floor=args.fifth_floor,
            opposite_margin=args.opposite_margin,
            max_extra=args.max_extra,
            extra_floor=args.extra_floor,
            min_gap=args.min_gap,
        )
        if not label:
            continue

        status = row.get("status", "--") or "--"
        expected = expected_plain_labels(row)
        simplified_expected = simplified_expected_plain_labels(row)
        status_counts[status] += 1
        if label in expected and status == "chord_miss":
            recoveries.append((row, label, detail))
        elif label in simplified_expected and status == "chord_miss":
            simplified.append((row, label, detail))
        elif status in {"chord_hit", "single_note_false_chord", "no_chord"} or expected or simplified_expected:
            false_candidates.append((row, label, detail))
        else:
            neutral.append((row, label, detail))

    print(
        "probe_only",
        f"source={args.source}",
        f"rows={len(rows)}",
        f"gated={len(gated_rows)}",
        "pitch_class_only=1",
        f"candidates={sum(status_counts.values())}",
        f"recoveries={len(recoveries)}",
        f"simplified={len(simplified)}",
        f"false={len(false_candidates)}",
        f"neutral={len(neutral)}",
        "statuses=" + (" ".join(f"{key}={value}" for key, value in status_counts.most_common()) or "--"),
    )
    for title, examples in (
        ("recoveries", recoveries),
        ("simplified", simplified),
        ("false", false_candidates),
        ("neutral", neutral),
    ):
        print(title)
        for row, label, detail in examples[: max(0, args.show)]:
            print(
                "  "
                f"{row.get('recording_id', '')} status={row.get('status', '')} "
                f"expected={row.get('expected_chords', '--')} got={row.get('guitar_chord', '--')} "
                f"candidate={label} {detail} source={row.get('audio_path', '')}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
