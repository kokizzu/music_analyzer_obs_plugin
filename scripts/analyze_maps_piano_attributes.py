#!/usr/bin/env python3
"""Summarize per-window MAPS piano note and chord detection traits."""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path


def labels(value: str) -> list[str]:
    return [] if value in {"", "--"} else value.split(",")


def midi_levels(value: str) -> dict[int, float]:
    result: dict[int, float] = {}
    for item in labels(value):
        midi, separator, level = item.partition(":")
        if not separator:
            continue
        try:
            result[int(midi)] = float(level)
        except ValueError:
            continue
    return result


def pitch_class(midi: int) -> int:
    return midi % 12


def harmonic_aliases(midis: list[int], levels: dict[int, float], minimum_ratio: float) -> set[int]:
    intervals = (12, 19, 24, 28, 31, 36, 38, 40, 43, 45, 47, 48)
    removed: set[int] = set()
    for upper in midis:
        upper_level = levels.get(upper, 0.0)
        if upper_level <= 0.0:
            continue
        for interval in intervals:
            lower = upper - interval
            if lower not in levels or levels[lower] < upper_level * minimum_ratio:
                continue
            removed.add(upper)
            break
    return removed


def top(counter: collections.Counter[str], limit: int) -> str:
    return " ".join(f"{name}={count}" for name, count in counter.most_common(limit)) or "none"


def ratio(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator} ({numerator / denominator * 100.0:.1f}%)" if denominator else "--"


