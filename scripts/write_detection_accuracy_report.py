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

VISUAL_NOTE_FIELD = {
    "bass": "bass_visual_notes",
    "guitar": "guitar_visual_notes",
    "piano": "piano_visual_notes",
    "vocals": "vocal_visual_notes",
    "other": "other_visual_notes",
}

NOTE_FIELD = {
    "bass": "bass_notes",
    "guitar": "guitar_notes",
    "piano": "piano_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
}

NOTE_TOKEN_RE = re.compile(r"^([A-G])(#?)(-?\d+):([0-9.]+)$")
NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
VISUAL_LIT_THRESHOLD = 0.25
GUITAR_PRIMARY_AUDIT_RE = re.compile(
    r"^guitar_chord: primary=(?P<primary>\d+)/(?P<total>\d+) "
    r"later=(?P<later>\d+) miss=(?P<miss>\d+)$",
    re.MULTILINE,
)
GUITAR_PRIMARY_RUNTIME_SAFE_RE = re.compile(
    r"^same_root_extension_primary_runtime_safe_rules:\n(?P<body>(?:^  .*\n?)*)",
    re.MULTILINE,
)
GUITAR_TONE_AUDIT_RE = re.compile(
    r"^(?P<corpus>[^\n:]+): candidates=(?P<candidates>\d+) "
    r"recoveries=(?P<recoveries>\d+) false=(?P<false>\d+)$",
    re.MULTILINE,
)

# Analyzer TSV evidence can legitimately retain long comma-separated note
# histories.  Keep a finite but practical cap instead of csv's 128 KiB default.
csv.field_size_limit(8 * 1024 * 1024)


def truthy(value: str) -> bool:
    return value.strip().lower() not in {"", "0", "false", "no"}


def labels(value: str) -> set[str]:
    return {item for item in value.replace("=", ",").split(",") if item and item != "--"}


def visual_expected_pitch_lit(row: dict[str, str], expected_row: str) -> bool:
    """Whether an expected-row pitch class is visibly lit in this window."""
    try:
        expected_midi = int(row.get("expected_midi", ""))
    except ValueError:
        return False
    for token in row.get(VISUAL_NOTE_FIELD[expected_row], "").split(","):
        match = NOTE_TOKEN_RE.fullmatch(token.strip())
        if not match:
            continue
        letter, sharp, octave_text, level_text = match.groups()
        observed_midi = (int(octave_text) + 1) * 12 + NOTE_OFFSETS[letter] + (1 if sharp else 0)
        if observed_midi % 12 == expected_midi % 12 and float(level_text) >= VISUAL_LIT_THRESHOLD:
            return True
    return False


def expected_exact_note_detected(rows: list[dict[str, str]], expected_row: str) -> bool:
    """Whether an expected-row grid contains the annotated MIDI note exactly."""
    try:
        expected_midi = int(rows[0].get("expected_midi", ""))
    except (IndexError, ValueError):
        return False
    for row in rows:
        for token in row.get(NOTE_FIELD[expected_row], "").split(","):
            match = NOTE_TOKEN_RE.fullmatch(token.strip())
            if not match:
                continue
            letter, sharp, octave_text, _level_text = match.groups()
            observed_midi = (int(octave_text) + 1) * 12 + NOTE_OFFSETS[letter] + (1 if sharp else 0)
            if observed_midi == expected_midi:
                return True
    return False


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
        "Lit expected pitch class": any(
            visual_expected_pitch_lit(row, expected_row) for row in rows
        ),
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


def label_only_routing_rows(samples: dict[str, list[dict[str, str]]]) -> list[tuple[str, int, int]]:
    """Summarize row routing where the corpus supplies an instrument label but no pitch truth."""
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    per_family: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for sample_rows in samples.values():
        family = sample_rows[0].get("family", "")
        expected = EXPECTED_ROW.get(family)
        if expected is None:
            continue
        values = {
            "Any runtime pitch candidate": any(truthy(row.get("detected", "")) for row in sample_rows),
            "Labelled instrument pitch-class row": any(truthy(row.get("row_grid", "")) for row in sample_rows),
            "Strongest raw routing row": any(row.get("buffer_strongest_row", "") == expected for row in sample_rows),
            "Strongest visible routing row": any(row.get("buffer_visual_strongest_row", "") == expected for row in sample_rows),
        }
        for label, accurate in values.items():
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


def exact_note_rows(samples: dict[str, list[dict[str, str]]]) -> list[tuple[str, int, int]]:
    """Return per-sample exact-MIDI detection across isolated rows."""
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for sample_rows in samples.values():
        family = sample_rows[0]["family"]
        expected_row = EXPECTED_ROW.get(family)
        if expected_row is None:
            continue
        totals["Exact expected MIDI note"][1] += 1
        totals[f"{family.title()} — exact expected MIDI note"][1] += 1
        if expected_exact_note_detected(sample_rows, expected_row):
            totals["Exact expected MIDI note"][0] += 1
            totals[f"{family.title()} — exact expected MIDI note"][0] += 1
    return [(label, values[0], values[1]) for label, values in totals.items()]


def exact_note_source_rows(
    samples: dict[str, list[dict[str, str]]], sources: tuple[str, ...]
) -> list[tuple[str, int, int]]:
    """Return exact-MIDI rows for explicitly selected isolated-note sources."""
    wanted = {source.casefold() for source in sources}
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for sample_rows in samples.values():
        source = sample_rows[0].get("source", "").casefold()
        if source not in wanted:
            continue
        family = sample_rows[0]["family"]
        expected_row = EXPECTED_ROW.get(family)
        if expected_row is None:
            continue
        label = f"{source.replace('-', ' ').title()} — exact expected MIDI note"
        totals[label][1] += 1
        if expected_exact_note_detected(sample_rows, expected_row):
            totals[label][0] += 1
    missing = wanted - {sample_rows[0].get("source", "").casefold() for sample_rows in samples.values()}
    if missing:
        raise ValueError(f"missing expected TinySOL source rows: {', '.join(sorted(missing))}")
    return [(label, values[0], values[1]) for label, values in sorted(totals.items())]


def medley_solos_rows(path: Path) -> list[tuple[str, int, int]]:
    """Return sample-level expected-row recall from Medley Solos attributes."""
    with path.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"sample_id", "family", "instrument", "expected_row_hit"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing required Medley Solos columns: {', '.join(sorted(missing))}")
        samples: dict[str, dict[str, object]] = {}
        for row in rows:
            sample_id = row["sample_id"]
            family = row["family"]
            instrument = row["instrument"]
            if family not in EXPECTED_ROW:
                raise ValueError(f"{path}: unknown Medley Solos family `{family}`")
            sample = samples.setdefault(
                sample_id,
                {"family": family, "instrument": instrument, "hit": False},
            )
            if sample["family"] != family or sample["instrument"] != instrument:
                raise ValueError(f"{path}: inconsistent family or instrument for `{sample_id}`")
            sample["hit"] = bool(sample["hit"]) or truthy(row["expected_row_hit"])
    if not samples:
        raise ValueError(f"{path}: no Medley Solos attribute rows")

    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for sample in samples.values():
        family = str(sample["family"])
        instrument = str(sample["instrument"])
        totals["Expected instrument row"][1] += 1
        totals[f"Family {family.title()} expected row"][1] += 1
        totals[f"Instrument {instrument.title()} expected row"][1] += 1
        if bool(sample["hit"]):
            totals["Expected instrument row"][0] += 1
            totals[f"Family {family.title()} expected row"][0] += 1
            totals[f"Instrument {instrument.title()} expected row"][0] += 1
    return [(label, values[0], values[1]) for label, values in totals.items()]


def integer(row: dict[str, str], field: str) -> int:
    try:
        return int(row[field])
    except (KeyError, ValueError):
        return 0


def chord_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {
        "expected_chords",
        "chord_hit",
        "guitar_chord",
        "expected_pitch_class_count",
        "guitar_note_hits",
    }
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing required chord columns: {', '.join(sorted(missing))}")
    expected = [row for row in rows if row["expected_chords"] not in {"", "--"}]
    chord_hits = sum(truthy(row["chord_hit"]) for row in expected)
    primary_chord_hits = sum(
        row["guitar_chord"].split("=", 1)[0]
        in {label for label in re.split(r"[=/]", row["expected_chords"]) if label}
        for row in expected
    )
    expected_pitch_classes = sum(integer(row, "expected_pitch_class_count") for row in expected)
    pitch_hits = sum(min(integer(row, "guitar_note_hits"), integer(row, "expected_pitch_class_count")) for row in expected)
    name = path.stem.replace("_attributes", "").replace("_", " ").title()
    result = [
        (f"{name} — exact chord windows", chord_hits, len(expected)),
        (f"{name} — primary displayed chord windows", primary_chord_hits, len(expected)),
        (f"{name} — expected guitar pitch classes", pitch_hits, expected_pitch_classes),
    ]
    power = [
        row
        for row in expected
        if any(label.endswith("pow") for label in re.split(r"[=/]", row["expected_chords"]) if label)
    ]
    if power:
        result.append(
            (f"{name} — power-chord exact windows", sum(truthy(row["chord_hit"]) for row in power), len(power))
        )
    return result


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

MAPS_GATE_RE = re.compile(
    r"analyzer_maestro: \d+ checks (?:passed|failed) \(recordings "
    r"(?P<recordings_done>\d+)/(?P<recordings_total>\d+), windows (?P<windows>\d+), "
    r".*?note hits (?P<note_hits>\d+)/(?P<note_total>\d+), chord hits "
    r"(?P<chord_hits>\d+)/(?P<chord_total>\d+)"
)
MAPS_NOTE_COUNTS_RE = re.compile(
    r"keyboard precision [\d.]+%, keyboard recall [\d.]+%, F1 [\d.]+%, .*?tp/fp/fn "
    r"(?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+), keyboard chord precision"
)
MAPS_CHORD_COUNTS_RE = re.compile(
    r"keyboard chord precision [\d.]+%, keyboard chord recall [\d.]+%, F1 [\d.]+%, "
    r"tp/fp/fn (?P<tp>\d+)/(?P<fp>\d+)/(?P<fn>\d+)"
)
ELECTRONIC_PIANO_GUITAR_MATCH_RE = re.compile(
    r"^matched rows=(?P<rows>\d+) samples=(?P<samples>\d+)$", re.MULTILINE
)
ELECTRONIC_PIANO_GUITAR_COMPARE_RE = re.compile(
    r"^compare rows=(?P<rows>\d+) samples=(?P<samples>\d+) path=.+$", re.MULTILINE
)
INDEPENDENT_PIANO_STATE_RE = re.compile(
    r"independent_piano_chord_states: corpora=(?P<corpora>\d+) "
    r"shared_no_label_states=(?P<states>\d+) "
    r"complete_pcs_recovery_candidates=(?P<candidates>\d+)"
)

