#!/usr/bin/env python3
"""Summarize prepared analyzer sample manifests for detector coverage audits."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import sys


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class ManifestSummary:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.rows = 0
        self.audio_rows = 0
        self.note_rows = 0
        self.families: collections.Counter[str] = collections.Counter()
        self.categories: collections.Counter[str] = collections.Counter()
        self.sources: collections.Counter[str] = collections.Counter()
        self.midi_values: list[int] = []
        self.duration_seconds: list[float] = []

    def add_midi(self, value: str) -> None:
        try:
            self.midi_values.append(int(float(value)))
        except ValueError:
            return

    def add_duration(self, value: str) -> None:
        try:
            duration = float(value)
        except ValueError:
            return
        if duration > 0.0:
            self.duration_seconds.append(duration)

    def add_note_duration(self, start: str, end: str) -> None:
        try:
            start_seconds = float(start)
            end_seconds = float(end)
        except ValueError:
            return
        duration = end_seconds - start_seconds
        if duration > 0.0:
            self.duration_seconds.append(duration)


def midi_label(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def compact_counter(counter: collections.Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    parts = []
    for key, value in counter.most_common(limit):
        label = key if key else "(blank)"
        parts.append(f"{label}={value}")
    remaining = len(counter) - len(parts)
    if remaining > 0:
        parts.append(f"+{remaining}")
    return ",".join(parts)


def infer_family(path: pathlib.Path) -> str:
    name = path.as_posix().lower()
    if "drum" in name or "egmd" in name:
        return "drums"
    if "bass" in name:
        return "bass"
    if "guitar" in name or "gaps" in name or "egfx" in name:
        return "guitar"
    if "piano" in name or "maestro" in name or "maps" in name:
        return "piano"
    if "vocal" in name or "vocadito" in name:
        return "vocals"
    if "string" in name or "orchestra" in name or "philharmonia" in name:
        return "other"
    return "unknown"


def parse_header_manifest(path: pathlib.Path, header: list[str], rows: list[list[str]]) -> ManifestSummary:
    summary = ManifestSummary(path)
    columns = {name: index for index, name in enumerate(header)}

    def field(row: list[str], name: str) -> str:
        index = columns.get(name)
        if index is None or index >= len(row):
            return ""
        return row[index]

    for row in rows:
        summary.rows += 1
        family = field(row, "family") or field(row, "nsynth_family")
        category = field(row, "category")
        inferred_family = infer_family(path)
        if inferred_family == "drums":
            if category:
                summary.categories[category] += 1
            elif family:
                summary.categories[family] += 1
            summary.families["drums"] += 1
            source = field(row, "source")
            if source:
                summary.sources[source] += 1
            midi = field(row, "midi")
            if midi:
                summary.add_midi(midi)
            duration = field(row, "duration_seconds")
            if duration:
                summary.add_duration(duration)
            continue
        if category:
            summary.categories[category] += 1
        if family:
            summary.families[family] += 1
        elif category:
            summary.families["drums"] += 1
        else:
            summary.families[inferred_family] += 1
        source = field(row, "source")
        if source:
            summary.sources[source] += 1
        midi = field(row, "midi")
        if midi:
            summary.add_midi(midi)
        duration = field(row, "duration_seconds")
        if duration:
            summary.add_duration(duration)
    return summary


def parse_event_manifest(path: pathlib.Path, rows: list[list[str]]) -> ManifestSummary:
    summary = ManifestSummary(path)
    family = infer_family(path)
    for row in rows:
        if not row:
            continue
        tag = row[0]
        if tag == "AUDIO":
            summary.audio_rows += 1
            summary.rows += 1
            summary.families[family] += 1
        elif tag == "NOTE":
            summary.note_rows += 1
            summary.rows += 1
            summary.families[family] += 1
            if len(row) >= 5:
                summary.add_midi(row[4])
            if len(row) >= 4:
                summary.add_note_duration(row[2], row[3])
        elif tag == "CHORD":
            summary.rows += 1
            summary.families[family] += 1
    return summary


def read_data_rows(path: pathlib.Path) -> list[list[str]]:
    rows: list[list[str]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as file:
        for row in csv.reader(file, delimiter="\t"):
            if not row or not any(cell.strip() for cell in row):
                continue
            if row[0].startswith("#"):
                continue
            rows.append(row)
    return rows


def parse_manifest(path: pathlib.Path) -> ManifestSummary:
    rows = read_data_rows(path)
    if not rows:
        return ManifestSummary(path)
    first = rows[0]
    if first and first[0] in {"AUDIO", "NOTE", "CHORD"}:
        return parse_event_manifest(path, rows)
    return parse_header_manifest(path, first, rows[1:])


def midi_range(values: list[int]) -> str:
    if not values:
        return "--"
    low = min(values)
    high = max(values)
    return f"{low}-{high}({midi_label(low)}-{midi_label(high)})"


def duration_range(values: list[float]) -> str:
    if not values:
        return "--"
    return f"{min(values):.3f}-{max(values):.3f}s"


def print_summary(summary: ManifestSummary, top_sources: int) -> None:
    print(
        "sample_manifest "
        f"path={summary.path} "
        f"rows={summary.rows} "
        f"audio={summary.audio_rows} "
        f"notes={summary.note_rows} "
        f"families={compact_counter(summary.families, top_sources)} "
        f"categories={compact_counter(summary.categories, top_sources)} "
        f"sources={compact_counter(summary.sources, top_sources)} "
        f"midi={midi_range(summary.midi_values)} "
        f"duration={duration_range(summary.duration_seconds)}"
    )


def merge_summaries(summaries: list[ManifestSummary]) -> ManifestSummary:
    total = ManifestSummary(pathlib.Path("<total>"))
    for summary in summaries:
        total.rows += summary.rows
        total.audio_rows += summary.audio_rows
        total.note_rows += summary.note_rows
        total.families.update(summary.families)
        total.categories.update(summary.categories)
        total.sources.update(summary.sources)
        total.midi_values.extend(summary.midi_values)
        total.duration_seconds.extend(summary.duration_seconds)
    return total


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="*", type=pathlib.Path)
    parser.add_argument("--top-sources", type=int, default=5)
    args = parser.parse_args(argv)

    unique_paths = []
    seen: set[pathlib.Path] = set()
    for path in args.manifests:
        normalized = path.resolve()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_paths.append(path)

    summaries: list[ManifestSummary] = []
    for path in unique_paths:
        if not path.exists():
            print(f"sample_manifest skipped missing={path}", file=sys.stderr)
            continue
        summary = parse_manifest(path)
        summaries.append(summary)
        print_summary(summary, args.top_sources)

    total = merge_summaries(summaries)
    print(
        "sample_manifest_total "
        f"manifests={len(summaries)} "
        f"rows={total.rows} "
        f"audio={total.audio_rows} "
        f"notes={total.note_rows} "
        f"families={compact_counter(total.families, args.top_sources)} "
        f"categories={compact_counter(total.categories, args.top_sources)} "
        f"sources={compact_counter(total.sources, args.top_sources)} "
        f"midi={midi_range(total.midi_values)} "
        f"duration={duration_range(total.duration_seconds)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
