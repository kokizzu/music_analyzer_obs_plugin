#!/usr/bin/env python3
"""Write a compact, reproducible real-note detection accuracy dashboard."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


EXPECTED_ROW = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}


def truthy(value: str) -> bool:
    return value.strip().lower() not in {"", "0", "false", "no"}


def load_samples(path: Path) -> dict[str, list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"sample_id", "family", "detected", "detected_expected_row", "first_row", "visual_first_row"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}")
        samples: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            samples[row["sample_id"]].append(row)
    if not samples:
        raise ValueError(f"{path}: no attribute rows")
    return samples


def metric_values(rows: list[dict[str, str]], expected_row: str) -> dict[str, bool]:
    return {
        "Any detected note": any(truthy(row["detected"]) for row in rows),
        "Expected instrument row": any(truthy(row["detected_expected_row"]) for row in rows),
        "Primary display row": any(row["first_row"] == expected_row for row in rows),
        "Visual primary row": any(row["visual_first_row"] == expected_row for row in rows),
    }


def fraction(value: int, total: int) -> str:
    percent = 100.0 * value / total if total else 0.0
    return f"{value} / {total} ({percent:.1f}%)"


def table_rows(samples: dict[str, list[dict[str, str]]]) -> list[tuple[str, int, int]]:
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    per_family: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for sample_rows in samples.values():
        family = sample_rows[0]["family"]
        expected = EXPECTED_ROW.get(family)
        if expected is None:
            continue
        for label, accurate in metric_values(sample_rows, expected).items():
            totals[label][1] += 1
            totals[label][0] += int(accurate)
            per_family[family][label][1] += 1
            per_family[family][label][0] += int(accurate)

    result = [(label, values[0], values[1]) for label, values in totals.items()]
    for family in sorted(per_family):
        for label, values in per_family[family].items():
            result.append((f"{family.title()} — {label}", values[0], values[1]))
    return result


def family_metric_rows(samples: dict[str, list[dict[str, str]]], family: str) -> list[tuple[str, int, int]]:
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    expected = EXPECTED_ROW[family]
    for sample_rows in samples.values():
        if sample_rows[0]["family"] != family:
            continue
        for label, accurate in metric_values(sample_rows, expected).items():
            totals[label][1] += 1
            totals[label][0] += int(accurate)
    return [(label, values[0], values[1]) for label, values in totals.items()]


def integer(row: dict[str, str], field: str) -> int:
    try:
        return int(row[field])
    except (KeyError, ValueError):
        return 0


def chord_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected_chords", "chord_hit", "expected_pitch_class_count", "guitar_note_hits"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing required chord columns: {', '.join(sorted(missing))}")
    expected = [row for row in rows if row["expected_chords"] not in {"", "--"}]
    chord_hits = sum(truthy(row["chord_hit"]) for row in expected)
    expected_pitch_classes = sum(integer(row, "expected_pitch_class_count") for row in expected)
    pitch_hits = sum(min(integer(row, "guitar_note_hits"), integer(row, "expected_pitch_class_count")) for row in expected)
    name = path.stem.replace("_attributes", "").replace("_", " ").title()
    return [
        (f"{name} — exact chord windows", chord_hits, len(expected)),
        (f"{name} — expected guitar pitch classes", pitch_hits, expected_pitch_classes),
    ]


BACH10_GATE_RE = re.compile(
    r"note hits (?P<note_hits>\d+)/(?P<note_total>\d+), chord hits "
    r"(?P<chord_hits>\d+)/(?P<chord_total>\d+).*?simple chord hits "
    r"(?P<simple_hits>\d+)/(?P<simple_total>\d+)"
)

MUSICNET_GATE_RE = re.compile(
	r"analyzer_musicnet: \d+/\d+ checks (?:passed|failed) \(recordings "
	r"(?P<recordings_done>\d+)/(?P<recordings_total>\d+), windows \d+.*?note hits "
    r"(?P<note_hits>\d+)/(?P<note_total>\d+), chord hits "
    r"(?P<chord_hits>\d+)/(?P<chord_total>\d+).*?simple chord hits "
    r"(?P<simple_hits>\d+)/(?P<simple_total>\d+)"
)

DRUM_PRIMARY_MATRIX_RE = re.compile(
    r"analyzer_drum_samples: primary matrix\n(?P<rows>(?:\s+expected "
    r"(?:kick|snare|hihat|crash|tom|ride|rim)\s+[^\n]+\n)+)"
)
DRUM_PRIMARY_ROW_RE = re.compile(r"^\s*expected (?P<expected>\w+)\s+(?P<counts>.+)$")
DRUM_PRIMARY_COUNT_RE = re.compile(r"(?P<instrument>\w+)=(?P<count>\d+)")


def bach10_gate_rows(paths: list[Path]) -> list[tuple[str, int, int]]:
    totals = {name: [0, 0] for name in ("note", "chord", "simple")}
    for path in paths:
        match = BACH10_GATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
        if match is None:
            raise ValueError(f"{path}: missing Bach10 MusicNet gate summary")
        for name in totals:
            totals[name][0] += int(match[f"{name}_hits"])
            totals[name][1] += int(match[f"{name}_total"])
    return [
        ("Bach10-mf0-synth — expected note slots", *totals["note"]),
        ("Bach10-mf0-synth — exact chord windows", *totals["chord"]),
        ("Bach10-mf0-synth — simplified chord windows", *totals["simple"]),
    ]


def musicnet_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    match = MUSICNET_GATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing MusicNet gate summary")
    return [
        ("MusicNet real mixes — recordings evaluated", int(match["recordings_done"]), int(match["recordings_total"])),
        ("MusicNet real mixes — expected pitch classes", int(match["note_hits"]), int(match["note_total"])),
        ("MusicNet real mixes — exact chord windows", int(match["chord_hits"]), int(match["chord_total"])),
        ("MusicNet real mixes — simplified chord windows", int(match["simple_hits"]), int(match["simple_total"])),
    ]


def drum_primary_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    match = DRUM_PRIMARY_MATRIX_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing full-drum primary matrix")
    result: list[tuple[str, int, int]] = []
    for line in match["rows"].splitlines():
        row = DRUM_PRIMARY_ROW_RE.match(line)
        if row is None:
            continue
        counts = {
            count["instrument"]: int(count["count"])
            for count in DRUM_PRIMARY_COUNT_RE.finditer(row["counts"])
        }
        expected = row["expected"]
        if expected not in counts:
            raise ValueError(f"{path}: missing primary count for {expected}")
        result.append((f"Full drum gate — primary {expected}", counts[expected], sum(counts.values())))
    if len(result) != 7:
        raise ValueError(f"{path}: expected seven full-drum primary rows, got {len(result)}")
    return result


def render(
    input_path: Path,
    chord_inputs: list[Path] | None = None,
    vocal_full_mix_input: Path | None = None,
    bach10_gate_outputs: list[Path] | None = None,
    musicnet_gate_output: Path | None = None,
    drum_gate_output: Path | None = None,
) -> str:
    samples = load_samples(input_path)
    lines = [
        "# Real-audio detection accuracy",
        "",
        "This dashboard is generated from the deterministic full-mix real-note attribute TSV. "
        "Each denominator is the number of unique audio samples; a sample is accurate when any "
        "analyzed buffer meets the stated condition.",
        "",
        f"Source: `{input_path.as_posix()}`",
        "",
        "| Metric | Accurate / total | Remaining |",
        "| --- | ---: | ---: |",
    ]
    for label, accurate, total in table_rows(samples):
        lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if vocal_full_mix_input is not None:
        vocal_samples = load_samples(vocal_full_mix_input)
        vocal_rows = family_metric_rows(vocal_samples, "vocals")
        if vocal_rows:
            lines.extend(
                [
                    "",
                    "## Vocadito full-mix vocal routing",
                    "",
                    "This separate real-vocal corpus measures how often the vocal row remains visible "
                    "when the analyzer also proposes instrumental rows.",
                    "",
                    f"Source: `{vocal_full_mix_input.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                ]
            )
            for label, accurate, total in vocal_rows:
                lines.append(
                    f"| Vocadito vocals — {label} | {fraction(accurate, total)} | {total - accurate} |"
                )
    cached_chord_inputs = chord_inputs or []
    if cached_chord_inputs:
        lines.extend(
            [
                "",
                "## Cached isolated-guitar chord gates",
                "",
                "These rows count expected labeled chord-analysis windows (not full-mix samples). "
                "They are included only when the corresponding cached attribute TSV exists.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for chord_input in cached_chord_inputs:
            for label, accurate, total in chord_gate_rows(chord_input):
                lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if bach10_gate_outputs:
        lines.extend(
            [
                "",
                "## Bach10-mf0-synth multitrack stress gate",
                "",
                "This F0-derived, resynthesized four-part corpus is reported separately from "
                "real-recording metrics. It measures expected active note slots and global chord windows.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in bach10_gate_rows(bach10_gate_outputs):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if musicnet_gate_output is not None:
        lines.extend(
            [
                "",
                "## MusicNet real-mixture gate",
                "",
                "This open CC-BY corpus measures real classical mixtures; unlike Bach10, it has no isolated stems.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in musicnet_gate_rows(musicnet_gate_output):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if drum_gate_output is not None:
        lines.extend(
            [
                "",
                "## Full drum primary-classification gate",
                "",
                "These rows count one-shot samples by the instrument shown as the primary drum. "
                "The latest completed full gate is reported even when a threshold fails, so its "
                "remaining classifications remain visible.",
                "",
                f"Source: `{drum_gate_output.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in drum_primary_gate_rows(drum_gate_output):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    lines.extend(
        [
            "",
            "Refresh with `make update-detection-accuracy-report`. Whenever a verified detection "
            "metric changes, update this report in the same commit.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--chord-input", action="append", type=Path, default=[])
    parser.add_argument("--vocal-full-mix-input", type=Path)
    parser.add_argument("--bach10-gate-output", action="append", type=Path, default=[])
    parser.add_argument("--musicnet-gate-output", type=Path)
    parser.add_argument("--drum-gate-output", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        rendered = render(
            args.input, args.chord_input, args.vocal_full_mix_input, args.bach10_gate_output,
            args.musicnet_gate_output, args.drum_gate_output
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"detection_accuracy_report: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