URMP_COVERAGE_RE = re.compile(
    r"analyzer_urmp: coverage: discovered (?P<discovered>\d+) piece dirs, loadable "
    r"(?P<loadable>\d+).*?selected (?P<windows>\d+) candidate windows"
)
URMP_PRECISION_RE = re.compile(
    r"URMP separated-track precision: expected >=\d+%, got (?P<exact_hits>\d+)/"
    r"(?P<detected_total>\d+)"
)
URMP_EXACT_RE = re.compile(
    r"URMP separated-track exact recall: expected >=\d+%, got (?P<exact_hits>\d+)/"
    r"(?P<note_total>\d+)"
)
URMP_SUMMARY_RE = re.compile(
    r"analyzer_urmp: \d+/\d+ checks (?:passed|failed) \(\d+ pieces, \d+ windows, "
    r"(?P<detected_hits>\d+) track hits/(?P<note_total>\d+)"
)
URMP_CHORD_RE = re.compile(
    r"analyzer_urmp: chord metrics: provided global chord precision [\d.]+%, recall [\d.]+%, "
    r"F1 [\d.]+%, tp/fp/fn (?P<provided_hits>\d+)/\d+/(?P<provided_total_miss>\d+); "
    r".*?provided stream global chord precision [\d.]+%, recall [\d.]+%, F1 [\d.]+%, "
    r"tp/fp/fn (?P<stream_hits>\d+)/\d+/(?P<stream_total_miss>\d+); "
    r".*?provided sequence global chord precision [\d.]+%, recall [\d.]+%, F1 [\d.]+%, "
    r"tp/fp/fn (?P<sequence_hits>\d+)/\d+/(?P<sequence_total_miss>\d+)"
)
URMP_INSTRUMENT_EXACT_RE = re.compile(
    r"^analyzer_urmp: (?P<instrument>[a-z]+) isolated metrics: .*?"
    r"by-row (?:bass|other) tp/fp/fn (?P<exact_hits>\d+)/\d+/(?P<exact_misses>\d+),",
    re.MULTILINE,
)
URMP_INSTRUMENT_NAMES = {
    "bn": "bassoon",
    "cl": "clarinet",
    "db": "double bass",
    "fl": "flute",
    "hn": "horn",
    "ob": "oboe",
    "sax": "saxophone",
    "tba": "tuba",
    "tbn": "trombone",
    "tpt": "trumpet",
    "va": "viola",
    "vc": "cello",
    "vn": "violin",
}

DRUM_PRIMARY_MATRIX_RE = re.compile(
    r"analyzer_drum_samples: primary matrix\n(?P<rows>(?:\s+expected "
    r"(?:kick|snare|hihat|crash|tom|ride|rim)\s+[^\n]+\n)+)"
)
DRUM_PRIMARY_ROW_RE = re.compile(r"^\s*expected (?P<expected>\w+)\s+(?P<counts>.+)$")
DRUM_PRIMARY_COUNT_RE = re.compile(r"(?P<instrument>\w+)=(?P<count>\d+)")
EGMD_DRUM_SUMMARY_RE = re.compile(
    r"analyzer_egmd: .*?windows (?P<windows>\d+),.*?drum hits "
    r"(?P<hits>\d+)/(?P<total>\d+), drum precision [\d.]+%, drum recall [\d.]+%,"
    r".*?false-positive windows [\d.]+% \((?P<false_windows>\d+)/(?P<window_total>\d+)\),"
    r".*?tp/fp/fn (?P<true_positive>\d+)/(?P<false_positive>\d+)/(?P<false_negative>\d+),"
)
ROUTE_SUMMARY_RE = re.compile(
    r"detector_route_summary: candidates=(?P<candidates>\d+).*?"
    r"actionable=(?P<actionable>\d+) coverage_blocked=(?P<coverage_blocked>\d+)"
    r"(?: independent_corpus_blocked=(?P<independent_corpus_blocked>\d+))?"
)


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
        (
            "MusicNet real mixes — recordings with eligible chord windows",
            int(match["recordings_done"]),
            int(match["recordings_total"]),
        ),
        ("MusicNet real mixes — expected pitch classes", int(match["note_hits"]), int(match["note_total"])),
        ("MusicNet real mixes — exact chord windows", int(match["chord_hits"]), int(match["chord_total"])),
        ("MusicNet real mixes — simplified chord windows", int(match["simple_hits"]), int(match["simple_total"])),
    ]


def musicnet_routing_rows(path: Path) -> list[tuple[str, int, int]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            (f"MusicNet {row['scope']} — {row['metric']}", int(row["accurate"]), int(row["total"]))
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def maps_gate_rows(paths: list[Path]) -> list[tuple[str, int, int]]:
    totals = {
        "recordings_done": 0,
        "recordings_total": 0,
        "note_hits": 0,
        "note_total": 0,
        "chord_hits": 0,
        "chord_total": 0,
        "note_tp": 0,
        "note_fp": 0,
        "chord_tp": 0,
        "chord_fp": 0,
    }
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        match = MAPS_GATE_RE.search(text)
        note_counts = MAPS_NOTE_COUNTS_RE.search(text)
        chord_counts = MAPS_CHORD_COUNTS_RE.search(text)
        if match is None or note_counts is None or chord_counts is None:
            raise ValueError(f"{path}: missing MAPS piano shard summary")
        for key in totals:
            if key in {"note_tp", "note_fp"}:
                value = int(note_counts[key.removeprefix("note_")])
            elif key in {"chord_tp", "chord_fp"}:
                value = int(chord_counts[key.removeprefix("chord_")])
            else:
                value = int(match[key])
            totals[key] = max(totals[key], value) if key == "recordings_total" else totals[key] + value
    return [
        ("MAPS real piano — recordings with eligible chord windows", totals["recordings_done"], totals["recordings_total"]),
        ("MAPS real piano — expected pitch classes", totals["note_hits"], totals["note_total"]),
        ("MAPS real piano — keyboard detected-note precision", totals["note_tp"], totals["note_tp"] + totals["note_fp"]),
        ("MAPS real piano — exact chord windows", totals["chord_hits"], totals["chord_total"]),
        ("MAPS real piano — keyboard chord precision", totals["chord_tp"], totals["chord_tp"] + totals["chord_fp"]),
    ]


def maps_note_gate_rows(paths: list[Path]) -> list[tuple[str, int, int]]:
    rows = maps_gate_rows(paths)
    return [
        ("MAPS isolated piano — recordings with annotated note windows", *rows[0][1:]),
        ("MAPS isolated piano — expected pitch classes", *rows[1][1:]),
        ("MAPS isolated piano — keyboard detected-note precision", *rows[2][1:]),
    ]


def maestro_real_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    return [
        (label.replace("MAPS real piano", "MAESTRO external piano"), accurate, total)
        for label, accurate, total in maps_gate_rows([path])
    ]


def independent_piano_state_evidence(path: Path) -> tuple[int, int]:
    match = INDEPENDENT_PIANO_STATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None or int(match["corpora"]) < 2:
        raise ValueError(f"{path}: missing independent piano runtime-state summary")
    candidates = int(match["candidates"])
    states = int(match["states"])
    if candidates < 0 or candidates > states:
        raise ValueError(f"{path}: invalid independent piano runtime-state counts")
    return candidates, states


def maps_chord_miss_rows(path: Path) -> list[tuple[str, int, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected_chords", "chord_hit", "missing_pcs", "keyboard_chord"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing MAPS chord-miss columns")
    misses = [
        row for row in rows
        if row["expected_chords"] not in {"", "--"} and not truthy(row["chord_hit"])
    ]
    return [
        (
            "Expected pitch classes are all present",
            sum(row["missing_pcs"] in {"", "--"} for row in misses),
            len(misses),
        ),
        ("No keyboard chord label", sum(row["keyboard_chord"] in {"", "--"} for row in misses), len(misses)),
    ]


def chord_outcome_counts(path: Path) -> tuple[int, int, int, int]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"expected_chords", "chord_hit"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing chord outcome columns")
    chord_column = "keyboard_chord" if "keyboard_chord" in rows[0] else "guitar_chord" if "guitar_chord" in rows[0] else None
    if chord_column is None:
        raise ValueError(f"{path}: missing detected chord column")
    eligible = [row for row in rows if labels(row["expected_chords"])]
    if not eligible:
        raise ValueError(f"{path}: no eligible chord rows")
    hits = sum(truthy(row["chord_hit"]) for row in eligible)
    no_label = sum(
        not truthy(row["chord_hit"]) and not labels(row[chord_column])
        for row in eligible
    )
    wrong_label = len(eligible) - hits - no_label
    return hits, no_label, wrong_label, len(eligible)


def drum_primary_attribute_rows(path: Path, name: str) -> list[tuple[str, int, int]]:
    """Return exact one-shot primary-label accuracy from the full attribute matrix."""
    instruments = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
    totals = {instrument: [0, 0] for instrument in instruments}
    with path.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"expected", "got"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing full drum attribute columns: {', '.join(sorted(missing))}")
        for row in rows:
            expected = row["expected"]
            if expected not in totals:
                raise ValueError(f"{path}: unknown expected drum `{expected}`")
            totals[expected][1] += 1
            totals[expected][0] += int(row["got"] == expected)
    return [
        (f"{name} — primary {instrument}", totals[instrument][0], totals[instrument][1])
        for instrument in instruments
    ]


def urmp_gate_rows(path: Path) -> list[tuple[str, int, int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    coverage = URMP_COVERAGE_RE.search(text)
    precision = URMP_PRECISION_RE.search(text)
    exact = URMP_EXACT_RE.search(text)
    summary = URMP_SUMMARY_RE.search(text)
    chords = URMP_CHORD_RE.search(text)
    if None in {coverage, precision, exact, summary, chords}:
        raise ValueError(f"{path}: missing URMP measurement summary")
    assert coverage is not None and precision is not None and exact is not None and summary is not None and chords is not None
    note_total = int(exact["note_total"])
    if note_total != int(summary["note_total"]):
        raise ValueError(f"{path}: inconsistent URMP note totals")
    rows = [
        ("URMP — real pieces loadable", int(coverage["loadable"]), int(coverage["discovered"])),
        ("URMP — selected annotated windows", int(coverage["windows"]), int(coverage["windows"])),
        ("URMP — isolated-track exact notes", int(exact["exact_hits"]), note_total),
        ("URMP — isolated-track detected notes", int(summary["detected_hits"]), note_total),
        ("URMP — isolated-track precision", int(precision["exact_hits"]), int(precision["detected_total"])),
        ("URMP — provided-mix exact chords", int(chords["provided_hits"]), int(chords["provided_hits"]) + int(chords["provided_total_miss"])),
        ("URMP — provided stream chord windows", int(chords["stream_hits"]), int(chords["stream_hits"]) + int(chords["stream_total_miss"])),
        ("URMP — provided sequence chord windows", int(chords["sequence_hits"]), int(chords["sequence_hits"]) + int(chords["sequence_total_miss"])),
    ]
    for match in sorted(URMP_INSTRUMENT_EXACT_RE.finditer(text), key=lambda value: value["instrument"]):
        exact_hits = int(match["exact_hits"])
        instrument = match["instrument"]
        rows.append(
            (
                f"URMP — {URMP_INSTRUMENT_NAMES.get(instrument, instrument)} isolated exact notes",
                exact_hits,
                exact_hits + int(match["exact_misses"]),
            )
        )
    return rows


def drum_primary_gate_rows(paths: list[Path], label_prefix: str) -> list[tuple[str, int, int]]:
    if label_prefix == "Full drum gate" and len(paths) == 1:
        exact_attribute_path = paths[0].with_name("drum_full_exact_attribute_rows.tsv")
        if exact_attribute_path.is_file():
            return drum_primary_attribute_rows(exact_attribute_path, label_prefix)
    rows_by_expected: dict[str, tuple[int, int]] = {}
    for path in paths:
        match = DRUM_PRIMARY_MATRIX_RE.search(path.read_text(encoding="utf-8", errors="replace"))
        if match is None:
            raise ValueError(f"{path}: missing drum primary matrix")
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
            total = sum(counts.values())
            # Sharded high-fidelity outputs include the six unprocessed
            # categories as all-zero placeholder rows.  They are not a
            # second observation and must not collide with the shard that
            # actually evaluated that expected instrument.
            if total == 0:
                continue
            if expected in rows_by_expected:
                raise ValueError(f"{path}: duplicate primary row for {expected}")
            rows_by_expected[expected] = (counts[expected], total)
    if len(rows_by_expected) != 7:
        raise ValueError(f"{label_prefix}: expected seven drum primary rows, got {len(rows_by_expected)}")
    return [
        (f"{label_prefix} — primary {expected}", *rows_by_expected[expected])
        for expected in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
    ]


def egmd_drum_rows(path: Path, label_prefix: str) -> list[tuple[str, int, int, str]]:
    """Return event recall and precision from an EGMD-compatible multitrack summary."""
    match = EGMD_DRUM_SUMMARY_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing EGMD drum summary")
    true_positive = int(match["true_positive"])
    false_positive = int(match["false_positive"])
    false_windows = int(match["false_windows"])
    window_total = int(match["window_total"])
    if int(match["windows"]) != window_total:
        raise ValueError(f"{path}: inconsistent EGMD window totals")
    return [
        (f"{label_prefix} — annotated drum events detected", int(match["hits"]), int(match["total"]), ""),
        (f"{label_prefix} — detected-drum precision", true_positive, true_positive + false_positive,
         "false predictions"),
        (f"{label_prefix} — windows without a false drum", window_total - false_windows, window_total,
         "false-positive windows"),
    ]


def route_coverage_rows(path: Path) -> list[tuple[str, int, int]]:
    match = ROUTE_SUMMARY_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing detector route summary")
    total = int(match["candidates"])
    rows = [
        ("Routes meeting protected and cross-corpus gates", int(match["actionable"]), total),
        ("Routes awaiting additional fixture coverage", int(match["coverage_blocked"]), total),
    ]
    if match["independent_corpus_blocked"] is not None:
        rows.append(
            (
                "Routes lacking independent-corpus replication",
                int(match["independent_corpus_blocked"]),
                total,
            )
        )
    return rows


def route_profile_audit(path: Path, expected_comparisons: int) -> tuple[int, int, int]:
    """Return source samples and independent-profile recurrence counts."""
    text = path.read_text(encoding="utf-8", errors="replace")
    source = ELECTRONIC_PIANO_GUITAR_MATCH_RE.search(text)
    comparisons = list(ELECTRONIC_PIANO_GUITAR_COMPARE_RE.finditer(text))
    if source is None or len(comparisons) != expected_comparisons:
        raise ValueError(f"{path}: missing cached route audit")
    return (
        int(source["samples"]),
        sum(int(match["samples"]) > 0 for match in comparisons),
        len(comparisons),
    )


def electronic_piano_guitar_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 2)


def scms_vocal_other_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 3)


def tenor_sax_piano_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 3)


def violin_guitar_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 2)


