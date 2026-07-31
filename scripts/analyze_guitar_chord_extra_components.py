#!/usr/bin/env python3
"""Summarize extra GuitarSet chord components beyond the expected labels."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re

from inspect_guitarset_attribute_buckets import derive_row as derive_guitarset_row


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
LABEL_RE = re.compile(r"^([A-G]#?)(.*)$")
CELL_RE = re.compile(r"^([A-G]#?)(-?\d+):([0-9.]+)$")
STANDARD_GUITAR_TUNING = (40, 45, 50, 55, 59, 64)
MAX_GUITAR_FRET = 15
MAX_COMPACT_FRET_SPAN = 5
MIN_OBSERVED_LEVEL = 0.12
TEMPLATES = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "pow": (0, 7),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "dim7": (0, 3, 6, 9),
    "m7b5": (0, 3, 6, 10),
    "9": (0, 2, 4, 7, 10),
    "maj9": (0, 2, 4, 7, 11),
    "m9": (0, 2, 3, 7, 10),
    "add9": (0, 2, 4, 7),
}


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_labels(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [label for label in value.replace("/", "=").split("=") if label and label != "--"]


def parse_label(label: str) -> tuple[int, str] | None:
    match = LABEL_RE.match(label)
    if not match:
        return None
    root = NOTE_TO_PC.get(match.group(1))
    if root is None:
        return None
    return root, match.group(2)


def label_suffix(label: str) -> str:
    parsed = parse_label(label)
    if parsed is None:
        return "unknown"
    suffix = parsed[1]
    return "maj" if suffix == "" else suffix


def pitch_set(label: str) -> frozenset[int] | None:
    parsed = parse_label(label)
    if parsed is None:
        return None
    root, suffix = parsed
    intervals = TEMPLATES.get(suffix)
    if intervals is None:
        return None
    return frozenset((root + interval) % 12 for interval in intervals)


def pitch_set_text(values: frozenset[int] | None) -> str:
    if not values:
        return "--"
    return ",".join(PC_TO_NOTE[pitch_class] for pitch_class in sorted(values))


def midi_from_note(note: str, octave_text: str) -> int | None:
    pitch_class = NOTE_TO_PC.get(note)
    if pitch_class is None:
        return None
    try:
        octave = int(octave_text)
    except ValueError:
        return None
    return (octave + 1) * 12 + pitch_class


def parse_cells(value: str, min_level: float = MIN_OBSERVED_LEVEL) -> list[tuple[int, int, float]]:
    cells: list[tuple[int, int, float]] = []
    if not value or value == "--":
        return cells
    for item in value.split(","):
        match = CELL_RE.match(item)
        if not match:
            continue
        midi = midi_from_note(match.group(1), match.group(2))
        if midi is None:
            continue
        try:
            level = float(match.group(3))
        except ValueError:
            continue
        if level >= min_level:
            cells.append((midi, midi % 12, level))
    return cells


def midi_positions(midi: int) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for string_index, open_midi in enumerate(STANDARD_GUITAR_TUNING):
        fret = midi - open_midi
        if 0 <= fret <= MAX_GUITAR_FRET:
            positions.append((string_index, fret))
    return positions


def compact_fret_span(positions: list[tuple[int, int]]) -> bool:
    fretted = [fret for _string_index, fret in positions if fret > 0]
    if not fretted:
        return True
    return max(fretted) - min(fretted) <= MAX_COMPACT_FRET_SPAN


def playable_position_assignment(choices_by_pitch: dict[int, list[tuple[int, int]]]) -> bool:
    if not choices_by_pitch:
        return False

    ordered = sorted(choices_by_pitch, key=lambda pitch_class: len(choices_by_pitch[pitch_class]))
    if any(not choices_by_pitch[pitch_class] for pitch_class in ordered):
        return False

    def search(index: int, used_strings: set[int], selected: list[tuple[int, int]]) -> bool:
        if index >= len(ordered):
            return compact_fret_span(selected)
        for string_index, fret in choices_by_pitch[ordered[index]]:
            if string_index in used_strings:
                continue
            used_strings.add(string_index)
            selected.append((string_index, fret))
            if search(index + 1, used_strings, selected):
                return True
            selected.pop()
            used_strings.remove(string_index)
        return False

    return search(0, set(), [])


def pitch_set_playable_on_standard_guitar(values: frozenset[int] | None) -> str:
    if not values:
        return "unknown"
    choices_by_pitch: dict[int, list[tuple[int, int]]] = {}
    for pitch_class in values:
        choices: list[tuple[int, int]] = []
        for string_index, open_midi in enumerate(STANDARD_GUITAR_TUNING):
            for fret in range(MAX_GUITAR_FRET + 1):
                if (open_midi + fret) % 12 == pitch_class:
                    choices.append((string_index, fret))
        choices_by_pitch[pitch_class] = choices
    return "playable" if playable_position_assignment(choices_by_pitch) else "unplayable"


def observed_pitch_set_playable(values: frozenset[int] | None, cells: list[tuple[int, int, float]]) -> bool:
    if not values or not cells:
        return False
    choices_by_pitch: dict[int, list[tuple[int, int]]] = {}
    for pitch_class in values:
        choices: list[tuple[int, int]] = []
        for midi, cell_pitch_class, _level in cells:
            if cell_pitch_class != pitch_class:
                continue
            choices.extend(midi_positions(midi))
        choices_by_pitch[pitch_class] = sorted(set(choices))
    return playable_position_assignment(choices_by_pitch)


def observed_playability(label: str, row: dict[str, str]) -> str:
    values = pitch_set(label)
    if not values:
        return "unknown"
    display_cells = parse_cells(row.get("guitar_cells", ""))
    analysis_cells = parse_cells(row.get("guitar_analysis_cells", ""))
    display = observed_pitch_set_playable(values, display_cells)
    analysis = observed_pitch_set_playable(values, analysis_cells)
    if display and analysis:
        return "display_analysis"
    if display:
        return "display_only"
    if analysis:
        return "analysis_only"
    return "unsupported"


def compact(counter: collections.Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def expected_roots(labels: list[str]) -> set[int]:
    roots: set[int] = set()
    for label in labels:
        parsed = parse_label(label)
        if parsed is not None:
            roots.add(parsed[0])
    return roots


def component_relation(label: str, expected_labels: list[str]) -> str:
    parsed = parse_label(label)
    if parsed is None:
        return "unparsed"
    label_pcs = pitch_set(label)
    expected_sets = [pcs for item in expected_labels if (pcs := pitch_set(item)) is not None]
    if label_pcs is not None:
        if any(label_pcs == expected for expected in expected_sets):
            return "same_pitch_set"
        if any(expected <= label_pcs for expected in expected_sets):
            return "contains_expected"
        if any(label_pcs <= expected for expected in expected_sets):
            return "subset_of_expected"
    if parsed[0] in expected_roots(expected_labels):
        return "same_root_extra"
    return "different_root_extra"


def detected_subset_relation(label: str, detected_labels: list[str]) -> str:
    parsed = parse_label(label)
    label_pcs = pitch_set(label)
    if parsed is None or label_pcs is None:
        return "--"
    for other in detected_labels:
        if other == label:
            continue
        other_parsed = parse_label(other)
        other_pcs = pitch_set(other)
        if other_parsed is None or other_pcs is None:
            continue
        if parsed[0] != other_parsed[0] and label_pcs < other_pcs:
            return f"rootless_subset_of_{other}"
    return "--"


def chord_hit(labels: list[str], expected_labels: list[str]) -> bool:
    expected = set(expected_labels)
    return any(label in expected for label in labels)


def same_root(label: str, reference: str) -> bool:
    parsed = parse_label(label)
    reference_parsed = parse_label(reference)
    return parsed is not None and reference_parsed is not None and parsed[0] == reference_parsed[0]


def same_pitch_set(label: str, reference: str) -> bool:
    label_pcs = pitch_set(label)
    reference_pcs = pitch_set(reference)
    return label_pcs is not None and label_pcs == reference_pcs


def is_plain_major_minor(label: str) -> bool:
    parsed = parse_label(label)
    return parsed is not None and parsed[1] in ("", "m")


def prune_labels(labels: list[str], policy: str, row: dict[str, str] | None = None) -> list[str]:
    if not labels:
        return []
    if policy == "none":
        return labels
    primary = labels[0]
    pruned = [primary]
    for label in labels[1:]:
        keep = False
        if policy == "primary":
            keep = False
        elif policy == "primary-equivalent":
            keep = same_pitch_set(label, primary)
        elif policy == "primary-equivalent-plain":
            keep = same_pitch_set(label, primary) or is_plain_major_minor(label)
        elif policy == "primary-equivalent-plain-observed-playable":
            keep = (
                same_pitch_set(label, primary)
                or is_plain_major_minor(label)
                or (row is not None and observed_playability(label, row) != "unsupported")
            )
        elif policy == "primary-same-root-equivalent":
            keep = same_root(label, primary) or same_pitch_set(label, primary)
        elif policy == "observed-playable":
            keep = row is not None and observed_playability(label, row) != "unsupported"
        elif policy == "primary-equivalent-observed-playable":
            keep = same_pitch_set(label, primary) or (
                row is not None and observed_playability(label, row) != "unsupported"
            )
        else:
            raise ValueError(f"unknown prune policy: {policy}")
        if keep and label not in pruned:
            pruned.append(label)
    return pruned


def row_extra_components(row: dict[str, str]) -> list[tuple[str, str, str, str]]:
    expected = split_labels(row.get("expected_chords", ""))
    expected_set = set(expected)
    detected = split_labels(row.get("guitar_chord", ""))
    extras: list[tuple[str, str, str, str]] = []
    for label in detected:
        if label in expected_set:
            continue
        extras.append(
            (
                label,
                label_suffix(label),
                component_relation(label, expected),
                detected_subset_relation(label, detected),
            )
        )
    return extras


def summarize_prune_policy(rows: list[dict[str, str]], policy: str, examples: int) -> list[str]:
    current_hits = 0
    pruned_hits = 0
    lost_hits = 0
    gained_hits = 0
    current_components = 0
    pruned_components = 0
    current_extras = 0
    pruned_extras = 0
    removed_counter: collections.Counter[str] = collections.Counter()
    retained_extra_counter: collections.Counter[str] = collections.Counter()
    lost_examples: list[tuple[dict[str, str], list[str], list[str]]] = []

    for row in rows:
        expected = split_labels(row.get("expected_chords", ""))
        detected = split_labels(row.get("guitar_chord", ""))
        pruned = prune_labels(detected, policy, row)
        current_hit = chord_hit(detected, expected)
        pruned_hit = chord_hit(pruned, expected)
        current_hits += int(current_hit)
        pruned_hits += int(pruned_hit)
        lost_hits += int(current_hit and not pruned_hit)
        gained_hits += int(pruned_hit and not current_hit)
        current_components += len(detected)
        pruned_components += len(pruned)

        expected_set = set(expected)
        current_extras += sum(1 for label in detected if label not in expected_set)
        pruned_extras += sum(1 for label in pruned if label not in expected_set)
        pruned_set = set(pruned)
        for label in detected:
            if label not in pruned_set:
                removed_counter[label_suffix(label)] += 1
        for label in pruned:
            if label not in expected_set:
                retained_extra_counter[label_suffix(label)] += 1
        if current_hit and not pruned_hit and len(lost_examples) < examples:
            lost_examples.append((row, detected, pruned))

    lines = [
        f"prune policy {policy}: rows={len(rows)} current_hits={current_hits} "
        f"pruned_hits={pruned_hits} lost_hits={lost_hits} gained_hits={gained_hits} "
        f"components={pruned_components}/{current_components} "
        f"extras={pruned_extras}/{current_extras}",
        f"  removed suffixes {compact(removed_counter, 10)}",
        f"  retained extra suffixes {compact(retained_extra_counter, 10)}",
    ]
    if lost_examples:
        lines.append("  lost hit examples")
        for row, detected, pruned in lost_examples:
            lines.append(
                "    "
                f"{row.get('recording_id', '')} expected={row.get('expected_chords', '')} "
                f"got={'='.join(detected) or '--'} pruned={'='.join(pruned) or '--'} "
                f"match={row.get('guitar_match_kind', '--')} "
                f"evidence={row.get('evidence_class', '--')}/{row.get('evidence_source', '--')}"
            )
    return lines


def summarize(path: pathlib.Path, examples: int, limit: int, prune_policies: list[str]) -> list[str]:
    rows = [derive_guitarset_row(row) for row in load_rows(path) if row.get("recording_id")]
    component_counter: collections.Counter[str] = collections.Counter()
    suffix_counter: collections.Counter[str] = collections.Counter()
    relation_counter: collections.Counter[str] = collections.Counter()
    hit_component_counter: collections.Counter[str] = collections.Counter()
    hit_suffix_counter: collections.Counter[str] = collections.Counter()
    hit_relation_counter: collections.Counter[str] = collections.Counter()
    subset_counter: collections.Counter[str] = collections.Counter()
    hit_subset_counter: collections.Counter[str] = collections.Counter()
    playable_counter: collections.Counter[str] = collections.Counter()
    hit_playable_counter: collections.Counter[str] = collections.Counter()
    observed_playable_counter: collections.Counter[str] = collections.Counter()
    hit_observed_playable_counter: collections.Counter[str] = collections.Counter()
    label_count_counter: collections.Counter[str] = collections.Counter()
    extra_count_counter: collections.Counter[str] = collections.Counter()
    rows_with_extras = 0
    hit_rows_with_extras = 0
    crowded_rows = 0
    hit_crowded_rows = 0
    max_components = 0
    examples_by_relation: dict[str, list[tuple[dict[str, str], str]]] = collections.defaultdict(list)
    subset_examples: list[tuple[dict[str, str], str, str]] = []
    unsupported_examples: list[tuple[dict[str, str], str, str]] = []

    for row in rows:
        detected = split_labels(row.get("guitar_chord", ""))
        extras = row_extra_components(row)
        label_count_counter[str(len(detected))] += 1
        extra_count_counter[str(len(extras))] += 1
        max_components = max(max_components, len(detected))
        if len(detected) >= 7:
            crowded_rows += 1
            if row.get("status") == "chord_hit":
                hit_crowded_rows += 1
        if not extras:
            continue
        rows_with_extras += 1
        if row.get("status") == "chord_hit":
            hit_rows_with_extras += 1
        for label, suffix, relation, subset_relation in extras:
            playable = pitch_set_playable_on_standard_guitar(pitch_set(label))
            observed = observed_playability(label, row)
            component_counter[label] += 1
            suffix_counter[suffix] += 1
            relation_counter[relation] += 1
            playable_counter[playable] += 1
            observed_playable_counter[observed] += 1
            if len(examples_by_relation[relation]) < examples:
                examples_by_relation[relation].append((row, label))
            if subset_relation != "--":
                subset_counter[subset_relation] += 1
                if len(subset_examples) < examples:
                    subset_examples.append((row, label, subset_relation))
            if observed == "unsupported" and len(unsupported_examples) < examples:
                unsupported_examples.append((row, label, observed))
            if row.get("status") == "chord_hit":
                hit_component_counter[label] += 1
                hit_suffix_counter[suffix] += 1
                hit_relation_counter[relation] += 1
                hit_playable_counter[playable] += 1
                hit_observed_playable_counter[observed] += 1
                if subset_relation != "--":
                    hit_subset_counter[subset_relation] += 1

    total_components = sum(component_counter.values())
    hit_components = sum(hit_component_counter.values())
    lines = [
        f"guitar chord extra components rows={rows_with_extras}/{len(rows)} "
        f"components={total_components} hit_rows={hit_rows_with_extras} hit_components={hit_components}",
        f"label component counts {compact(label_count_counter, limit)}",
        f"extra component counts {compact(extra_count_counter, limit)}",
        f"crowded labels >=7 rows={crowded_rows} hit_rows={hit_crowded_rows} "
        f"max_components={max_components}",
        f"component labels {compact(component_counter, limit)}",
        f"component suffixes {compact(suffix_counter, limit)}",
        f"component relations {compact(relation_counter, limit)}",
        f"component standard-guitar playability {compact(playable_counter, limit)}",
        f"component observed-guitar playability {compact(observed_playable_counter, limit)}",
        f"hit component labels {compact(hit_component_counter, limit)}",
        f"hit component suffixes {compact(hit_suffix_counter, limit)}",
        f"hit component relations {compact(hit_relation_counter, limit)}",
        f"hit component standard-guitar playability {compact(hit_playable_counter, limit)}",
        f"hit component observed-guitar playability {compact(hit_observed_playable_counter, limit)}",
        f"detected rootless subsets {compact(subset_counter, limit)}",
        f"hit detected rootless subsets {compact(hit_subset_counter, limit)}",
    ]

    if subset_examples:
        lines.append("detected rootless subset examples")
        for row, label, subset_relation in subset_examples:
            lines.append(
                "  "
                f"{row.get('recording_id', '')} status={row.get('status', '')} "
                f"expected={row.get('expected_chords', '')} got={row.get('guitar_chord', '--')} "
                f"extra={label} relation={subset_relation} "
                f"extra_pc={pitch_set_text(pitch_set(label))} "
                f"expected_pc={row.get('expected_pitch_classes', '--')} "
                f"match={row.get('guitar_match_kind', '--')} "
                f"evidence={row.get('evidence_class', '--')}/{row.get('evidence_source', '--')}"
            )

    if unsupported_examples:
        lines.append("observed-guitar unsupported examples")
        for row, label, _observed in unsupported_examples:
            lines.append(
                "  "
                f"{row.get('recording_id', '')} status={row.get('status', '')} "
                f"expected={row.get('expected_chords', '')} got={row.get('guitar_chord', '--')} "
                f"extra={label} "
                f"extra_pc={pitch_set_text(pitch_set(label))} "
                f"display_cells={row.get('guitar_cells', '--')} "
                f"analysis_cells={row.get('guitar_analysis_cells', '--')} "
                f"match={row.get('guitar_match_kind', '--')} "
                f"evidence={row.get('evidence_class', '--')}/{row.get('evidence_source', '--')}"
            )

    for relation, samples in sorted(examples_by_relation.items()):
        lines.append(f"{relation} examples")
        for row, label in samples:
            lines.append(
                "  "
                f"{row.get('recording_id', '')} status={row.get('status', '')} "
                f"expected={row.get('expected_chords', '')} got={row.get('guitar_chord', '--')} "
                f"extra={label} suffix={label_suffix(label)} "
                f"extra_pc={pitch_set_text(pitch_set(label))} "
                f"expected_pc={row.get('expected_pitch_classes', '--')} "
                f"match={row.get('guitar_match_kind', '--')} "
                f"evidence={row.get('evidence_class', '--')}/{row.get('evidence_source', '--')}"
            )

    for policy in prune_policies:
        lines.extend(summarize_prune_policy(rows, policy, examples))
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--examples", type=int, default=4)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--simulate-prune",
        action="append",
        choices=(
            "none",
            "primary",
            "primary-equivalent",
            "primary-equivalent-plain",
            "primary-equivalent-plain-observed-playable",
            "primary-same-root-equivalent",
            "observed-playable",
            "primary-equivalent-observed-playable",
        ),
        default=[],
        help="append simulated post-detection guitar chord label pruning metrics",
    )
    args = parser.parse_args()

    for line in summarize(
        pathlib.Path(args.path),
        max(0, args.examples),
        max(1, args.limit),
        args.simulate_prune,
    ):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
