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


def summarize(path: pathlib.Path, examples: int, limit: int) -> list[str]:
    rows = [derive_guitarset_row(row) for row in load_rows(path) if row.get("recording_id")]
    component_counter: collections.Counter[str] = collections.Counter()
    suffix_counter: collections.Counter[str] = collections.Counter()
    relation_counter: collections.Counter[str] = collections.Counter()
    hit_component_counter: collections.Counter[str] = collections.Counter()
    hit_suffix_counter: collections.Counter[str] = collections.Counter()
    hit_relation_counter: collections.Counter[str] = collections.Counter()
    subset_counter: collections.Counter[str] = collections.Counter()
    hit_subset_counter: collections.Counter[str] = collections.Counter()
    rows_with_extras = 0
    hit_rows_with_extras = 0
    examples_by_relation: dict[str, list[tuple[dict[str, str], str]]] = collections.defaultdict(list)
    subset_examples: list[tuple[dict[str, str], str, str]] = []

    for row in rows:
        extras = row_extra_components(row)
        if not extras:
            continue
        rows_with_extras += 1
        if row.get("status") == "chord_hit":
            hit_rows_with_extras += 1
        for label, suffix, relation, subset_relation in extras:
            component_counter[label] += 1
            suffix_counter[suffix] += 1
            relation_counter[relation] += 1
            if len(examples_by_relation[relation]) < examples:
                examples_by_relation[relation].append((row, label))
            if subset_relation != "--":
                subset_counter[subset_relation] += 1
                if len(subset_examples) < examples:
                    subset_examples.append((row, label, subset_relation))
            if row.get("status") == "chord_hit":
                hit_component_counter[label] += 1
                hit_suffix_counter[suffix] += 1
                hit_relation_counter[relation] += 1
                if subset_relation != "--":
                    hit_subset_counter[subset_relation] += 1

    total_components = sum(component_counter.values())
    hit_components = sum(hit_component_counter.values())
    lines = [
        f"guitar chord extra components rows={rows_with_extras}/{len(rows)} "
        f"components={total_components} hit_rows={hit_rows_with_extras} hit_components={hit_components}",
        f"component labels {compact(component_counter, limit)}",
        f"component suffixes {compact(suffix_counter, limit)}",
        f"component relations {compact(relation_counter, limit)}",
        f"hit component labels {compact(hit_component_counter, limit)}",
        f"hit component suffixes {compact(hit_suffix_counter, limit)}",
        f"hit component relations {compact(hit_relation_counter, limit)}",
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
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/guitar_chord_mix_attributes.tsv")
    parser.add_argument("--examples", type=int, default=4)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    for line in summarize(pathlib.Path(args.path), max(0, args.examples), max(1, args.limit)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