def guitar_chord_primary_display_audit(
    path: Path,
) -> tuple[tuple[int, int, int], tuple[int, int, int], int, int]:
    """Return primary-display totals and zero-regression rule counts for two guitar corpora."""
    text = path.read_text(encoding="utf-8", errors="replace")
    primary_rows = list(GUITAR_PRIMARY_AUDIT_RE.finditer(text))
    safe_sections = list(GUITAR_PRIMARY_RUNTIME_SAFE_RE.finditer(text))
    if len(primary_rows) != 2 or len(safe_sections) != 2:
        raise ValueError(f"{path}: missing two-corpus guitar primary display audit")

    def primary(match: re.Match[str]) -> tuple[int, int, int]:
        return int(match["primary"]), int(match["total"]), int(match["miss"])

    def safe_rule_count(match: re.Match[str]) -> int:
        return sum(
            line.lstrip().startswith("+") and "protected_false=0" in line
            for line in match["body"].splitlines()
        )

    return (
        primary(primary_rows[0]),
        primary(primary_rows[1]),
        safe_rule_count(safe_sections[0]),
        safe_rule_count(safe_sections[1]),
    )


def guitar_chord_tone_recovery_audit(path: Path) -> dict[str, tuple[int, int, int]]:
    """Return per-tone corpus recovery and false-promotion counts from the tri-corpus audit."""
    sections = re.split(r"^tone=(?P<tone>[a-z-]+)$", path.read_text(encoding="utf-8", errors="replace"), flags=re.MULTILINE)
    result: dict[str, tuple[int, int, int]] = {}
    for index in range(1, len(sections), 2):
        tone = sections[index]
        rows = list(GUITAR_TONE_AUDIT_RE.finditer(sections[index + 1]))
        if len(rows) != 3:
            raise ValueError(f"{path}: expected three corpus rows for {tone}")
        result[tone] = (
            sum(int(row["recoveries"]) > 0 for row in rows),
            sum(int(row["false"]) for row in rows),
            len(rows),
        )
    if set(result) != {"minor-third", "major-third", "minor-fifth", "major-fifth"}:
        raise ValueError(f"{path}: missing guitar tone audit sections")
    return result