def summarize(path: Path, limit: int) -> list[str]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"missing_pcs", "extra_pcs", "expected_chords", "chord_hit", "keyboard_chord"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing MAPS attribute columns")

    missing_components: collections.Counter[str] = collections.Counter()
    extra_components: collections.Counter[str] = collections.Counter()
    missing_patterns: collections.Counter[str] = collections.Counter()
    chord_misses: collections.Counter[str] = collections.Counter()
    chord_miss_predictions: collections.Counter[str] = collections.Counter()
    no_chord_detected_pc_counts: collections.Counter[int] = collections.Counter()
    no_chord_debug: collections.Counter[str] = collections.Counter()
    note_routes: collections.Counter[str] = collections.Counter()
    midi_offsets: collections.Counter[int] = collections.Counter()
    detected_midi_counts: collections.Counter[int] = collections.Counter()
    expected_note_hits = 0
    expected_note_total = 0
    detected_pitch_total = 0
    harmonic_only_predictions = 0
    harmonic_only_hits = 0
    harmonic_only_extras = 0
    harmonic_only_misses = 0
    harmonic_prune_stats = {
        ratio: {"removed": 0, "hits": 0, "predicted": 0}
        for ratio in (0.25, 0.50, 0.75, 1.00)
    }
    candidate_floor_stats = {
        floor: {"hits": 0, "predicted": 0}
        for floor in (0.15, 0.18, 0.20, 0.25, 0.30)
    }
    rms_by_detection: dict[str, list[float]] = {"hit": [], "miss": []}
    chord_rms_by_detection: dict[str, list[float]] = {"hit": [], "miss": []}
    chord_note_counts: dict[str, list[int]] = {"hit": [], "miss": []}
    no_keyboard_chord = 0
    complete_pitch_chord_misses = 0
    complete_pitch_chord_labels: collections.Counter[str] = collections.Counter()
    complete_pitch_chord_predictions: collections.Counter[str] = collections.Counter()
    complete_pitch_chord_debug: collections.Counter[str] = collections.Counter()
    complete_pitch_chord_examples: list[str] = []
    isolated_note_miss_examples: list[str] = []
    audible_isolated_note_misses: list[tuple[float, str]] = []
    for row in rows:
        missing = labels(row["missing_pcs"])
        extra = labels(row["extra_pcs"])
        expected = labels(row["expected_pcs"])
        detected = labels(row["detected_keyboard_pcs"])
        missing_components.update(missing)
        extra_components.update(extra)
        if missing:
            missing_patterns[row["missing_pcs"]] += 1
        if len(expected) == 1:
            expected_note_total += 1
            expected_note_hits += expected[0] in detected
            detected_pitch_total += len(detected)
            note_routes[f"{expected[0]}->{','.join(detected) if detected else '--'}"] += 1
            bucket = "hit" if expected[0] in detected else "miss"
            rms_by_detection[bucket].append(float(row["audio_rms"]))
            if bucket == "miss" and len(isolated_note_miss_examples) < limit:
                isolated_note_miss_examples.append(
                    f"{row['recording']}@{row['center_sample']} expected={expected[0]} "
                    f"detected={','.join(detected) if detected else '--'} "
                    f"midis={row['detected_keyboard_midis'] or '--'} "
                    f"levels={row.get('keyboard_levels', '') or '--'} "
                    f"rms={row['audio_rms']} peak={row['audio_peak']}"
                )
            if bucket == "miss":
                audible_isolated_note_misses.append(
                    (
                        float(row["audio_rms"]),
                        f"{row['recording']}@{row['center_sample']} expected={expected[0]} "
                        f"detected={','.join(detected) if detected else '--'} "
                        f"midis={row['detected_keyboard_midis'] or '--'} "
                        f"levels={row.get('keyboard_levels', '') or '--'} "
                        f"rms={row['audio_rms']} peak={row['audio_peak']}",
                    )
                )
        expected_midis = [int(value) for value in labels(row["expected_midis"])]
        detected_midis = [int(value) for value in labels(row["detected_keyboard_midis"])]
        if len(expected_midis) == 1:
            detected_midi_counts[len(detected_midis)] += 1
            midi_offsets.update(midi - expected_midis[0] for midi in detected_midis if midi != expected_midis[0])
            harmonic_intervals = {12, 19, 24, 28, 31, 36, 38, 40, 43, 45, 47, 48}
            has_harmonic_base = any(
                all(midi == base or midi - base in harmonic_intervals for midi in detected_midis)
                for base in detected_midis
            )
            if len(detected_midis) > 1 and has_harmonic_base:
                harmonic_only_predictions += 1
                harmonic_only_hits += expected_midis[0] in detected_midis
                harmonic_only_extras += sum(midi != expected_midis[0] for midi in detected_midis)
                harmonic_only_misses += expected_midis[0] not in detected_midis
            levels = midi_levels(row.get("keyboard_midi_levels", ""))
            if levels:
                strongest_level = max(levels.values())
                for floor, stats in candidate_floor_stats.items():
                    retained_pcs = {
                        pitch_class(midi)
                        for midi, level in levels.items()
                        if level >= strongest_level * floor
                    }
                    stats["hits"] += pitch_class(expected_midis[0]) in retained_pcs
                    stats["predicted"] += len(retained_pcs)
                for minimum_ratio, stats in harmonic_prune_stats.items():
                    removed = harmonic_aliases(detected_midis, levels, minimum_ratio)
                    retained_pcs = {pitch_class(midi) for midi in detected_midis if midi not in removed}
                    stats["removed"] += len(removed)
                    stats["hits"] += pitch_class(expected_midis[0]) in retained_pcs
                    stats["predicted"] += len(retained_pcs)
        expected_chords = labels(row["expected_chords"])
        if expected_chords:
            chord_bucket = "hit" if row["chord_hit"] == "1" else "miss"
            chord_rms_by_detection[chord_bucket].append(float(row["audio_rms"]))
            chord_note_counts[chord_bucket].append(len(expected_midis))
        if expected_chords and row["chord_hit"] != "1":
            chord_misses[row["expected_chords"]] += 1
            chord_miss_predictions[row["keyboard_chord"]] += 1
            if row["keyboard_chord"] == "--":
                no_keyboard_chord += 1
                no_chord_detected_pc_counts[len(labels(row["detected_chord_pcs"]))] += 1
                no_chord_debug[row["chord_debug"]] += 1
            if not labels(row["missing_pcs"]):
                complete_pitch_chord_misses += 1
                complete_pitch_chord_labels[row["expected_chords"]] += 1
                complete_pitch_chord_predictions[row["keyboard_chord"]] += 1
                complete_pitch_chord_debug[row["chord_debug"]] += 1
                if len(complete_pitch_chord_examples) < limit:
                    complete_pitch_chord_examples.append(
                        f"{row['recording']}@{row['center_sample']} "
                        f"expected={row['expected_chords']} keyboard={row['keyboard_chord']} "
                        f"chord_levels={row.get('keyboard_chord_levels', '--')} "
                        f"path={row['chord_debug']}"
                    )

    chord_windows = sum(bool(labels(row["expected_chords"])) for row in rows)
    return [
        f"analyze_maps_piano_attributes: windows={len(rows)} chord_windows={chord_windows}",
        "missing pitch-class components " + top(missing_components, limit),
        "extra keyboard pitch-class components " + top(extra_components, limit),
        "top missing pitch-class patterns " + top(missing_patterns, limit),
        "top expected-to-keyboard pitch routes " + top(note_routes, limit),
        "top detected MIDI offsets from expected " + top(midi_offsets, limit),
        "isolated-note pitch recall/precision "
        f"{ratio(expected_note_hits, expected_note_total)}/"
        f"{ratio(expected_note_hits, detected_pitch_total)} "
        f"false_predictions={detected_pitch_total - expected_note_hits}",
        "isolated-note miss examples " + " | ".join(isolated_note_miss_examples),
        "loudest isolated-note miss examples " + " | ".join(
            example for _, example in sorted(audible_isolated_note_misses, reverse=True)[:limit]
        ),
        "detected MIDI count distribution " + top(detected_midi_counts, limit),
        "single-series harmonic predictions "
        f"windows={harmonic_only_predictions} hits={harmonic_only_hits} "
        f"extras={harmonic_only_extras} misses={harmonic_only_misses}",
        "isolated harmonic-alias pruning simulation " + "; ".join(
            f"lower/upper>={minimum_ratio:.2f}: removed={stats['removed']} "
            f"recall={ratio(stats['hits'], expected_note_total)} "
            f"precision={ratio(stats['hits'], stats['predicted'])}"
            for minimum_ratio, stats in harmonic_prune_stats.items()
        ),
        "isolated candidate-floor simulation " + "; ".join(
            f"floor>={floor:.2f}: recall={ratio(stats['hits'], expected_note_total)} "
            f"precision={ratio(stats['hits'], stats['predicted'])}"
            for floor, stats in candidate_floor_stats.items()
        ),
        "audio RMS median hit/miss " + "/".join(
            f"{sorted(values)[len(values) // 2]:.5f}" if values else "--"
            for values in (rms_by_detection["hit"], rms_by_detection["miss"])
        ),
        "chord RMS median hit/miss " + "/".join(
            f"{sorted(values)[len(values) // 2]:.5f}" if values else "--"
            for values in (chord_rms_by_detection["hit"], chord_rms_by_detection["miss"])
        ),
        "chord expected-note median hit/miss " + "/".join(
            str(sorted(values)[len(values) // 2]) if values else "--"
            for values in (chord_note_counts["hit"], chord_note_counts["miss"])
        ),
        f"chord misses={sum(chord_misses.values())}/{chord_windows} no_keyboard_chord={no_keyboard_chord}",
        "no-label missed windows by chord-grid pitch classes " + top(no_chord_detected_pc_counts, limit),
        "no-label chord detector paths " + top(no_chord_debug, limit),
        f"chord misses with every expected pitch class visible={complete_pitch_chord_misses}/{sum(chord_misses.values())}",
        "complete-pitch missed expected chord labels " + top(complete_pitch_chord_labels, limit),
        "keyboard labels on complete-pitch chord misses " + top(complete_pitch_chord_predictions, limit),
        "complete-pitch chord detector paths " + top(complete_pitch_chord_debug, limit),
        "complete-pitch chord miss examples " + " | ".join(complete_pitch_chord_examples),
        "top missed expected chord labels " + top(chord_misses, limit),
        "keyboard labels on chord misses " + top(chord_miss_predictions, limit),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    try:
        print("\n".join(summarize(args.input, max(1, args.limit))))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