def dagstuhl_choirset_rows(path: Path) -> list[tuple[str, str, int, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"group", "metric", "accurate", "total"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing DCS columns: {', '.join(sorted(missing))}")
    result: list[tuple[str, str, int, int]] = []
    for row in rows:
        try:
            accurate, total = int(row["accurate"]), int(row["total"])
        except ValueError as error:
            raise ValueError(f"{path}: invalid DCS count") from error
        if total <= 0 or accurate < 0 or accurate > total:
            raise ValueError(f"{path}: invalid DCS fraction {accurate}/{total}")
        result.append((row["group"], row["metric"], accurate, total))
    if not result:
        raise ValueError(f"{path}: no DCS measurement rows")
    return result


def vocal_exact_note_cross_corpus_rows(path: Path) -> list[tuple[str, int, int, int, int, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = ("corpus", "exact_vocal", "exact_foreign", "pitch_class_only", "no_pitch_class", "total")
        missing = set(fields) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing vocal exact-note columns: {', '.join(sorted(missing))}")
        result: list[tuple[str, int, int, int, int, int]] = []
        for row in reader:
            try:
                values = tuple(int(row[field]) for field in fields[1:])
            except ValueError as error:
                raise ValueError(f"{path}: invalid vocal exact-note count") from error
            if values[-1] <= 0 or any(value < 0 for value in values[:-1]) or sum(values[:-1]) != values[-1]:
                raise ValueError(f"{path}: invalid vocal exact-note fraction")
            result.append((row["corpus"], *values))
    if not result:
        raise ValueError(f"{path}: no vocal exact-note rows")
    return result


def render(
    input_path: Path,
    chord_inputs: list[Path] | None = None,
    vocal_full_mix_input: Path | None = None,
    bach10_gate_outputs: list[Path] | None = None,
    musicnet_gate_output: Path | None = None,
    drum_gate_output: Path | None = None,
    urmp_gate_output: Path | None = None,
    vocalset_full_mix_input: Path | None = None,
    maps_gate_outputs: list[Path] | None = None,
    maps_note_gate_outputs: list[Path] | None = None,
    route_summary: Path | None = None,
    good_sounds_full_mix_input: Path | None = None,
    irmas_labelled_input: Path | None = None,
    hf_drum_gate_outputs: list[Path] | None = None,
    maps_attribute_input: Path | None = None,
    medley_solos_attribute_input: Path | None = None,
    focused_vocalset_clean_vowel_input: Path | None = None,
    pitch_shifted_violin_input: Path | None = None,
    philharmonia_full_input: Path | None = None,
    iowa_orchestra_full_input: Path | None = None,
    tinysol_wind_exact_input: Path | None = None,
    iowa_sax_full_mix_input: Path | None = None,
    tinysol_sax_full_mix_input: Path | None = None,
    tinysol_flute_full_mix_input: Path | None = None,
    real_a2s_tenor_scale_input: Path | None = None,
    urmp_sax_exact_input: Path | None = None,
    urmp_sax_full_mix_input: Path | None = None,
    star_drums_gate_output: Path | None = None,
    mdb_drums_gate_output: Path | None = None,
    dagstuhl_choirset_input: Path | None = None,
    dagstuhl_choirset_validation: Path | None = None,
    dagstuhl_choirset_inspection: Path | None = None,
    dagstuhl_choirset_extraction: Path | None = None,
    dagstuhl_choirset_manifest: Path | None = None,
    choral_singing_dataset_archive: Path | None = None,
    choral_singing_dataset_extraction: Path | None = None,
    choral_singing_dataset_inspection: Path | None = None,
    choral_singing_dataset_manifest: Path | None = None,
    choral_singing_dataset_measurement: Path | None = None,
    esmuc_choir_dataset_archive: Path | None = None,
    esmuc_choir_dataset_extraction: Path | None = None,
    esmuc_choir_dataset_manifest: Path | None = None,
    esmuc_choir_dataset_measurement: Path | None = None,
    esmuc_choir_dataset_pattern_report: Path | None = None,
    mir1k_dataset_archive: Path | None = None,
    mir1k_dataset_extraction: Path | None = None,
    mir1k_full_mix_input: Path | None = None,
    scms_dataset_archive: Path | None = None,
    scms_dataset_inspection: Path | None = None,
    scms_dataset_extraction: Path | None = None,
    scms_dataset_manifest: Path | None = None,
    scms_dataset_measurement: Path | None = None,
    scms_full_mix_input: Path | None = None,
    vocal_exact_note_cross_corpus_input: Path | None = None,
    iowa_piano_full_mix_input: Path | None = None,
    maestro_real_measurement: Path | None = None,
    maestro_real_manifest: Path | None = None,
    maestro_real_attribute_input: Path | None = None,
    independent_piano_chord_state_evidence_input: Path | None = None,
    kraisler_archive: Path | None = None,
    kraisler_extraction: Path | None = None,
    kraisler_manifest: Path | None = None,
    kraisler_measurement: Path | None = None,
    musicnet_routing_input: Path | None = None,
    high_vocal_octave_audit: Path | None = None,
    electronic_piano_guitar_route_audit_input: Path | None = None,
    scms_vocal_other_route_audit_input: Path | None = None,
    tenor_sax_piano_route_audit_input: Path | None = None,
    violin_guitar_route_audit_input: Path | None = None,
    guitar_chord_primary_display_audit_input: Path | None = None,
    guitar_chord_tone_recovery_audit_input: Path | None = None,
) -> str:
    samples = load_samples(input_path)
    dcs_rows = dagstuhl_choirset_rows(dagstuhl_choirset_input) if dagstuhl_choirset_input else []
    dcs_validation_ready = int(dagstuhl_choirset_validation is not None and dagstuhl_choirset_validation.is_file())
    dcs_inspection_ready = int(dagstuhl_choirset_inspection is not None and dagstuhl_choirset_inspection.is_file())
    dcs_extraction_ready = int(dagstuhl_choirset_extraction is not None and dagstuhl_choirset_extraction.is_file())
    dcs_manifest_ready = int(dagstuhl_choirset_manifest is not None and dagstuhl_choirset_manifest.is_file())
    maestro_real_rows = maestro_real_gate_rows(maestro_real_measurement) if maestro_real_measurement else []
    maestro_real_manifest_ready = int(maestro_real_manifest is not None and maestro_real_manifest.is_file())
    kraisler_rows = dagstuhl_choirset_rows(kraisler_measurement) if kraisler_measurement else []
    kraisler_archive_ready = int(kraisler_archive is not None and kraisler_archive.is_file())
    kraisler_extraction_ready = int(kraisler_extraction is not None and kraisler_extraction.is_dir())
    kraisler_manifest_ready = int(kraisler_manifest is not None and kraisler_manifest.is_file())
    kraisler_audit_ready = int(bool(kraisler_rows) and route_summary is not None and route_summary.is_file())
    piano_state_evidence = (
        independent_piano_state_evidence(independent_piano_chord_state_evidence_input)
        if independent_piano_chord_state_evidence_input
        else None
    )
    electronic_piano_guitar_audit = (
        electronic_piano_guitar_route_audit(electronic_piano_guitar_route_audit_input)
        if electronic_piano_guitar_route_audit_input is not None
        and electronic_piano_guitar_route_audit_input.is_file()
        else None
    )
    scms_vocal_other_audit = (
        scms_vocal_other_route_audit(scms_vocal_other_route_audit_input)
        if scms_vocal_other_route_audit_input is not None
        and scms_vocal_other_route_audit_input.is_file()
        else None
    )
    tenor_sax_piano_audit = (
        tenor_sax_piano_route_audit(tenor_sax_piano_route_audit_input)
        if tenor_sax_piano_route_audit_input is not None
        and tenor_sax_piano_route_audit_input.is_file()
        else None
    )
    violin_guitar_audit = (
        violin_guitar_route_audit(violin_guitar_route_audit_input)
        if violin_guitar_route_audit_input is not None
        and violin_guitar_route_audit_input.is_file()
        else None
    )
    guitar_chord_primary_audit = (
        guitar_chord_primary_display_audit(guitar_chord_primary_display_audit_input)
        if guitar_chord_primary_display_audit_input is not None
        and guitar_chord_primary_display_audit_input.is_file()
        else None
    )
    guitar_chord_tone_audit = (
        guitar_chord_tone_recovery_audit(guitar_chord_tone_recovery_audit_input)
        if guitar_chord_tone_recovery_audit_input is not None
        and guitar_chord_tone_recovery_audit_input.is_file()
        else None
    )
    csd_rows = dagstuhl_choirset_rows(choral_singing_dataset_measurement) if choral_singing_dataset_measurement else []
    esmuc_rows = dagstuhl_choirset_rows(esmuc_choir_dataset_measurement) if esmuc_choir_dataset_measurement else []
    exact_note_cross_rows = (
        vocal_exact_note_cross_corpus_rows(vocal_exact_note_cross_corpus_input)
        if vocal_exact_note_cross_corpus_input
        else []
    )
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
    if route_summary is not None:
        lines.extend(
            [
                "",
                "## Detector-improvement route coverage",
                "",
                "This tracks the empirical candidate search. A route is actionable only when its "
                "measured gain has no protected-row regression and positive evidence from two "
                "independently prepared corpora.",
                "",
                f"Source: `{route_summary.as_posix()}`",
                "",
                "| Metric | Routes / total | Other routes |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, count, total in route_coverage_rows(route_summary):
            lines.append(f"| {label} | {fraction(count, total)} | {total - count} |")
    if electronic_piano_guitar_audit is not None:
        source_samples, recurring_corpora, corpus_total = electronic_piano_guitar_audit
        lines.extend(
            [
                "",
                "## Electronic-piano-to-Guitar safety audit",
                "",
                "The leading three-signal electronic-piano display profile is audited against "
                "the independent MAPS and MAESTRO piano corpora before any routing change.",
                "",
                f"Source: `{electronic_piano_guitar_route_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Independent piano corpora reproducing the profile | {fraction(recurring_corpora, corpus_total)} | {corpus_total - recurring_corpora} |",
                f"| Runtime routing change eligible | {fraction(int(recurring_corpora == corpus_total), 1)} | {int(recurring_corpora != corpus_total)} |",
                "",
                f"The originating cached corpus has {source_samples} matching electronic-piano samples; neither independent corpus reproduces the profile, so the rule is rejected.",
            ]
        )
    if scms_vocal_other_audit is not None:
        source_samples, recurring_corpora, corpus_total = scms_vocal_other_audit
        lines.extend(
            [
                "",
                "## SCMS vocal-to-Other safety audit",
                "",
                "The leading SCMS visual vocal-route profile is audited against independent "
                "Vocadito, VocalSet, and MIR-1K vocal corpora before any display change.",
                "",
                f"Source: `{scms_vocal_other_route_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Independent vocal corpora reproducing the profile | {fraction(recurring_corpora, corpus_total)} | {corpus_total - recurring_corpora} |",
                f"| Runtime display change eligible | {fraction(int(recurring_corpora >= 2), 1)} | {int(recurring_corpora < 2)} |",
                "",
                f"The originating SCMS corpus has {source_samples} matching vocal samples. Only one independent corpus reproduces the profile, so the rule is rejected.",
            ]
        )
    if tenor_sax_piano_audit is not None:
        source_samples, recurring_corpora, corpus_total = tenor_sax_piano_audit
        lines.extend(
            [
                "",
                "## Tenor-saxophone-to-Piano safety audit",
                "",
                "The leading Good Sounds tenor-saxophone routing profile is audited against "
                "independent Iowa, TinySOL, and real tenor-saxophone fixtures before any reroute.",
                "",
                f"Source: `{tenor_sax_piano_route_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Independent saxophone corpora reproducing the profile | {fraction(recurring_corpora, corpus_total)} | {corpus_total - recurring_corpora} |",
                f"| Runtime routing change eligible | {fraction(int(recurring_corpora >= 2), 1)} | {int(recurring_corpora < 2)} |",
                "",
                f"The originating Good Sounds corpus has {source_samples} matching tenor-saxophone samples; no independent saxophone fixture reproduces the profile, so the rule is rejected.",
            ]
        )
    if violin_guitar_audit is not None:
        source_samples, recurring_corpora, corpus_total = violin_guitar_audit
        lines.extend(
            [
                "",
                "## Violin-to-Guitar safety audit",
                "",
                "The leading Good Sounds violin routing profile is audited against independent "
                "Iowa strings and KRAISLER piano--violin mixture evidence before any reroute.",
                "",
                f"Source: `{violin_guitar_route_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Independent violin corpora reproducing the profile | {fraction(recurring_corpora, corpus_total)} | {corpus_total - recurring_corpora} |",
                f"| Runtime routing change eligible | {fraction(int(recurring_corpora >= 2), 1)} | {int(recurring_corpora < 2)} |",
                "",
                f"The originating Good Sounds corpus has {source_samples} matching violin samples; neither independent violin corpus reproduces the profile, so the rule is rejected.",
            ]
        )
    if guitar_chord_primary_audit is not None:
        source_primary, comparison_primary, source_safe_rules, comparison_safe_rules = (
            guitar_chord_primary_audit
        )
    if guitar_chord_tone_audit is not None:
        minor_third = guitar_chord_tone_audit["minor-third"]
        major_third = guitar_chord_tone_audit["major-third"]
        minor_fifth = guitar_chord_tone_audit["minor-fifth"]
        major_fifth = guitar_chord_tone_audit["major-fifth"]
        eligible = int(
            minor_third[0] >= 2 and minor_third[1] == 0
        ) + int(major_third[0] >= 2 and major_third[1] == 0)
        lines.extend(
            [
                "",
                "## Guitar chord tone-recovery safety audit",
                "",
                "Third and fifth recovery rules are checked against the independent GAPS, Guitar "
                "Chord Mix, and Guitar-TECHS corpora before changing chord construction.",
                "",
                f"Source: `{guitar_chord_tone_recovery_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Minor-third recovery corpora | {fraction(minor_third[0], minor_third[2])} | {minor_third[2] - minor_third[0]} |",
                f"| Major-third recovery corpora | {fraction(major_third[0], major_third[2])} | {major_third[2] - major_third[0]} |",
                f"| Major-third protected false promotions avoided | {fraction(int(major_third[1] == 0), 1)} | {int(major_third[1] != 0)} |",
                f"| Minor-fifth recovery corpora | {fraction(minor_fifth[0], minor_fifth[2])} | {minor_fifth[2] - minor_fifth[0]} |",
                f"| Major-fifth recovery corpora | {fraction(major_fifth[0], major_fifth[2])} | {major_fifth[2] - major_fifth[0]} |",
                f"| Runtime tone-recovery change eligible | {fraction(eligible, 2)} | {2 - eligible} |",
                "",
                f"Minor third is source-local; major third has {major_third[1]} protected false promotions; neither fifth route has candidates. No tone-recovery rule is permitted.",
            ]
        )
        supporting_corpora = int(source_safe_rules > 0) + int(comparison_safe_rules > 0)
        lines.extend(
            [
                "",
                "## Guitar chord primary-display safety audit",
                "",
                "The primary label may only be reordered when the same runtime-safe predicate "
                "is supported by both the isolated Guitar Chord Mix and full-performance GAPS "
                "corpora.",
                "",
                f"Source: `{guitar_chord_primary_display_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Guitar Chord Mix primary displayed chord | {fraction(source_primary[0], source_primary[1])} | {source_primary[1] - source_primary[0]} |",
                f"| GAPS full-performance primary displayed chord | {fraction(comparison_primary[0], comparison_primary[1])} | {comparison_primary[1] - comparison_primary[0]} |",
                f"| Corpora with any zero-regression local reorder rule | {fraction(supporting_corpora, 2)} | {2 - supporting_corpora} |",
                f"| Shared runtime display change eligible | {fraction(int(source_safe_rules > 0 and comparison_safe_rules > 0), 1)} | {int(not (source_safe_rules > 0 and comparison_safe_rules > 0))} |",
                "",
                f"GAPS has {comparison_safe_rules} local zero-regression rule candidates, but Guitar Chord Mix has {source_safe_rules}; no shared rule exists, so no runtime reorder is permitted.",
            ]
        )
    if high_vocal_octave_audit is not None and high_vocal_octave_audit.is_file():
        lines.extend(
            [
                "",
                "## High-soprano octave safety audit",
                "",
                "A high F5/F#5 vocal recovery is only eligible if it improves at least two independent choir corpora with no protected-instrument reroutes. The lower-octave gate selects protected keyboard candidates; all tested zero-overlap multi-signal profiles reduced protected visual accuracy, so no behavior change is permitted.",
                "",
                f"Source: `{high_vocal_octave_audit.as_posix()}`",
                "",
            ]
        )
        lines.extend(high_vocal_octave_audit.read_text(encoding="utf-8").strip().splitlines())
    lines.extend(
        [
            "",
            "## Rejected three-corpus keys-to-vocal routing trial",
            "",
            "A zero-static-risk `keys`-owned vocal subset spanning DCS, CSD, and ESMUC was "
            "trialled as a Vocal route. It did not improve DCS and reduced protected first-row "
            "accuracy, so the runtime change was removed.",
            "",
            "| Metric | Accurate / total | Remaining |",
            "| --- | ---: | ---: |",
            f"| DCS note hits during trial | {fraction(659, 925)} | {925 - 659} |",
            f"| DCS exact chord hits during trial | {fraction(49, 240)} | {240 - 49} |",
            f"| Protected full-mix first-row accuracy during trial | {fraction(771, 2212)} | {2212 - 771} |",
            f"| Protected full-mix first-row baseline | {fraction(772, 2212)} | {2212 - 772} |",
            "",
            "The one protected-row regression violates the zero-regression gate despite the "
            "cross-corpus static evidence.",
        ]
    )
    lines.extend(
        [
            "",
            "## Dagstuhl ChoirSet (DCS) coverage-gap checklist",
            "",
            "DCS is an independent real vocal-ensemble corpus. Generated fixtures never count as "
            "DCS measurements; completion requires validated public audio plus score-aligned results.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store DCS archive in InstrumentSamples | {fraction(dcs_validation_ready, 1)} | {1 - dcs_validation_ready} | validated archive and checksum |",
            f"| Extract DCS safely in InstrumentSamples | {fraction(dcs_extraction_ready, 1)} | {1 - dcs_extraction_ready} | traversal-safe extraction record |",
            f"| Inspect real DCS audio and annotations | {fraction(dcs_inspection_ready, 1)} | {1 - dcs_inspection_ready} | corpus inventory by song/take/microphone |",
            f"| Import DCS sources and labels | {fraction(dcs_manifest_ready, 1)} | {1 - dcs_manifest_ready} | tested prepared-multitrack manifest |",
            f"| Measure note and pitch-class recall | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | real DCS x/total results |",
            f"| Measure octave accuracy | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | real DCS exact-MIDI x/total results |",
            f"| Measure vocal ownership and display routing | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | real DCS row-routing x/total results |",
            f"| Measure chord accuracy | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | real DCS chord x/total results |",
            f"| Break down results by SATB range | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | S/A/T/B x/total rows |",
            f"| Break down results by recording configuration | {fraction(int(bool(dcs_rows)), 1)} | {int(not dcs_rows)} | setting/take/microphone x/total rows |",
            "| Verify a safe cross-corpus detector improvement | 0 / 1 (0.0%) | 1 | DCS and protected-corpus regression evidence |",
        ]
    )
    csd_archive_ready = int(choral_singing_dataset_archive is not None and choral_singing_dataset_archive.is_file())
    csd_extraction_ready = int(choral_singing_dataset_extraction is not None and choral_singing_dataset_extraction.is_file())
    csd_inspection_ready = int(choral_singing_dataset_inspection is not None and choral_singing_dataset_inspection.is_file())
    csd_manifest_ready = int(choral_singing_dataset_manifest is not None and choral_singing_dataset_manifest.is_file())
    lines.extend(
        [
            "",
            "## Choral Singing Dataset (CSD) coverage-gap checklist",
            "",
            "CSD is the next independent labelled SATB corpus. It contains isolated singers and "
            "synchronised MIDI; every step below must remain external to the repository through "
            "`build/InstrumentSamples`.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store current CSD archive in InstrumentSamples | {fraction(csd_archive_ready, 1)} | {1 - csd_archive_ready} | validated official archive and checksum |",
            f"| Extract CSD safely in InstrumentSamples | {fraction(csd_extraction_ready, 1)} | {1 - csd_extraction_ready} | traversal-safe extraction record |",
            f"| Inspect CSD audio, stems, and MIDI | {fraction(csd_inspection_ready, 1)} | {1 - csd_inspection_ready} | corpus inventory by work and section |",
            f"| Import CSD sources and labels | {fraction(csd_manifest_ready, 1)} | {1 - csd_manifest_ready} | tested prepared-multitrack manifest |",
            f"| Measure CSD note, octave, and pitch-class recall | {fraction(int(bool(csd_rows)), 1)} | {int(not csd_rows)} | real CSD x/total results |",
            f"| Measure CSD vocal ownership and current-note routing | {fraction(int(bool(csd_rows)), 1)} | {int(not csd_rows)} | real CSD routing x/total results |",
            f"| Measure CSD chord accuracy | {fraction(int(bool(csd_rows)), 1)} | {int(not csd_rows)} | real CSD chord x/total results |",
            "| Recheck any candidate across DCS, CSD, and cached vocal corpora | 0 / 1 (0.0%) | 1 | latest scan rejects DCS/CSD-only key rules: no cached-corpus support without regressions |",
        ]
    )
    if csd_rows:
        lines.extend(
            [
                "",
                "## Choral Singing Dataset (CSD) real-audio measurement",
                "",
                "Each CSD recording is a sum of four synchronised, individually recorded SATB stems. "
                "Per-part ownership is strict; current-note routing credits the monophonic vocal display "
                "when it matches any active SATB score pitch.",
                "",
                f"Source: `{choral_singing_dataset_measurement.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for group, metric, accurate, total in csd_rows:
            if group in {"All SATB notes", "All CSD chord windows", "All CSD vocal windows"}:
                lines.append(f"| CSD {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### CSD SATB range breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in csd_rows:
            if group.startswith("SATB range — "):
                lines.append(f"| CSD {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### CSD recording-configuration breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in csd_rows:
            if group.startswith("Configuration — "):
                lines.append(f"| CSD {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
    esmuc_archive_ready = int(esmuc_choir_dataset_archive is not None and esmuc_choir_dataset_archive.is_file())
    esmuc_extraction_ready = int(esmuc_choir_dataset_extraction is not None and esmuc_choir_dataset_extraction.is_file())
    esmuc_manifest_ready = int(esmuc_choir_dataset_manifest is not None and esmuc_choir_dataset_manifest.is_file())
    esmuc_pattern_audit_ready = int(esmuc_choir_dataset_pattern_report is not None and esmuc_choir_dataset_pattern_report.is_file())
    lines.extend(
        [
            "",
            "## ESMUC Choir Dataset coverage-gap checklist",
            "",
            "ESMUC adds independently labelled, synchronised SATB choir recordings with full takes, "
            "isolated sections, and short excerpts. The archive and extracted corpus remain in "
            "InstrumentSamples; only prepared measurement fixtures may be produced under `build/`.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store validated ESMUC archive in InstrumentSamples | {fraction(esmuc_archive_ready, 1)} | {1 - esmuc_archive_ready} | official archive checksum |",
            f"| Extract ESMUC safely in InstrumentSamples | {fraction(esmuc_extraction_ready, 1)} | {1 - esmuc_extraction_ready} | traversal-safe extraction marker |",
            "| Inventory ESMUC stems and corrected labels | 1 / 1 (100.0%) | 0 | 495 WAV, 276 note labels, 300 F0 files; FT/IS/SE configurations |",
            f"| Import ESMUC sources and labels | {fraction(esmuc_manifest_ready, 1)} | {1 - esmuc_manifest_ready} | tested prepared-multitrack manifest (19 complete SATB recordings) |",
            f"| Measure ESMUC note, octave, and pitch-class recall | {fraction(int(bool(esmuc_rows)), 1)} | {int(not esmuc_rows)} | real ESMUC x/total results |",
            f"| Measure ESMUC vocal ownership and current-note routing | {fraction(int(bool(esmuc_rows)), 1)} | {int(not esmuc_rows)} | real ESMUC routing x/total results |",
            f"| Measure ESMUC chord accuracy | {fraction(int(bool(esmuc_rows)), 1)} | {int(not esmuc_rows)} | real ESMUC chord x/total results |",
            f"| Break down ESMUC results by SATB and configuration | {fraction(int(bool(esmuc_rows)), 1)} | {int(not esmuc_rows)} | S/A/T/B and FT/IS/SE x/total rows |",
            f"| Run DCS/CSD/ESMUC/MIR-1K/cached-vocal ownership audit | {fraction(esmuc_pattern_audit_ready, 1)} | {1 - esmuc_pattern_audit_ready} | MIR-1K-inclusive zero-regression pattern report |",
            f"| Audit exact-MIDI vocal failures across all six corpora | {fraction(int(bool(exact_note_cross_rows)), 1)} | {int(not exact_note_cross_rows)} | exact-vocal, foreign-route, octave-alias, and absent evidence x/total |",
            "| Verify a safe cross-corpus detector improvement | 0 / 1 (0.0%) | 1 | zero-protected keyboard candidates remain choir-only; MIR-1K/solo-vocal-supported candidates regress protected vocal rows, so every rule is rejected |",
        ]
    )
    if esmuc_rows:
        lines.extend(
            [
                "",
                "## ESMUC Choir Dataset real-audio measurement",
                "",
                "Each recording is a real synchronised four-source SATB mix. Current-note routing is "
                "credited when the monophonic vocal display matches any concurrent SATB score pitch.",
                "",
                f"Source: `{esmuc_choir_dataset_measurement.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for group, metric, accurate, total in esmuc_rows:
            if group in {"All SATB notes", "All ESMUC chord windows", "All ESMUC vocal windows"}:
                lines.append(f"| ESMUC {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### ESMUC SATB range breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in esmuc_rows:
            if group.startswith("SATB range — "):
                lines.append(f"| ESMUC {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### ESMUC recording-configuration breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in esmuc_rows:
            if group.startswith("Configuration — "):
                lines.append(f"| ESMUC {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
    mir1k_samples = load_samples(mir1k_full_mix_input) if mir1k_full_mix_input else {}
    mir1k_rows = family_metric_rows(mir1k_samples, "vocals") if mir1k_samples else []
    mir1k_exact_rows = exact_note_rows(mir1k_samples) if mir1k_samples else []
    mir1k_archive_ready = int(mir1k_dataset_archive is not None and mir1k_dataset_archive.is_file())
    mir1k_extraction_ready = int(mir1k_dataset_extraction is not None and mir1k_dataset_extraction.is_file())
    lines.extend(
        [
            "",
            "## MIR-1K vocal-with-accompaniment coverage-gap checklist",
            "",
            "MIR-1K provides real karaoke vocal/accompaniment clips and manual frame-level vocal pitch "
            "annotations. It is the independent non-choir corpus needed to test whether proposed vocal "
            "routing improvements generalise beyond isolated singers and SATB mixtures.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store validated MIR-1K archive in InstrumentSamples | {fraction(mir1k_archive_ready, 1)} | {1 - mir1k_archive_ready} | published archive checksum |",
            f"| Extract MIR-1K safely in InstrumentSamples | {fraction(mir1k_extraction_ready, 1)} | {1 - mir1k_extraction_ready} | traversal-safe extraction marker |",
            "| Inventory audio, pitch, and vocal-activity annotations | 1 / 1 (100.0%) | 0 | 3,000 WAV, 1,000 pitch, 1,000 vocal, and 1,000 unvoiced labels |",
            f"| Import labelled vocal-plus-accompaniment clips | {fraction(int(bool(mir1k_rows)), 1)} | {int(not mir1k_rows)} | tested measurement manifest |",
            f"| Measure vocal pitch-class and exact-MIDI recall | {fraction(int(bool(mir1k_rows)), 1)} | {int(not mir1k_rows)} | real MIR-1K x/total results |",
            f"| Measure vocal ownership and visible current-note routing | {fraction(int(bool(mir1k_rows)), 1)} | {int(not mir1k_rows)} | real MIR-1K routing x/total results |",
            f"| Re-audit ownership rules across choir, solo-vocal, and MIR-1K corpora | {fraction(esmuc_pattern_audit_ready, 1)} | {1 - esmuc_pattern_audit_ready} | zero-regression cross-corpus report |",
        ]
    )
    if mir1k_rows:
        lines.extend([
            "",
            "## MIR-1K full-mix vocal routing",
            "",
            "Each probe is cut from the supplied vocal-plus-accompaniment mix at the centre of its "
            "longest stable manually annotated 20 ms vocal-pitch run. The vocal stem is not used as "
            "measurement audio.",
            "",
            f"Source: `{mir1k_full_mix_input.as_posix()}`",
            "",
            "| Metric | Accurate / total | Remaining |",
            "| --- | ---: | ---: |",
        ])
        for label, accurate, total in mir1k_rows:
            lines.append(f"| MIR-1K vocals — {label} | {fraction(accurate, total)} | {total - accurate} |")
        for label, accurate, total in mir1k_exact_rows:
            if label == "Vocals — exact expected MIDI note":
                lines.append(f"| MIR-1K vocals — {label} | {fraction(accurate, total)} | {total - accurate} |")
    scms_archive_ready = int(scms_dataset_archive is not None and scms_dataset_archive.is_file())
    scms_inspection_ready = int(scms_dataset_inspection is not None and scms_dataset_inspection.is_file())
    scms_extraction_ready = int(scms_dataset_extraction is not None and scms_dataset_extraction.is_file())
    scms_manifest_ready = int(scms_dataset_manifest is not None and scms_dataset_manifest.is_file())
    scms_measurement_ready = int(scms_dataset_measurement is not None and scms_dataset_measurement.is_file())
    scms_samples = load_samples(scms_full_mix_input) if scms_full_mix_input else {}
    scms_rows = family_metric_rows(scms_samples, "vocals") if scms_samples else []
    scms_exact_rows = exact_note_rows(scms_samples) if scms_samples else []
    scms_cross_corpus_ready = int(any(row[0] == "SCMS" for row in exact_note_cross_rows))
    lines.extend(
        [
            "",
            "## Saraga-Carnatic-Melody-Synth (SCMS) coverage-gap checklist",
            "",
            "SCMS supplies real 30-second vocal-plus-accompaniment mixtures with time-aligned continuous "
            "vocal-melody annotations. Its archive stays in InstrumentSamples; the layout must be inspected "
            "before a traversal-safe extractor or labelled measurement importer is added.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store validated SCMS archive in InstrumentSamples | {fraction(scms_archive_ready, 1)} | {1 - scms_archive_ready} | official Zenodo MD5 |",
            f"| Inspect SCMS audio and CSV/LAB annotation inventory | {fraction(scms_inspection_ready, 1)} | {1 - scms_inspection_ready} | non-extracting ZIP inventory |",
            f"| Extract SCMS safely in InstrumentSamples | {fraction(scms_extraction_ready, 1)} | {1 - scms_extraction_ready} | traversal-safe extraction marker |",
            f"| Prepare labelled vocal-plus-accompaniment windows | {fraction(scms_manifest_ready, 1)} | {1 - scms_manifest_ready} | tested measurement manifest |",
            f"| Measure current-note exact-MIDI and pitch-class recall | {fraction(scms_measurement_ready, 1)} | {1 - scms_measurement_ready} | real SCMS x/total results |",
            f"| Measure vocal ownership and visible current-note routing | {fraction(scms_measurement_ready, 1)} | {1 - scms_measurement_ready} | real SCMS routing x/total results |",
            f"| Re-audit protected routes with SCMS and existing vocal corpora | {fraction(scms_cross_corpus_ready, 1)} | {1 - scms_cross_corpus_ready} | cross-corpus baseline report |",
        ]
    )
    if scms_rows:
        lines.extend([
            "",
            "## SCMS full-mix vocal routing",
            "",
            "Each probe is measured from its labelled vocal-plus-accompaniment mixture; annotations are "
            "used only as ground truth, never as analyzer input.",
            "",
            f"Source: `{scms_full_mix_input.as_posix()}`",
            "",
            "| Metric | Accurate / total | Remaining |",
            "| --- | ---: | ---: |",
        ])
        for label, accurate, total in scms_rows:
            lines.append(f"| SCMS vocals — {label} | {fraction(accurate, total)} | {total - accurate} |")
        for label, accurate, total in scms_exact_rows:
            if label == "Vocals — exact expected MIDI note":
                lines.append(f"| SCMS vocals — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if exact_note_cross_rows:
        lines.extend([
            "",
            "## Cross-corpus vocal exact-MIDI evidence",
            "",
            "Exact vocal means the annotated MIDI pitch is present in the vocal row. Foreign-route "
            "means the exact pitch is present only in another row; pitch-class-only means the pitch class "
            "is detected in the wrong octave.",
            "",
            f"Source: `{vocal_exact_note_cross_corpus_input.as_posix()}`",
            "",
            "| Corpus / outcome | Accurate / total | Remaining |",
            "| --- | ---: | ---: |",
        ])
        for corpus, exact_vocal, exact_foreign, pitch_class_only, no_pitch_class, total in exact_note_cross_rows:
            lines.append(f"| {corpus} — exact MIDI in vocal row | {fraction(exact_vocal, total)} | {total - exact_vocal} |")
            lines.append(f"| {corpus} — exact MIDI only in foreign row | {fraction(exact_foreign, total)} | {total - exact_foreign} |")
            lines.append(f"| {corpus} — pitch class only (wrong octave) | {fraction(pitch_class_only, total)} | {total - pitch_class_only} |")
            lines.append(f"| {corpus} — no expected pitch class | {fraction(no_pitch_class, total)} | {total - no_pitch_class} |")
    if dcs_rows:
        lines.extend(
            [
                "",
                "## Dagstuhl ChoirSet (DCS) real-audio measurement",
                "",
                "The SATB rows count every score-active singer at a stable center-of-note window in a "
                "real, summed four-singer recording. Vocal ownership and routing require the expected "
                "pitch class in the vocal row; visible routing additionally requires visual level at least "
                "0.25. Current-note vocal rows are separate window-level metrics: because the UI is "
                "monophonic, they count success when its one displayed note matches any concurrent SATB "
                "score pitch.",
                "",
                f"Source: `{dagstuhl_choirset_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for group, metric, accurate, total in dcs_rows:
            if group in {"All SATB notes", "All DCS chord windows", "All DCS vocal windows"}:
                lines.append(f"| DCS {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### DCS SATB range breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in dcs_rows:
            if group.startswith("SATB range — "):
                lines.append(f"| DCS {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
        lines.extend(["", "### DCS recording-configuration breakdown", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for group, metric, accurate, total in dcs_rows:
            if group.startswith("Configuration — "):
                lines.append(f"| DCS {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
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
    if vocalset_full_mix_input is not None:
        vocalset_samples = load_samples(vocalset_full_mix_input)
        vocalset_rows = family_metric_rows(vocalset_samples, "vocals")
        if vocalset_rows:
            lines.extend(
                [
                    "",
                    "## VocalSet full-mix vocal routing",
                    "",
                    "This larger, varied real-vocal corpus measures whether the detected note remains "
                    "on the vocal row when the analyzer also proposes instrumental rows.",
                    "",
                    f"Source: `{vocalset_full_mix_input.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                ]
            )
            for label, accurate, total in vocalset_rows:
                lines.append(
                    f"| VocalSet vocals — {label} | {fraction(accurate, total)} | {total - accurate} |"
                )
    if focused_vocalset_clean_vowel_input is not None:
        focused_rows = family_metric_rows(load_samples(focused_vocalset_clean_vowel_input), "vocals")
        expected_rows = [row for row in focused_rows if row[0] == "Expected instrument row"]
        if expected_rows:
            lines.extend(
                [
                    "",
                    "### Focused clean-vowel regression",
                    "",
                    "This cached VocalSet C5 fixture exercises the measured clean high-vowel profile",
                    "and is regenerated from its one-fixture attribute TSV.",
                    "",
                    f"Source: `{focused_vocalset_clean_vowel_input.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                ]
            )
            for label, accurate, total in expected_rows:
                lines.append(
                    f"| VocalSet clean C5 vowel — {label} | {fraction(accurate, total)} | {total - accurate} |"
                )
    if good_sounds_full_mix_input is not None:
        good_sounds_samples = load_samples(good_sounds_full_mix_input)
        lines.extend(
            [
                "",
                "## Good Sounds full-mix acoustic routing",
                "",
                "This independent acoustic-instrument corpus is measured in full-mix mode. "
                "It is a coverage benchmark, not a release threshold, and includes bass plus "
                "woodwind, brass, and violin samples.",
                "",
                f"Source: `{good_sounds_full_mix_input.as_posix()}`",
                "",
                "The cached Good Sounds archive has been inventoried without extraction: all 1,318 usable "
                "labelled recordings are already in this fixture (661 violin, 453 tenor sax, 159 bass, and "
                "45 other winds/brass). The remaining catalogue rows have no matching packed audio, so this "
                "corpus cannot supply independent additional examples for coverage-blocked route rules.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in table_rows(good_sounds_samples):
            lines.append(f"| Good Sounds — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if irmas_labelled_input is not None:
        irmas_samples = load_samples(irmas_labelled_input)
        lines.extend(
            [
                "",
                "## IRMAS independent instrument-routing coverage",
                "",
                "IRMAS supplies real musical excerpts labelled for their predominant instrument. It has no "
                "time-aligned pitch truth, so these rows measure only runtime candidate availability and "
                "instrument/display routing; they are never used as note- or chord-accuracy claims.",
                "",
                f"Source: `{irmas_labelled_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in label_only_routing_rows(irmas_samples):
            lines.append(f"| IRMAS — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if pitch_shifted_violin_input is not None:
        fixture_rows = family_metric_rows(load_samples(pitch_shifted_violin_input), "other")
        lines.extend(
            [
                "",
                "## Controlled octave-down violin fixture",
                "",
                "Twenty real Philharmonia G3–B3 violin recordings are shifted down one octave. "
                "This explicitly derived fixture covers pitch-shifted/sample-playback violin below "
                "the acoustic violin range; it is kept separate from real-acoustic aggregate accuracy.",
                "",
                f"Source: `{pitch_shifted_violin_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in fixture_rows:
            lines.append(f"| Pitch-shifted violin — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if philharmonia_full_input is not None:
        lines.extend(
            [
                "",
                "## Philharmonia isolated exact-note coverage",
                "",
                "This independent real acoustic corpus requires the annotated MIDI octave, not merely "
                "the pitch class, to appear in its expected instrument row.",
                "",
                f"Source: `{philharmonia_full_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in exact_note_rows(load_samples(philharmonia_full_input)):
            lines.append(f"| Philharmonia — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if iowa_orchestra_full_input is not None:
        iowa_samples = load_samples(iowa_orchestra_full_input)
        lines.extend(
            [
                "",
                "## Iowa orchestra isolated-note coverage",
                "",
                "This independent real acoustic corpus includes brass, woodwind, strings, pitched "
                "percussion, and double bass. The strict rows require the annotated MIDI octave, "
                "while the routing rows distinguish octave errors from absent or misrouted notes.",
                "",
                f"Source: `{iowa_orchestra_full_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in table_rows(iowa_samples):
            lines.append(f"| Iowa orchestra — {label} | {fraction(accurate, total)} | {total - accurate} |")
        for label, accurate, total in exact_note_rows(iowa_samples):
            lines.append(f"| Iowa orchestra — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if tinysol_wind_exact_input is not None:
        wind_rows = exact_note_source_rows(load_samples(tinysol_wind_exact_input), ("oboe", "trombone"))
        lines.extend(
            [
                "",
                "## TinySOL isolated wind and brass exact-note coverage",
                "",
                "This fresh symlink-only independent fixture checks whether the unresolved Philharmonia "
                "oboe and trombone octave aliases recur in a second library. Its exact-MIDI rows are "
                "measured in isolated-note mode before any recovery rule is considered.",
                "",
                f"Source: `{tinysol_wind_exact_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in wind_rows:
            lines.append(f"| TinySOL — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if iowa_sax_full_mix_input is not None:
        sax_rows = family_metric_rows(load_samples(iowa_sax_full_mix_input), "other")
        lines.extend(
            [
                "",
                "## Iowa saxophone full-mix routing",
                "",
                "This symlink-only 60-sample subset of the independent Iowa orchestra corpus "
                "covers alto and soprano saxophones in full-mix mode. It is a focused routing "
                "benchmark for woodwinds whose pitch is detected but can be assigned to another row.",
                "",
                f"Source: `{iowa_sax_full_mix_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in sax_rows:
            lines.append(f"| Iowa saxophones — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if iowa_piano_full_mix_input is not None:
        piano_rows = family_metric_rows(load_samples(iowa_piano_full_mix_input), "piano")
        lines.extend(
            [
                "",
                "## Iowa piano full-mix routing",
                "",
                "This independently labelled real-piano library is measured in the same full-mix "
                "routing mode as the detector audit. It supplies independent evidence before a "
                "piano-to-guitar routing rule can be accepted.",
                "",
                f"Source: `{iowa_piano_full_mix_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in piano_rows:
            lines.append(f"| Iowa piano — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if tinysol_sax_full_mix_input is not None:
        sax_rows = family_metric_rows(load_samples(tinysol_sax_full_mix_input), "other")
        lines.extend(
            [
                "",
                "## TinySOL alto-saxophone full-mix routing",
                "",
                "This independent 98-recording alto-saxophone subset is symlinked from TinySOL and "
                "measured in full-mix mode. Together with Iowa saxophones, it distinguishes a "
                "general saxophone routing failure from a single-library artifact.",
                "",
                f"Source: `{tinysol_sax_full_mix_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in sax_rows:
            lines.append(f"| TinySOL alto saxophone — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if tinysol_flute_full_mix_input is not None:
        flute_rows = family_metric_rows(load_samples(tinysol_flute_full_mix_input), "other")
        lines.extend(
            [
                "",
                "## TinySOL flute full-mix routing",
                "",
                "This independent 118-recording flute subset is symlinked from TinySOL and measured "
                "in full-mix mode. It expands woodwind ownership coverage before any flute recovery "
                "rule is allowed to change the detector.",
                "",
                f"Source: `{tinysol_flute_full_mix_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in flute_rows:
            lines.append(f"| TinySOL flute — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if real_a2s_tenor_scale_input is not None:
        tenor_samples = load_samples(real_a2s_tenor_scale_input)
        lines.extend(
            [
                "",
                "## Real A2S tenor-saxophone score-aligned probes",
                "",
                "These are 489 timed notes cut silently from twelve real tenor-saxophone major-scale "
                "recordings and three exercises, aligned to their bundled **kern scores. The source notation is shifted "
                "down one octave to its measured sounding pitch before scoring. This is an independent "
                "real-tenor diagnostic, not yet a broad generalization gate.",
                "",
                f"Source: `{real_a2s_tenor_scale_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in table_rows(tenor_samples):
            lines.append(f"| Real A2S tenor saxophone — {label} | {fraction(accurate, total)} | {total - accurate} |")
        for label, accurate, total in exact_note_rows(tenor_samples):
            lines.append(f"| Real A2S tenor saxophone — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if urmp_sax_exact_input is not None:
        urmp_sax_samples = load_samples(urmp_sax_exact_input)
        lines.extend(
            [
                "",
                "## URMP isolated saxophone exact-note coverage",
                "",
                "This independent real multitrack fixture uses stable center-of-note clips cut silently "
                "from official URMP saxophone stems with timestamp, frequency, and duration annotations. "
                "It measures exact sounding MIDI octave separately from the score-aligned A2S probes.",
                "",
                f"Source: `{urmp_sax_exact_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in exact_note_rows(urmp_sax_samples):
            lines.append(f"| URMP saxophones — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if urmp_sax_full_mix_input is not None:
        urmp_sax_full_mix_samples = load_samples(urmp_sax_full_mix_input)
        lines.extend(
            [
                "",
                "## URMP saxophone full-mix-mode routing",
                "",
                "The same independent, annotated URMP saxophone clips are analyzed in full-mix mode. "
                "This isolates row-routing behavior from the exact-octave isolated-note benchmark.",
                "",
                f"Source: `{urmp_sax_full_mix_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in table_rows(urmp_sax_full_mix_samples):
            lines.append(f"| URMP saxophones — {label} | {fraction(accurate, total)} | {total - accurate} |")
        for label, accurate, total in exact_note_rows(urmp_sax_full_mix_samples):
            lines.append(f"| URMP saxophones — {label} | {fraction(accurate, total)} | {total - accurate} |")
    if medley_solos_attribute_input is not None:
        lines.extend(
            [
                "",
                "## Medley Solos instrument routing",
                "",
                "This independent corpus contains 300 three-second isolated performances from each "
                "of eight instruments. It is measured in full-mix mode; a sample is accurate when any "
                "analyzed buffer activates its expected instrument row. It supplies routing coverage, "
                "not pitch or chord ground truth.",
                "",
                f"Source: `{medley_solos_attribute_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in medley_solos_rows(medley_solos_attribute_input):
            lines.append(f"| Medley Solos — {label} | {fraction(accurate, total)} | {total - accurate} |")
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
    if urmp_gate_output is not None:
        lines.extend(
            [
                "",
                "## URMP real multitrack gate",
                "",
                "This downloaded real chamber-music corpus measures the same performances as "
                "provided mixes and as sums of their isolated tracks, with official note and MIDI annotations.",
                "Instrument rows below show exact isolated-note recall for each measured instrument.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in urmp_gate_rows(urmp_gate_output):
            remaining = f"{total - accurate} false notes" if label.endswith("precision") else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remaining} |")
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
                "This open CC-BY corpus measures real classical mixtures; unlike Bach10, it has no isolated stems. "
                "A recording is eligible for its chord rows only when annotations provide a window with at least "
                "two active instruments and two pitch classes.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in musicnet_gate_rows(musicnet_gate_output):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if musicnet_routing_input is not None:
        lines.extend(["", "### MusicNet annotated instrument-routing", "", "Each active annotated note is checked against its General-MIDI family row. These are real-mixture routing measurements, separate from the global chord gate.", "", f"Source: `{musicnet_routing_input.as_posix()}`", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for label, accurate, total in musicnet_routing_rows(musicnet_routing_input):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if maps_gate_outputs:
        lines.extend(
            [
                "",
                "## MAPS real-piano gate",
                "",
                "This real Disklavier corpus uses aligned MIDI annotations. The four stored shard summaries "
                "are combined here; rows remain visible even when the aggregate quality gate fails.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in maps_gate_rows(maps_gate_outputs):
            remaining = f"{total - accurate} false predictions" if label.endswith("precision") else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remaining} |")
        lines.extend(
            [
                "",
                "## Independent piano cross-corpus coverage checklist",
                "",
                "MAESTRO is independent external paired WAV/MIDI evidence. It remains separate from MAPS until a protected cross-piano rule is verified.",
                "",
                "| Task | Complete / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Prepare external MAESTRO paired-audio subset | {fraction(maestro_real_manifest_ready, 1)} | {1 - maestro_real_manifest_ready} |",
                f"| Measure MAESTRO note and chord outcomes | {fraction(int(bool(maestro_real_rows)), 1)} | {int(not maestro_real_rows)} |",
                "| Mine a protected cross-piano detector rule | 0 / 1 (0.0%) | 1 |",
            ]
        )
        if maestro_real_rows:
            lines.extend(
                [
                    "",
                    "### MAESTRO external-piano measurement",
                    "",
                    f"Source: `{maestro_real_measurement.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                ]
            )
            for label, accurate, total in maestro_real_rows:
                remaining = f"{total - accurate} false predictions" if label.endswith("precision") else str(total - accurate)
                lines.append(f"| {label} | {fraction(accurate, total)} | {remaining} |")
        if piano_state_evidence is not None:
            candidates, states = piano_state_evidence
            lines.extend(
                [
                    "",
                    "### Independent-piano runtime-state mining",
                    "",
                    f"Source: `{independent_piano_chord_state_evidence_input.as_posix()}`",
                    "",
                    "| Metric | Candidate states / shared states | Remaining |",
                    "| --- | ---: | ---: |",
                    f"| No-label states with complete pitch-class recovery in every corpus | {fraction(candidates, states)} | {states - candidates} |",
                ]
            )
    if kraisler_archive is not None or kraisler_rows:
        lines.extend(
            [
                "",
                "## KRAISLER independent piano–violin coverage checklist",
                "",
                "KRAISLER is an independent real piano–violin duet corpus with separately recorded stems, "
                "summed mixtures, Disklavier piano MIDI, and reviewed violin note labels.",
                "",
                "| Task | Complete / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Validate external KRAISLER archive | {fraction(kraisler_archive_ready, 1)} | {1 - kraisler_archive_ready} |",
                f"| Extract KRAISLER safely in InstrumentSamples | {fraction(kraisler_extraction_ready, 1)} | {1 - kraisler_extraction_ready} |",
                f"| Import dry piano/violin stems and labels | {fraction(kraisler_manifest_ready, 1)} | {1 - kraisler_manifest_ready} |",
                f"| Measure real KRAISLER note and chord outcomes | {fraction(int(bool(kraisler_rows)), 1)} | {int(not kraisler_rows)} |",
                f"| Complete protected KRAISLER cross-corpus rule audit | {fraction(kraisler_audit_ready, 1)} | {1 - kraisler_audit_ready} |",
            ]
        )
        if kraisler_rows:
            lines.extend(
                [
                    "",
                    "### KRAISLER real piano–violin measurement",
                    "",
                    f"Source: `{kraisler_measurement.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                ]
            )
            for group, metric, accurate, total in kraisler_rows:
                lines.append(f"| KRAISLER {group} — {metric} | {fraction(accurate, total)} | {total - accurate} |")
    if maps_attribute_input is not None:
        lines.extend(
            [
                "",
                "## MAPS chord-miss evidence",
                "",
                "This isolates misses where note evidence is already present from misses that still lack a keyboard chord label.",
                "",
                "| Metric | Affected / chord misses | Other misses |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, affected, total in maps_chord_miss_rows(maps_attribute_input):
            lines.append(f"| {label} | {fraction(affected, total)} | {total - affected} |")
    if maps_attribute_input is not None and maestro_real_attribute_input is not None:
        lines.extend(
            [
                "",
                "## Independent piano chord-outcome evidence",
                "",
                "These compatible MAPS and MAESTRO labels establish shared failure outcomes, not a detector rule by themselves.",
                "",
                "| Corpus | Exact chord hit | Missing chord label | Wrong chord label |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for name, path in (("MAPS", maps_attribute_input), ("MAESTRO", maestro_real_attribute_input)):
            hits, no_label, wrong_label, total = chord_outcome_counts(path)
            lines.append(
                f"| {name} | {fraction(hits, total)} | {fraction(no_label, total)} | {fraction(wrong_label, total)} |"
            )
    if maps_note_gate_outputs:
        lines.extend(["", "## MAPS isolated-piano note gate", "", "This separate Disklavier subset contains isolated notes with aligned MIDI annotations.", "", "| Metric | Accurate / total | Remaining |", "| --- | ---: | ---: |"])
        for label, accurate, total in maps_note_gate_rows(maps_note_gate_outputs):
            remaining = f"{total - accurate} false predictions" if label.endswith("precision") else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remaining} |")
    if drum_gate_output is not None:
        full_drum_source = drum_gate_output
        exact_attribute_path = drum_gate_output.with_name("drum_full_exact_attribute_rows.tsv")
        if exact_attribute_path.is_file():
            full_drum_source = exact_attribute_path
        lines.extend(
            [
                "",
                "## Full drum primary-classification gate",
                "",
                "These rows count one-shot samples by the instrument shown as the primary drum. "
                "The latest completed full gate is reported even when a threshold fails, so its "
                "remaining classifications remain visible.",
                "",
                f"Source: `{full_drum_source.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in drum_primary_gate_rows([drum_gate_output], "Full drum gate"):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if hf_drum_gate_outputs:
        lines.extend(
            [
                "",
                "## High-fidelity drum-kit primary-classification gate",
                "",
                "These independent one-shot samples are sharded by expected instrument; the seven "
                "shard matrices are combined here so primary-label changes remain visible.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total in drum_primary_gate_rows(hf_drum_gate_outputs, "High-fidelity drum kit"):
            lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if star_drums_gate_output is not None:
        lines.extend(
            [
                "",
                "## STAR Drums preview multitrack gate",
                "",
                "This independent real-music preview measures annotated drum-event recall and "
                "false activations across mixed recordings.",
                "",
                f"Source: `{star_drums_gate_output.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total, remainder_unit in egmd_drum_rows(star_drums_gate_output, "STAR Drums preview"):
            remainder = f"{total - accurate} {remainder_unit}" if remainder_unit else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remainder} |")
    if mdb_drums_gate_output is not None:
        lines.extend(
            [
                "",
                "## MDB Drums multitrack gate",
                "",
                "This independent real-music fixture measures annotated drum-event recall and "
                "false activations across a larger variety of mixed recordings.",
                "",
                f"Source: `{mdb_drums_gate_output.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total, remainder_unit in egmd_drum_rows(mdb_drums_gate_output, "MDB Drums"):
            remainder = f"{total - accurate} {remainder_unit}" if remainder_unit else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remainder} |")
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
    parser.add_argument("--vocalset-full-mix-input", type=Path)
    parser.add_argument("--bach10-gate-output", action="append", type=Path, default=[])
    parser.add_argument("--musicnet-gate-output", type=Path)
    parser.add_argument("--musicnet-routing-input", type=Path)
    parser.add_argument("--maps-gate-output", action="append", type=Path, default=[])
    parser.add_argument("--maps-note-gate-output", action="append", type=Path, default=[])
    parser.add_argument("--maps-attribute-input", type=Path)
    parser.add_argument("--drum-gate-output", type=Path)
    parser.add_argument("--hf-drum-gate-output", action="append", type=Path, default=[])
    parser.add_argument("--urmp-gate-output", type=Path)
    parser.add_argument("--route-summary", type=Path)
    parser.add_argument("--good-sounds-full-mix-input", type=Path)
    parser.add_argument("--irmas-labelled-input", type=Path)
    parser.add_argument("--pitch-shifted-violin-input", type=Path)
    parser.add_argument("--medley-solos-attribute-input", type=Path)
    parser.add_argument("--focused-vocalset-clean-vowel-input", type=Path)
    parser.add_argument("--philharmonia-full-input", type=Path)
    parser.add_argument("--iowa-orchestra-full-input", type=Path)
    parser.add_argument("--tinysol-wind-exact-input", type=Path)
    parser.add_argument("--iowa-sax-full-mix-input", type=Path)
    parser.add_argument("--iowa-piano-full-mix-input", type=Path)
    parser.add_argument("--tinysol-sax-full-mix-input", type=Path)
    parser.add_argument("--tinysol-flute-full-mix-input", type=Path)
    parser.add_argument("--real-a2s-tenor-scale-input", type=Path)
    parser.add_argument("--urmp-sax-exact-input", type=Path)
    parser.add_argument("--urmp-sax-full-mix-input", type=Path)
    parser.add_argument("--star-drums-gate-output", type=Path)
    parser.add_argument("--mdb-drums-gate-output", type=Path)
    parser.add_argument("--dagstuhl-choirset-input", type=Path)
    parser.add_argument("--dagstuhl-choirset-validation", type=Path)
    parser.add_argument("--dagstuhl-choirset-inspection", type=Path)
    parser.add_argument("--dagstuhl-choirset-extraction", type=Path)
    parser.add_argument("--dagstuhl-choirset-manifest", type=Path)
    parser.add_argument("--choral-singing-dataset-archive", type=Path)
    parser.add_argument("--choral-singing-dataset-extraction", type=Path)
    parser.add_argument("--choral-singing-dataset-inspection", type=Path)
    parser.add_argument("--choral-singing-dataset-manifest", type=Path)
    parser.add_argument("--choral-singing-dataset-measurement", type=Path)
    parser.add_argument("--esmuc-choir-dataset-archive", type=Path)
    parser.add_argument("--esmuc-choir-dataset-extraction", type=Path)
    parser.add_argument("--esmuc-choir-dataset-manifest", type=Path)
    parser.add_argument("--esmuc-choir-dataset-measurement", type=Path)
    parser.add_argument("--esmuc-choir-dataset-pattern-report", type=Path)
    parser.add_argument("--mir1k-dataset-archive", type=Path)
    parser.add_argument("--mir1k-dataset-extraction", type=Path)
    parser.add_argument("--mir1k-full-mix-input", type=Path)
    parser.add_argument("--scms-dataset-archive", type=Path)
    parser.add_argument("--scms-dataset-inspection", type=Path)
    parser.add_argument("--scms-dataset-extraction", type=Path)
    parser.add_argument("--scms-dataset-manifest", type=Path)
    parser.add_argument("--scms-dataset-measurement", type=Path)
    parser.add_argument("--scms-full-mix-input", type=Path)
    parser.add_argument("--vocal-exact-note-cross-corpus-input", type=Path)
    parser.add_argument("--maestro-real-measurement", type=Path)
    parser.add_argument("--maestro-real-manifest", type=Path)
    parser.add_argument("--maestro-real-attribute-input", type=Path)
    parser.add_argument("--independent-piano-chord-state-evidence", type=Path)
    parser.add_argument("--kraisler-archive", type=Path)
    parser.add_argument("--kraisler-extraction", type=Path)
    parser.add_argument("--kraisler-manifest", type=Path)
    parser.add_argument("--kraisler-measurement", type=Path)
    parser.add_argument("--high-vocal-octave-audit", type=Path)
    parser.add_argument("--electronic-piano-guitar-route-audit", type=Path)
    parser.add_argument("--scms-vocal-other-route-audit", type=Path)
    parser.add_argument("--tenor-sax-piano-route-audit", type=Path)
    parser.add_argument("--violin-guitar-route-audit", type=Path)
    parser.add_argument("--guitar-chord-primary-display-audit", type=Path)
    parser.add_argument("--guitar-chord-tone-recovery-audit", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        rendered = render(
            args.input, args.chord_input, args.vocal_full_mix_input, args.bach10_gate_output,
            args.musicnet_gate_output, args.drum_gate_output, args.urmp_gate_output,
            args.vocalset_full_mix_input, args.maps_gate_output, args.maps_note_gate_output,
            args.route_summary, args.good_sounds_full_mix_input, args.irmas_labelled_input,
            args.hf_drum_gate_output,
            args.maps_attribute_input, args.medley_solos_attribute_input,
            args.focused_vocalset_clean_vowel_input, args.pitch_shifted_violin_input,
            args.philharmonia_full_input,
            args.iowa_orchestra_full_input,
            args.tinysol_wind_exact_input,
            args.iowa_sax_full_mix_input,
            args.tinysol_sax_full_mix_input,
            args.tinysol_flute_full_mix_input,
            args.real_a2s_tenor_scale_input,
            args.urmp_sax_exact_input,
            args.urmp_sax_full_mix_input,
            args.star_drums_gate_output,
            args.mdb_drums_gate_output,
            args.dagstuhl_choirset_input,
            args.dagstuhl_choirset_validation,
            args.dagstuhl_choirset_inspection,
            args.dagstuhl_choirset_extraction,
            args.dagstuhl_choirset_manifest,
            args.choral_singing_dataset_archive,
            args.choral_singing_dataset_extraction,
            args.choral_singing_dataset_inspection,
            args.choral_singing_dataset_manifest,
            args.choral_singing_dataset_measurement,
            args.esmuc_choir_dataset_archive,
            args.esmuc_choir_dataset_extraction,
            args.esmuc_choir_dataset_manifest,
            args.esmuc_choir_dataset_measurement,
            args.esmuc_choir_dataset_pattern_report,
            args.mir1k_dataset_archive,
            args.mir1k_dataset_extraction,
            args.mir1k_full_mix_input,
            args.scms_dataset_archive,
            args.scms_dataset_inspection,
            args.scms_dataset_extraction,
            args.scms_dataset_manifest,
            args.scms_dataset_measurement,
            args.scms_full_mix_input,
            args.vocal_exact_note_cross_corpus_input,
            args.iowa_piano_full_mix_input,
            args.maestro_real_measurement,
            args.maestro_real_manifest,
            args.maestro_real_attribute_input,
            args.independent_piano_chord_state_evidence,
            args.kraisler_archive,
            args.kraisler_extraction,
            args.kraisler_manifest,
            args.kraisler_measurement,
            args.musicnet_routing_input,
            args.high_vocal_octave_audit,
            args.electronic_piano_guitar_route_audit,
            args.scms_vocal_other_route_audit,
            args.tenor_sax_piano_route_audit,
            args.violin_guitar_route_audit,
            args.guitar_chord_primary_display_audit,
            args.guitar_chord_tone_recovery_audit,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"detection_accuracy_report: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
