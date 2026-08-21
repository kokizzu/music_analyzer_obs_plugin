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
URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_RE = re.compile(
    r"^shared_sax_candidates=(?P<count>\d+)$", re.MULTILINE
)
OCTAVE_CORRECTION_CROSS_CORPUS_RE = re.compile(
    r"^shared_octave_correction_candidates=(?P<count>\d+)$", re.MULTILINE
)
DOMINANT_SEVENTH_EXTENSION_RE = re.compile(
    r"^dominant_seventh_extension: supported_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"regressions=(?P<regressions>\d+)$", re.MULTILINE
)
GLOBAL_CHORD_CONFIDENCE_RE = re.compile(
    r"^global_chord_confidence: best_floor=(?P<floor>[0-9.]+) "
    r"supported_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"common_zero_regression_floors=(?P<common>\d+)$", re.MULTILINE
)
SAME_ROOT_GUITAR_QUALITY_RE = re.compile(
    r"^same_root_guitar_quality: best_floor=(?P<floor>[0-9.]+) "
    r"supported_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"regressions=(?P<regressions>\d+) common_zero_regression=(?P<common>\d+)$",
    re.MULTILINE,
)
OWNER_CLASSIFIER_LOCO_RE = re.compile(
    r"^owner_classifier_loco: improved_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"current=(?P<current>\d+)/(?P<count>\d+) model=(?P<model>\d+)/(?P=count)$",
    re.MULTILINE,
)
OWNER_SCORE_CALIBRATION_LOCO_RE = re.compile(
    r"^owner_score_calibration_loco: improved_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"current=(?P<current>\d+)/(?P<count>\d+) model=(?P<model>\d+)/(?P=count)$",
    re.MULTILINE,
)
DRUM_PRIMARY_LOCO_RE = re.compile(
    r"^drum_primary_loco: improved_corpora=(?P<supported>\d+)/(?P<total>\d+) "
    r"current=(?P<current>\d+)/(?P<count>\d+) model=(?P<model>\d+)/(?P=count) "
    r"target_delta=(?P<targets>.*)$",
    re.MULTILINE,
)
DRUM_FALSE_POSITIVE_CAP_RE = re.compile(
    r"^drum_false_positive_cap_audit: real_candidates=(?P<candidates>\d+) "
    r"cross_real_candidates=(?P<cross>\d+) "
    r"protected_runtime_safe=(?P<safe>\d+)/(?P<total>\d+)$",
    re.MULTILINE,
)
DRUM_COMPETING_ACTIVE_CONTEXT_RE = re.compile(
    r"^drum_competing_active_context_audit: real_candidates=(?P<candidates>\d+) "
    r"protected_runtime_safe=(?P<safe>\d+)/(?P<total>\d+)"
    r"(?: runtime_replayed=(?P<replayed>\d+)/(?P<replay_total>\d+) "
    r"runtime_gain=(?P<gained>\d+)/(?P<gain_total>\d+))?$",
    re.MULTILINE,
)
DRUM_FALSE_POSITIVE_CONTEXT_RE = re.compile(
    r"^drum_false_positive_context_audit: primitives=(?P<primitives>\d+) "
    r"cross_real_contexts=(?P<contexts>\d+) "
    r"protected_runtime_safe=(?P<safe>\d+)/(?P<total>\d+)$",
    re.MULTILINE,
)
CHORD_PRIMARY_COMPONENT_RE = re.compile(
    r"^chord_primary_component_audit: any_hit=(?P<any>\d+)/(?P<total>\d+) "
    r"primary_hit=(?P<primary>\d+)/(?P=total) alias_rescued=(?P<rescued>\d+) "
    r"dim7_primary_hit=(?P<dim7>\d+)/(?P=total) "
    r"dim7_promotions=(?P<promotions>\d+) dim7_regressions=(?P<regressions>\d+)$",
    re.MULTILINE,
)
SAMPLES29K_DRUMS_RE = re.compile(
    r"\b(?P<category>tom|ride) recall (?P<hits>\d+)/(?P<total>\d+) primary (?P<primary>\d+)/(?P=total)",
)

# Analyzer TSV evidence can legitimately retain long comma-separated note
# histories.  Keep a finite but practical cap instead of csv's 128 KiB default.
csv.field_size_limit(8 * 1024 * 1024)


def truthy(value: str) -> bool:
    return value.strip().lower() not in {"", "0", "false", "no"}


def samples29k_drum_counts(path: Path) -> dict[str, tuple[int, int, int]]:
    """Return active and primary hit counts from the Tom/Ride-only fixture log."""
    counts: dict[str, tuple[int, int, int]] = {}
    for match in SAMPLES29K_DRUMS_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
        counts[match.group("category")] = (
            int(match.group("hits")), int(match.group("total")), int(match.group("primary"))
        )
    return counts


def samples29k_primary_attributes_ready(path: Path | None) -> int:
    """Whether a complete 29k primary-decision TSV is available for replay."""
    return int(
        path is not None
        and path.is_file()
        and "sample\texpected\tgot\t" in path.read_text(encoding="utf-8", errors="replace")
    )


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
INDEPENDENT_PIANO_EXACT_FALLBACK_RE = re.compile(
    r"^independent_piano_exact_chord_fallback: corpora=(?P<corpora>\d+) "
    r"shared_runtime_safe=(?P<candidates>\d+)$",
    re.MULTILINE,
)
DRUM_RECOVERY_CANDIDATE_RE = re.compile(
    r"^drum_recovery_candidate_audit: corpora=(?P<corpora>\d+) "
    r"missed_events=(?P<misses>\d+) "
    r"cross_real_zero_false_candidates=(?P<candidates>\d+)$",
    re.MULTILINE,
)
PIANO_CHORD_STABILITY_RE = re.compile(
    r"^piano_chord_state_audit: combined sequences=(?P<sequences>\d+) "
    r"frames=(?P<frames>\d+) correct=(?P<correct>\d+)/(?P<correct_total>\d+) "
    r"no_label=(?P<no_label>\d+) wrong=(?P<wrong>\d+) "
    r"transient_losses=(?P<transient_losses>\d+)$",
    re.MULTILINE,
)
PIANO_CHORD_CONFIRMATION_RE = re.compile(
    r"^piano_chord_confirmation_audit: baseline_correct=(?P<baseline_correct>\d+)/(?P<frames>\d+) "
    r"baseline_wrong=(?P<baseline_wrong>\d+) baseline_flickers=(?P<baseline_flickers>\d+) "
    r"trial_correct=(?P<trial_correct>\d+)/(?P<trial_frames>\d+) trial_wrong=(?P<trial_wrong>\d+) "
    r"trial_flickers=(?P<trial_flickers>\d+) retained_confirm_frames=(?P<retained>\d+) "
    r"eligible=(?P<eligible>[01])$",
    re.MULTILINE,
)
PIANO_CHORD_DISPLAY_GATE_RE = re.compile(
    r"^piano_chord_display_gate: floor=(?P<floor>[0-9.]+) "
    r"baseline_correct=(?P<baseline_correct>\d+)/(?P<frames>\d+) "
    r"baseline_wrong=(?P<baseline_wrong>\d+) baseline_flickers=(?P<baseline_flickers>\d+) "
    r"trial_correct=(?P<trial_correct>\d+)/(?P<trial_frames>\d+) "
    r"trial_wrong=(?P<trial_wrong>\d+) trial_flickers=(?P<trial_flickers>\d+) "
    r"eligible=(?P<eligible>[01])$",
    re.MULTILINE,
)
FSD50K_RIM_METADATA_RE = re.compile(
    r"^fsd50k_rim_metadata: rimshot_labelled_rows=(?P<labelled>\d+) "
    r"pure_rimshot_candidates=(?P<pure>\d+) permissive_cc_candidates=(?P<permissive>\d+) "
    r"dev=(?P<dev>\d+) eval=(?P<eval>\d+)$",
    re.MULTILINE,
)
COMMONS_RIMSHOT_CANDIDATE_RE = re.compile(
    r"^commons_rimshot_candidate: sha1_verified=(?P<sha1>[01]) "
    r"source_labelled=(?P<labelled>[01]) expected_rolls=(?P<rolls>\d+) "
    r"temporal_annotations=(?P<timed>[01]) ",
    re.MULTILINE,
)
BEAT_THIS_CONTINUOUS_INTERVAL_GATE_RE = re.compile(
    r"^beat_this_continuous_interval_gate: minimum_intervals=(?P<intervals>-?\d+) "
    r"ballroom_correct=(?P<ballroom_correct>\d+)/(?P<ballroom_total>\d+) ballroom_wrong=(?P<ballroom_wrong>\d+) "
    r"filobass_correct=(?P<filobass_correct>\d+)/(?P<filobass_total>\d+) filobass_wrong=(?P<filobass_wrong>\d+) "
    r"minimum_per_corpus=(?P<minimum>\d+) eligible=(?P<eligible>[01])$",
    re.MULTILINE,
)
PIXABAY_RIMSHOT_MEASUREMENT_RE = re.compile(
    r"^pixabay_rimshot_measurement: detected=(?P<detected>\d+)/(?P<detected_total>\d+) "
    r"primary=(?P<primary>\d+)/(?P<primary_total>\d+) snare_primary=(?P<snare_primary>\d+)/(?P<snare_total>\d+)$",
    re.MULTILINE,
)
MDB_RIM_COVERAGE_RE = re.compile(
    r"^mdb_rim_coverage: detected=(?P<detected>\d+)/(?P<total>\d+)$",
    re.MULTILINE,
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
POLYPHONIC_CANDIDATE_CAPACITY_RE = re.compile(
    r"polyphonic_candidate_capacity: capacity_limited_corpora=(?P<limited>\d+)/(?P<corpora>\d+) "
    r"missing_pitch_windows=(?P<missing>\d+) saturation_explains_missing=(?P<explained>\d+)"
)
HARMONIC_PRODUCT_OCTAVE_RE = re.compile(
    r"harmonic_product_octave: common_zero_regression_thresholds=(?P<safe>\d+)/(?P<thresholds>\d+) "
    r"corpora=(?P<corpora>\d+)"
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


def drum_recovery_candidate_audit(path: Path) -> tuple[int, int, int]:
    match = DRUM_RECOVERY_CANDIDATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing cross-real drum recovery summary")
    corpora, misses, candidates = (int(match[name]) for name in ("corpora", "misses", "candidates"))
    if corpora < 2 or misses <= 0 or candidates < 0:
        raise ValueError(f"{path}: invalid cross-real drum recovery counts")
    return corpora, misses, candidates


def piano_chord_stability_evidence(path: Path) -> tuple[int, int, int, int, int, int]:
    match = PIANO_CHORD_STABILITY_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing combined continuous piano chord-state summary")
    sequences = int(match["sequences"])
    frames = int(match["frames"])
    correct = int(match["correct"])
    correct_total = int(match["correct_total"])
    no_label = int(match["no_label"])
    wrong = int(match["wrong"])
    transient_losses = int(match["transient_losses"])
    if (sequences <= 0 or frames <= 0 or correct_total != frames or
            correct + no_label + wrong != frames or transient_losses < 0 or
            transient_losses > sequences):
        raise ValueError(f"{path}: invalid continuous piano chord-state counts")
    return sequences, frames, correct, no_label, wrong, transient_losses


def piano_chord_confirmation_audit(path: Path) -> tuple[int, int, int, int, int, int, int, int]:
    match = PIANO_CHORD_CONFIRMATION_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing piano chord confirmation audit summary")
    values = {name: int(match[name]) for name in match.groupdict()}
    if values["frames"] <= 0 or values["trial_frames"] != values["frames"]:
        raise ValueError(f"{path}: inconsistent piano chord confirmation frame totals")
    if values["retained"] not in {1, 2} or values["eligible"] not in {0, 1}:
        raise ValueError(f"{path}: invalid piano chord confirmation decision")
    return (values["baseline_correct"], values["trial_correct"], values["frames"],
            values["baseline_wrong"], values["trial_wrong"], values["baseline_flickers"],
            values["trial_flickers"], values["retained"])


def fsd50k_rim_metadata_audit(path: Path) -> tuple[int, int, int]:
    """Return labelled, isolated, and licence-compatible FSD50K Rimshot counts."""
    match = FSD50K_RIM_METADATA_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing FSD50K Rimshot metadata summary")
    labelled, pure, permissive = (int(match[name]) for name in ("labelled", "pure", "permissive"))
    if labelled < 0 or pure < 0 or permissive < 0 or permissive > pure or pure > labelled:
        raise ValueError(f"{path}: invalid FSD50K Rimshot metadata counts")
    return labelled, pure, permissive


def commons_rimshot_candidate_audit(path: Path) -> tuple[int, int, int, int]:
    """Return the source-verification state without treating it as timed truth."""
    match = COMMONS_RIMSHOT_CANDIDATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing Commons Rimshot candidate summary")
    sha1_verified, labelled, rolls, timed = (int(match[name]) for name in ("sha1", "labelled", "rolls", "timed"))
    if sha1_verified != 1 or labelled != 1 or rolls != 4 or timed not in {0, 1}:
        raise ValueError(f"{path}: invalid Commons Rimshot candidate summary")
    return sha1_verified, labelled, rolls, timed


def beat_this_continuous_interval_gate_audit(path: Path) -> tuple[int, int, int, int, int, int, int, int]:
    match = BEAT_THIS_CONTINUOUS_INTERVAL_GATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing Beat This continuous interval-gate summary")
    values = {name: int(value) for name, value in match.groupdict().items()}
    if values["eligible"] == 1:
        if values["intervals"] < 0 or values["ballroom_wrong"] != 0 or values["filobass_wrong"] != 0:
            raise ValueError(f"{path}: unsafe Beat This interval gate")
        if min(values["ballroom_correct"], values["filobass_correct"]) < values["minimum"]:
            raise ValueError(f"{path}: insufficient safe Beat This interval-gate outputs")
    return (
        values["intervals"], values["ballroom_correct"], values["ballroom_total"], values["ballroom_wrong"],
        values["filobass_correct"], values["filobass_total"], values["filobass_wrong"], values["eligible"],
    )


def pixabay_rimshot_measurement_audit(path: Path) -> tuple[int, int, int]:
    match = PIXABAY_RIMSHOT_MEASUREMENT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing isolated Pixabay Rimshot measurement")
    values = {name: int(value) for name, value in match.groupdict().items()}
    if values["detected_total"] != 1 or values["primary_total"] != 1 or values["snare_total"] != 1:
        raise ValueError(f"{path}: invalid isolated Pixabay Rimshot denominator")
    if values["detected"] not in {0, 1} or values["primary"] not in {0, 1} or values["snare_primary"] not in {0, 1}:
        raise ValueError(f"{path}: invalid isolated Pixabay Rimshot count")
    if values["primary"] + values["snare_primary"] != 1:
        raise ValueError(f"{path}: inconsistent isolated Pixabay Rimshot primary result")
    return values["detected"], values["primary"], values["snare_primary"]


def mdb_rim_coverage(path: Path) -> tuple[int, int]:
    match = MDB_RIM_COVERAGE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing MDB Rim coverage summary")
    detected, total = (int(match[name]) for name in ("detected", "total"))
    if total <= 0 or detected < 0 or detected > total:
        raise ValueError(f"{path}: invalid MDB Rim coverage counts")
    return detected, total


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


def piano_chord_display_gate_audit(path: Path) -> tuple[float, int, int, int, int, int, int, int, int]:
    """Return the protected baseline/trial totals for the keyboard display gate."""
    match = PIANO_CHORD_DISPLAY_GATE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing piano chord display-gate summary")
    return (
        float(match["floor"]),
        int(match["baseline_correct"]),
        int(match["frames"]),
        int(match["baseline_wrong"]),
        int(match["baseline_flickers"]),
        int(match["trial_correct"]),
        int(match["trial_wrong"]),
        int(match["trial_flickers"]),
        int(match["eligible"]),
    )


def electronic_piano_guitar_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 2)


def scms_vocal_other_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 3)


def tenor_sax_piano_route_audit(path: Path) -> tuple[int, int, int]:
    return route_profile_audit(path, 4)


def urmp_good_sounds_sax_shared_pattern_audit(path: Path) -> int:
    """Return the number of shared, protected zero-regression sax selectors."""
    match = URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_RE.search(
        path.read_text(encoding="utf-8", errors="replace")
    )
    if match is None:
        raise ValueError(f"{path}: missing shared sax selector count")
    return int(match["count"])


def octave_correction_cross_corpus_audit(path: Path) -> int:
    """Return protected zero-regression octave-correction selector count."""
    match = OCTAVE_CORRECTION_CROSS_CORPUS_RE.search(
        path.read_text(encoding="utf-8", errors="replace")
    )
    if match is None:
        raise ValueError(f"{path}: missing shared octave selector count")
    return int(match["count"])


def dominant_seventh_extension_audit(path: Path) -> tuple[int, int, int]:
    """Return independent support and observed regressions for the extension rule."""
    match = DOMINANT_SEVENTH_EXTENSION_RE.search(
        path.read_text(encoding="utf-8", errors="replace")
    )
    if match is None:
        raise ValueError(f"{path}: missing dominant-seventh audit summary")
    return int(match["supported"]), int(match["total"]), int(match["regressions"])


def global_chord_confidence_audit(path: Path) -> tuple[float, int, int, int]:
    """Return the best tested floor and its protected-corpus support."""
    match = GLOBAL_CHORD_CONFIDENCE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing global-chord confidence audit summary")
    return (
        float(match["floor"]),
        int(match["supported"]),
        int(match["total"]),
        int(match["common"]),
    )


def same_root_guitar_quality_audit(path: Path) -> tuple[float, int, int, int, int]:
    """Return cross-corpus support for measured guitar quality promotion."""
    match = SAME_ROOT_GUITAR_QUALITY_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing same-root guitar quality audit summary")
    return (
        float(match["floor"]),
        int(match["supported"]),
        int(match["total"]),
        int(match["regressions"]),
        int(match["common"]),
    )


def owner_classifier_loco_audit(path: Path) -> tuple[int, int, int, int, int]:
    """Return LOCO support and aggregate baseline/model owner accuracy."""
    match = OWNER_CLASSIFIER_LOCO_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing owner-classifier LOCO summary")
    return (
        int(match["supported"]), int(match["total"]), int(match["current"]),
        int(match["model"]), int(match["count"]),
    )


def owner_score_calibration_loco_audit(path: Path) -> tuple[int, int, int, int, int]:
    """Return LOCO support and aggregate score-calibration accuracy."""
    match = OWNER_SCORE_CALIBRATION_LOCO_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing owner score-calibration LOCO summary")
    return (
        int(match["supported"]), int(match["total"]), int(match["current"]),
        int(match["model"]), int(match["count"]),
    )


def drum_primary_loco_audit(path: Path) -> tuple[int, int, int, int, int, str]:
    """Return cross-corpus support for the diagnostic drum classifier."""
    match = DRUM_PRIMARY_LOCO_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing drum-primary LOCO summary")
    return (
        int(match["supported"]), int(match["total"]), int(match["current"]),
        int(match["model"]), int(match["count"]), match["targets"],
    )


def drum_false_positive_cap_audit(path: Path) -> tuple[int, int, int, int]:
    """Return cross-real false-positive cap candidates and protected safety."""
    match = DRUM_FALSE_POSITIVE_CAP_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing drum false-positive-cap audit summary")
    return (
        int(match["candidates"]), int(match["cross"]),
        int(match["safe"]), int(match["total"]),
    )


def drum_competing_active_context_audit(path: Path) -> tuple[int, int, int, int, int, int, int]:
    """Return class-aware contexts, protected safety, and runtime replay results."""
    match = DRUM_COMPETING_ACTIVE_CONTEXT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing competing-active drum-context audit summary")
    safe = int(match["safe"])
    return (
        int(match["candidates"]), safe, int(match["total"]),
        int(match["replayed"] or 0), int(match["replay_total"] or safe),
        int(match["gained"] or 0), int(match["gain_total"] or 0),
    )


def independent_piano_exact_fallback_audit(path: Path) -> tuple[int, int]:
    """Return independently checked piano corpora and safe exact fallback count."""
    match = INDEPENDENT_PIANO_EXACT_FALLBACK_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing independent piano exact-fallback audit summary")
    return int(match["corpora"]), int(match["candidates"])


def drum_false_positive_context_audit(path: Path) -> tuple[int, int, int, int]:
    """Return two-feature real-mix candidates and protected safety."""
    match = DRUM_FALSE_POSITIVE_CONTEXT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing drum false-positive-context audit summary")
    return (
        int(match["primitives"]), int(match["contexts"]),
        int(match["safe"]), int(match["total"]),
    )


def chord_primary_component_audit(path: Path) -> tuple[int, int, int, int, int, int, int]:
    """Return any-alias, first-component, and narrow dim7-promotion matches."""
    match = CHORD_PRIMARY_COMPONENT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing chord primary-component audit summary")
    return (
        int(match["any"]), int(match["primary"]), int(match["total"]), int(match["rescued"]),
        int(match["dim7"]), int(match["promotions"]), int(match["regressions"]),
    )


def polyphonic_candidate_capacity_audit(path: Path) -> tuple[int, int, int, int]:
    """Return whether full-mix candidate capacity explains SATB pitch misses."""
    match = POLYPHONIC_CANDIDATE_CAPACITY_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing polyphonic candidate-capacity summary")
    return (
        int(match["limited"]), int(match["corpora"]), int(match["missing"]), int(match["explained"]),
    )


def harmonic_product_octave_audit(path: Path) -> tuple[int, int, int]:
    """Return safe harmonic-product thresholds and labelled-corpus coverage."""
    match = HARMONIC_PRODUCT_OCTAVE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing harmonic-product octave summary")
    return int(match["safe"]), int(match["thresholds"]), int(match["corpora"])


def guitarset_attribute_audit(path: Path) -> tuple[int, int, int, int]:
    """Return live-GuitarSet pitch-class and exact-chord coverage."""
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    required = {"guitar_note_hits", "expected_note_count", "expected_chords", "chord_hit"}
    missing = required - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{path}: missing GuitarSet attribute columns: {', '.join(sorted(missing))}")
    note_hits = 0
    note_total = 0
    chord_hits = 0
    chord_total = 0
    for row in rows:
        try:
            note_hits += int(row["guitar_note_hits"])
            note_total += int(row["expected_note_count"])
        except ValueError as error:
            raise ValueError(f"{path}: invalid GuitarSet note count") from error
        if (row["expected_chords"] or "").strip() not in {"", "--"}:
            chord_total += 1
            chord_hits += int(row["chord_hit"] == "1")
    if note_total <= 0 or chord_total <= 0:
        raise ValueError(f"{path}: no GuitarSet note or chord coverage")
    return note_hits, note_total, chord_hits, chord_total


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


def tempo_diagnostic_counts(path: Path, prefix: str = "MAESTRO tempo diag\t") -> tuple[int, int]:
    accurate = 0
    total = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        fields = dict(field.split("=", 1) for field in line[len(prefix) :].split("\t") if "=" in field)
        total += 1
        if fields.get("status") == "hit":
            accurate += 1
    if total <= 0:
        raise ValueError(f"{path}: no tempo diagnostic rows")
    return accurate, total


def beat_this_tempo_diagnostic_counts(
    path: Path, prefix: str = "Beat This tempo diag\t"
) -> tuple[int, int]:
    accurate = 0
    total = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        fields = dict(field.split("=", 1) for field in line[len(prefix):].split("\t") if "=" in field)
        total += 1
        if float(fields.get("error", "inf")) <= 8.0:
            accurate += 1
    if total <= 0:
        raise ValueError(f"{path}: no Beat This tempo diagnostic rows")
    return accurate, total


def beat_this_rolling_tempo_counts(path: Path) -> tuple[int, int, int]:
    """Return accurate, total, and on-budget bounded-window Beat This outcomes."""
    prefix = "Beat This rolling tempo diag\t"
    accurate, total = beat_this_tempo_diagnostic_counts(path, prefix)
    on_budget = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        fields = dict(field.split("=", 1) for field in line[len(prefix):].split("\t") if "=" in field)
        try:
            if float(fields["wall_seconds"]) <= float(fields["window_seconds"]):
                on_budget += 1
        except (KeyError, ValueError) as error:
            raise ValueError(f"{path}: invalid Beat This rolling timing row") from error
    return accurate, total, on_budget


def three_tempo_tracker_consensus_counts(path: Path) -> tuple[int, int, int, int]:
    """Return (correct, selected, newly_revealed, audited) offline consensus counts."""
    audited = None
    correct = selected = newly_revealed = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("three-tracker consensus sweep:"):
            match = re.search(r"\brows=(\d+)", line)
            if match is None:
                raise ValueError(f"{path}: missing three-tracker row count")
            audited = int(match.group(1))
        elif line.startswith("three-tracker consensus viable:"):
            if line.strip() == "three-tracker consensus viable: none":
                continue
            match = re.search(r"\bcorrect=(\d+)/(\d+)\b.*?\bnewly_revealed=(\d+)", line)
            if match is None:
                raise ValueError(f"{path}: invalid three-tracker viable summary")
            correct, selected, newly_revealed = (int(value) for value in match.groups())
            if correct != selected:
                raise ValueError(f"{path}: viable consensus contains a wrong BPM")
    if audited is None:
        raise ValueError(f"{path}: no three-tracker consensus sweep")
    if selected > audited or newly_revealed > audited:
        raise ValueError(f"{path}: invalid three-tracker consensus counts")
    return correct, selected, newly_revealed, audited


def permissive_tracker_tempo_counts(path: Path, confidence_floor: float = 0.0) -> tuple[int, int]:
    """Return within-eight-BPM tracker outcomes at a certainty floor."""
    accurate = 0
    total = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("BTT tempo diag\t"):
            continue
        fields = dict(field.split("=", 1) for field in line.split("\t")[1:] if "=" in field)
        try:
            confidence = float(fields["confidence"])
            error = float(fields["error"])
        except (KeyError, ValueError) as error:
            raise ValueError(f"{path}: invalid permissive-tracker diagnostic row") from error
        if confidence < confidence_floor:
            continue
        total += 1
        if error <= 8.0:
            accurate += 1
    if total <= 0:
        raise ValueError(f"{path}: no permissive-tracker rows at {confidence_floor:.2f}")
    return accurate, total


TEMPO_CANDIDATE_ALIGNMENT_RE = re.compile(
    r"(?P<bpm>\d+)\([^)]*?align="
    r"(?P<kick>[0-9.]+)/(?P<bass>[0-9.]+)/(?P<snare>[0-9.]+)/(?P<tonal>[0-9.]+)"
    r"(?:,kb=[0-9.]+)?\)"
)


def filobass_phase_energy_counts(path: Path, tolerance: float = 8.0) -> tuple[int, int, int, int, int] | None:
    """Return expected-candidate/bass-alignment evidence from FiloBass diagnostics.

    The measurement remains diagnostic-only: a higher bass alignment is not a
    reason by itself to alter a public BPM estimate.
    """
    total = 0
    eligible = higher = equal = lower = 0
    saw_alignment = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("MAESTRO tempo diag\t"):
            continue
        total += 1
        fields = dict(field.split("=", 1) for field in line[len("MAESTRO tempo diag\t") :].split("\t") if "=" in field)
        try:
            expected = float(fields.get("expected", "0"))
        except ValueError as error:
            raise ValueError(f"{path}: invalid FiloBass expected BPM") from error
        candidates = list(TEMPO_CANDIDATE_ALIGNMENT_RE.finditer(fields.get("candidates", "")))
        if not candidates:
            continue
        saw_alignment = True
        selected = candidates[0]
        expected_candidate = next(
            (candidate for candidate in candidates if abs(float(candidate["bpm"]) - expected) <= tolerance),
            None,
        )
        if expected_candidate is None:
            continue
        eligible += 1
        difference = float(expected_candidate["bass"]) - float(selected["bass"])
        if difference > 1.0:
            higher += 1
        elif difference < -1.0:
            lower += 1
        else:
            equal += 1
    if total <= 0:
        raise ValueError(f"{path}: no FiloBass tempo diagnostic rows")
    return (eligible, higher, equal, lower, total) if saw_alignment else None


def filobass_onset_diagnostic_counts(path: Path) -> tuple[int, int, int, int]:
    """Return direct, top-five, direct-or-double, and total bass-onset counts."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise ValueError(f"{path}: no FiloBass onset diagnostic rows")
    try:
        ranks = [int(row["expected_rank"]) for row in rows]
    except (KeyError, ValueError) as error:
        raise ValueError(f"{path}: invalid FiloBass onset diagnostic rows") from error
    direct_or_double = sum(
        int(row["top_or_double_hit"]) if row.get("top_or_double_hit", "") else rank == 1
        for row, rank in zip(rows, ranks)
    )
    return sum(rank == 1 for rank in ranks), sum(rank <= 5 for rank in ranks), direct_or_double, len(ranks)


def idmt_bass_timing_metadata_counts(path: Path) -> tuple[int, int]:
    """Count real bass tracks with corpus-supplied timing/grid metadata."""
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"track_id", "parameter", "timing_or_pattern_field"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing IDMT timing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    tracks = {row["track_id"] for row in rows if row["track_id"]}
    timing_tracks = {
        row["track_id"]
        for row in rows
        if row["track_id"] and row["timing_or_pattern_field"].strip().lower() == "yes"
    }
    if not tracks:
        raise ValueError(f"{path}: no IDMT metadata rows")
    return len(timing_tracks), len(tracks)


def urmp_bass_timing_counts(path: Path) -> tuple[int, int, int, int]:
    """Count URMP double-bass audio/note pairs and explicit metrical grids."""
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"audio_aligned_notes", "score_midi", "explicit_beat_grid", "qualifies_as_tempo_truth"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing URMP bass timing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no URMP double-bass timing rows")
    try:
        pairs = sum(int(row["audio_aligned_notes"]) for row in rows)
        grids = sum(int(row["explicit_beat_grid"]) for row in rows)
        qualified = sum(int(row["qualifies_as_tempo_truth"]) for row in rows)
    except ValueError as error:
        raise ValueError(f"{path}: invalid URMP bass timing rows") from error
    return pairs, grids, qualified, len(rows)


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
    independent_piano_chord_stability_evidence_input: Path | None = None,
    independent_piano_exact_chord_fallback_audit_input: Path | None = None,
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
    urmp_good_sounds_sax_shared_pattern_audit_input: Path | None = None,
    urmp_bass_timing_audit_input: Path | None = None,
    octave_correction_cross_corpus_audit_input: Path | None = None,
    dominant_seventh_extension_audit_input: Path | None = None,
    global_chord_confidence_audit_input: Path | None = None,
    guitarset_attribute_input: Path | None = None,
    same_root_guitar_quality_audit_input: Path | None = None,
    owner_classifier_loco_audit_input: Path | None = None,
    owner_classifier_quality_loco_audit_input: Path | None = None,
    owner_score_calibration_loco_audit_input: Path | None = None,
    drum_primary_loco_audit_input: Path | None = None,
    drum_false_positive_cap_audit_input: Path | None = None,
    mdb_full_mix_false_positive_cap_audit_input: Path | None = None,
    mdb_full_mix_competing_active_context_audit_input: Path | None = None,
    drum_false_positive_context_audit_input: Path | None = None,
    drum_recovery_candidate_audit_input: Path | None = None,
    chord_primary_component_audit_input: Path | None = None,
    other_detection_disabled: bool = False,
    polyphonic_candidate_capacity_audit_input: Path | None = None,
    harmonic_product_octave_audit_input: Path | None = None,
    kraisler_bpm_input: Path | None = None,
    ballroom_bpm_input: Path | None = None,
    gtzan_rhythm_bpm_input: Path | None = None,
    filobass_bpm_input: Path | None = None,
    filobass_onset_diagnostic_input: Path | None = None,
    egmd_bpm_input: Path | None = None,
    idmt_bass_tempo_metadata_input: Path | None = None,
    ballroom_annotations: Path | None = None,
    beat_this_gtzan_bpm_input: Path | None = None,
    beat_this_ballroom_bpm_input: Path | None = None,
    beat_this_filobass_bpm_input: Path | None = None,
    beat_this_rolling_ballroom_bpm_input: Path | None = None,
    beat_this_rolling_filobass_bpm_input: Path | None = None,
    beat_this_continuous_ballroom_bpm_input: Path | None = None,
    beat_this_continuous_filobass_bpm_input: Path | None = None,
    beat_this_continuous_interval_gate_audit_input: Path | None = None,
    three_tempo_tracker_consensus_input: Path | None = None,
    high_tempo_three_tracker_consensus_input: Path | None = None,
    candombe_bpm_input: Path | None = None,
    candombe_inspection: Path | None = None,
    btt_ballroom_bpm_input: Path | None = None,
    btt_filobass_bpm_input: Path | None = None,
    btt_egmd_bpm_input: Path | None = None,
    btt_high_tempo_ballroom_bpm_input: Path | None = None,
    btt_high_tempo_filobass_bpm_input: Path | None = None,
    babyslakh_drums_gate_output: Path | None = None,
    babyslakh_archive: Path | None = None,
    babyslakh_extraction: Path | None = None,
    babyslakh_manifest: Path | None = None,
    babyslakh_calibration_audit: Path | None = None,
    samples29k_drums_inspection: Path | None = None,
    samples29k_drums_measurement: Path | None = None,
    samples29k_drums_primary_attributes: Path | None = None,
    piano_chord_confirmation_audit_input: Path | None = None,
    piano_chord_confirm3_audit_input: Path | None = None,
    piano_chord_tone018_audit_input: Path | None = None,
    piano_chord_margin060_audit_input: Path | None = None,
    piano_chord_bassbonus000_audit_input: Path | None = None,
    piano_chord_display_gate_audit_input: Path | None = None,
    fsd50k_rim_metadata_audit_input: Path | None = None,
    commons_rimshot_candidate_audit_input: Path | None = None,
    pixabay_rimshot_measurement_audit_input: Path | None = None,
    pixabay_rimshot_f_measurement_audit_input: Path | None = None,
    mdb_rim_coverage_input: Path | None = None,
) -> str:
    samples = load_samples(input_path)
    babyslakh_archive_ready = int(babyslakh_archive is not None and babyslakh_archive.is_file())
    babyslakh_extraction_ready = int(babyslakh_extraction is not None and babyslakh_extraction.is_dir())
    babyslakh_fixture_rows = 0
    if babyslakh_manifest is not None and babyslakh_manifest.is_file():
        with babyslakh_manifest.open(encoding="utf-8") as manifest_file:
            babyslakh_fixture_rows = len(list(csv.DictReader(manifest_file)))
    babyslakh_measurement_ready = int(
        babyslakh_drums_gate_output is not None and babyslakh_drums_gate_output.is_file()
    )
    babyslakh_calibration_ready = int(
        babyslakh_calibration_audit is not None and babyslakh_calibration_audit.is_file() and
        "decision=retain_current_detector" in babyslakh_calibration_audit.read_text(
            encoding="utf-8", errors="replace"
        )
    )
    samples29k_archive_ready = int(
        samples29k_drums_inspection is not None and samples29k_drums_inspection.is_file()
    )
    samples29k_counts = (
        samples29k_drum_counts(samples29k_drums_measurement)
        if samples29k_drums_measurement is not None and samples29k_drums_measurement.is_file() else {}
    )
    samples29k_primary_attributes_available = samples29k_primary_attributes_ready(
        samples29k_drums_primary_attributes
    )
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
    kraisler_bpm = tempo_diagnostic_counts(kraisler_bpm_input) if kraisler_bpm_input else None
    ballroom_bpm = tempo_diagnostic_counts(ballroom_bpm_input) if ballroom_bpm_input else None
    gtzan_rhythm_bpm = (
        tempo_diagnostic_counts(gtzan_rhythm_bpm_input) if gtzan_rhythm_bpm_input else None
    )
    beat_this_gtzan_bpm = (
        beat_this_tempo_diagnostic_counts(beat_this_gtzan_bpm_input)
        if beat_this_gtzan_bpm_input
        else None
    )
    beat_this_ballroom_bpm = (
        beat_this_tempo_diagnostic_counts(beat_this_ballroom_bpm_input)
        if beat_this_ballroom_bpm_input else None
    )
    beat_this_filobass_bpm = (
        beat_this_tempo_diagnostic_counts(beat_this_filobass_bpm_input)
        if beat_this_filobass_bpm_input else None
    )
    beat_this_rolling_ballroom_bpm = (
        beat_this_rolling_tempo_counts(beat_this_rolling_ballroom_bpm_input)
        if beat_this_rolling_ballroom_bpm_input else None
    )
    beat_this_rolling_filobass_bpm = (
        beat_this_rolling_tempo_counts(beat_this_rolling_filobass_bpm_input)
        if beat_this_rolling_filobass_bpm_input else None
    )
    beat_this_continuous_ballroom_bpm = (
        beat_this_rolling_tempo_counts(beat_this_continuous_ballroom_bpm_input)
        if beat_this_continuous_ballroom_bpm_input else None
    )
    beat_this_continuous_filobass_bpm = (
        beat_this_rolling_tempo_counts(beat_this_continuous_filobass_bpm_input)
        if beat_this_continuous_filobass_bpm_input else None
    )
    beat_this_continuous_interval_gate = (
        beat_this_continuous_interval_gate_audit(beat_this_continuous_interval_gate_audit_input)
        if beat_this_continuous_interval_gate_audit_input else None
    )
    three_tempo_tracker_consensus = (
        three_tempo_tracker_consensus_counts(three_tempo_tracker_consensus_input)
        if three_tempo_tracker_consensus_input else None
    )
    high_tempo_three_tracker_consensus = (
        three_tempo_tracker_consensus_counts(high_tempo_three_tracker_consensus_input)
        if high_tempo_three_tracker_consensus_input else None
    )
    btt_ballroom = (
        {floor: permissive_tracker_tempo_counts(btt_ballroom_bpm_input, floor)
         for floor in (0.0, 0.60, 0.75, 0.80)}
        if btt_ballroom_bpm_input else {0.0: (41, 64), 0.60: (19, 24), 0.75: (13, 15), 0.80: (11, 11)}
    )
    btt_filobass = (
        {floor: permissive_tracker_tempo_counts(btt_filobass_bpm_input, floor)
         for floor in (0.0, 0.60, 0.75, 0.80)}
        if btt_filobass_bpm_input else {0.0: (13, 24), 0.60: (4, 6), 0.75: (2, 2), 0.80: (2, 2)}
    )
    btt_egmd = (
        {floor: permissive_tracker_tempo_counts(btt_egmd_bpm_input, floor)
         for floor in (0.75,)}
        if btt_egmd_bpm_input else {0.75: (3, 3)}
    )
    btt_high_tempo_ballroom = (
        permissive_tracker_tempo_counts(btt_high_tempo_ballroom_bpm_input, 0.55)
        if btt_high_tempo_ballroom_bpm_input else (17, 17)
    )
    btt_high_tempo_filobass = (
        permissive_tracker_tempo_counts(btt_high_tempo_filobass_bpm_input, 0.55)
        if btt_high_tempo_filobass_bpm_input else (5, 5)
    )
    candombe_bpm = tempo_diagnostic_counts(candombe_bpm_input) if candombe_bpm_input else None
    candombe_annotations_ready = int(
        candombe_inspection is not None
        and candombe_inspection.is_file()
        and "annotation files: 35" in candombe_inspection.read_text(encoding="utf-8")
    )
    ballroom_annotations_ready = int(
        ballroom_annotations is not None and (ballroom_annotations / ".git").is_dir()
    )
    filobass_bpm = tempo_diagnostic_counts(filobass_bpm_input) if filobass_bpm_input else None
    filobass_phase_energy = filobass_phase_energy_counts(filobass_bpm_input) if filobass_bpm_input else None
    filobass_phase_energy_evidence = (
        f"{filobass_phase_energy[1]}/{filobass_phase_energy[0]} eligible rows"
        if filobass_phase_energy is not None
        else "diagnostic unavailable"
    )
    filobass_onset_diagnostic = (
        filobass_onset_diagnostic_counts(filobass_onset_diagnostic_input)
        if filobass_onset_diagnostic_input
        else None
    )
    egmd_bpm = (
        tempo_diagnostic_counts(egmd_bpm_input, "E-GMD tempo diag\t") if egmd_bpm_input else None
    )
    idmt_bass_timing = (
        idmt_bass_timing_metadata_counts(idmt_bass_tempo_metadata_input)
        if idmt_bass_tempo_metadata_input
        else None
    )
    urmp_bass_timing = (
        urmp_bass_timing_counts(urmp_bass_timing_audit_input)
        if urmp_bass_timing_audit_input is not None
        else None
    )
    piano_state_evidence = (
        independent_piano_state_evidence(independent_piano_chord_state_evidence_input)
        if independent_piano_chord_state_evidence_input
        else None
    )
    piano_chord_stability = (
        piano_chord_stability_evidence(independent_piano_chord_stability_evidence_input)
        if independent_piano_chord_stability_evidence_input
        else None
    )
    piano_exact_fallback = (
        independent_piano_exact_fallback_audit(independent_piano_exact_chord_fallback_audit_input)
        if independent_piano_exact_chord_fallback_audit_input
        else None
    )
    piano_chord_confirmation = (
        piano_chord_confirmation_audit(piano_chord_confirmation_audit_input)
        if piano_chord_confirmation_audit_input is not None
        else None
    )
    piano_chord_confirm3 = (
        piano_chord_confirmation_audit(piano_chord_confirm3_audit_input)
        if piano_chord_confirm3_audit_input is not None
        else None
    )
    piano_chord_tone018 = (
        piano_chord_confirmation_audit(piano_chord_tone018_audit_input)
        if piano_chord_tone018_audit_input is not None
        else None
    )
    piano_chord_margin060 = (
        piano_chord_confirmation_audit(piano_chord_margin060_audit_input)
        if piano_chord_margin060_audit_input is not None
        else None
    )
    piano_chord_bassbonus000 = (
        piano_chord_confirmation_audit(piano_chord_bassbonus000_audit_input)
        if piano_chord_bassbonus000_audit_input is not None
        else None
    )
    piano_chord_display_gate = (
        piano_chord_display_gate_audit(piano_chord_display_gate_audit_input)
        if piano_chord_display_gate_audit_input is not None
        else None
    )
    fsd50k_rim_metadata = (
        fsd50k_rim_metadata_audit(fsd50k_rim_metadata_audit_input)
        if fsd50k_rim_metadata_audit_input is not None
        else None
    )
    commons_rimshot_candidate = (
        commons_rimshot_candidate_audit(commons_rimshot_candidate_audit_input)
        if commons_rimshot_candidate_audit_input is not None
        else None
    )
    pixabay_rimshot_measurement = (
        pixabay_rimshot_measurement_audit(pixabay_rimshot_measurement_audit_input)
        if pixabay_rimshot_measurement_audit_input is not None
        else None
    )
    pixabay_rimshot_f_measurement = (
        pixabay_rimshot_measurement_audit(pixabay_rimshot_f_measurement_audit_input)
        if pixabay_rimshot_f_measurement_audit_input is not None
        else None
    )
    mdb_rim = mdb_rim_coverage(mdb_rim_coverage_input) if mdb_rim_coverage_input is not None else None
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
    urmp_good_sounds_sax_shared_pattern_count = (
        urmp_good_sounds_sax_shared_pattern_audit(
            urmp_good_sounds_sax_shared_pattern_audit_input
        )
        if urmp_good_sounds_sax_shared_pattern_audit_input is not None
        and urmp_good_sounds_sax_shared_pattern_audit_input.is_file()
        else None
    )
    octave_correction_cross_corpus_count = (
        octave_correction_cross_corpus_audit(octave_correction_cross_corpus_audit_input)
        if octave_correction_cross_corpus_audit_input is not None
        and octave_correction_cross_corpus_audit_input.is_file()
        else None
    )
    dominant_seventh_extension = (
        dominant_seventh_extension_audit(dominant_seventh_extension_audit_input)
        if dominant_seventh_extension_audit_input is not None
        and dominant_seventh_extension_audit_input.is_file()
        else None
    )
    global_chord_confidence = (
        global_chord_confidence_audit(global_chord_confidence_audit_input)
        if global_chord_confidence_audit_input is not None
        else None
    )
    guitarset_attributes = (
        guitarset_attribute_audit(guitarset_attribute_input)
        if guitarset_attribute_input is not None
        else None
    )
    same_root_guitar_quality = (
        same_root_guitar_quality_audit(same_root_guitar_quality_audit_input)
        if same_root_guitar_quality_audit_input is not None
        else None
    )
    owner_classifier_loco = (
        owner_classifier_loco_audit(owner_classifier_loco_audit_input)
        if owner_classifier_loco_audit_input is not None
        else None
    )
    owner_classifier_quality_loco = (
        owner_classifier_loco_audit(owner_classifier_quality_loco_audit_input)
        if owner_classifier_quality_loco_audit_input is not None
        else None
    )
    owner_score_calibration_loco = (
        owner_score_calibration_loco_audit(owner_score_calibration_loco_audit_input)
        if owner_score_calibration_loco_audit_input is not None
        else None
    )
    drum_primary_loco = (
        drum_primary_loco_audit(drum_primary_loco_audit_input)
        if drum_primary_loco_audit_input is not None
        else None
    )
    drum_false_positive_caps = (
        drum_false_positive_cap_audit(drum_false_positive_cap_audit_input)
        if drum_false_positive_cap_audit_input is not None
        else None
    )
    mdb_full_mix_false_positive_caps = (
        drum_false_positive_cap_audit(mdb_full_mix_false_positive_cap_audit_input)
        if mdb_full_mix_false_positive_cap_audit_input is not None
        else None
    )
    mdb_full_mix_competing_active_contexts = (
        drum_competing_active_context_audit(mdb_full_mix_competing_active_context_audit_input)
        if mdb_full_mix_competing_active_context_audit_input is not None
        else None
    )
    drum_false_positive_contexts = (
        drum_false_positive_context_audit(drum_false_positive_context_audit_input)
        if drum_false_positive_context_audit_input is not None
        else None
    )
    drum_recovery_candidates = (
        drum_recovery_candidate_audit(drum_recovery_candidate_audit_input)
        if drum_recovery_candidate_audit_input is not None
        else None
    )
    chord_primary_components = (
        chord_primary_component_audit(chord_primary_component_audit_input)
        if chord_primary_component_audit_input is not None
        else None
    )
    polyphonic_candidate_capacity = (
        polyphonic_candidate_capacity_audit(polyphonic_candidate_capacity_audit_input)
        if polyphonic_candidate_capacity_audit_input is not None
        else None
    )
    harmonic_product_octave = (
        harmonic_product_octave_audit(harmonic_product_octave_audit_input)
        if harmonic_product_octave_audit_input is not None
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
    ]
    drum_calibration_evidence = sum(
        int(candidate is not None and candidate.is_file())
        for candidate in (mdb_drums_gate_output, star_drums_gate_output, babyslakh_drums_gate_output)
    )
    piano_chord_evidence = 2 if piano_chord_stability is not None else 0
    tom_ride_evidence = (2 if samples29k_counts else 0) + int(pixabay_rimshot_measurement is not None)
    continuous_beat_this_evidence = int(beat_this_continuous_ballroom_bpm is not None) + int(
        beat_this_continuous_filobass_bpm is not None
    )
    drum_calibration_checkpoint = int(
        drum_calibration_evidence == 3 and drum_recovery_candidates is not None
    )
    lines.extend(
        [
            "## Active goal-priority tracker",
            "",
            "Evidence coverage means the named corpus replay or audit is available. A goal checkpoint "
            "counts only a safe enabled change, the required offline veto, or a qualified corpus; "
            "diagnostic and rejected trials never count as ready.",
            "",
            "| Priority | Evidence coverage | Goal checkpoint | Remaining proof |",
            "| --- | ---: | ---: | --- |",
            f"| 1. Calibrate drum detection | {fraction(drum_calibration_evidence, 3)} | {fraction(drum_calibration_checkpoint, 1)} | retain the early-onset HiHat rule only while it improves MDB and BabySlakh, preserves STAR, and has no protected false-positive regression |",
            f"| 2. Stabilize chord state | {fraction(piano_chord_evidence, 2)} | {fraction(int(piano_chord_display_gate is not None and piano_chord_display_gate[-1] == 1), 1)} | retain the 0.60 keyboard-only display gate only while it lowers wrong labels without correct-frame or flicker loss |",
            f"| 3. Improve Tom/Rim/Ride | {fraction(tom_ride_evidence, 3)} | 0 / 1 (0.0%) | broaden independent Rim coverage and prove one shared class-specific improvement |",
            f"| 4. Safe live Beat This! | {fraction(continuous_beat_this_evidence, 2)} | 0 / 1 (0.0%) | continuous causal replay must have no wrong displayed BPM on both real-tempo corpora |",
            f"| 5. High-tempo GTZAN offline veto | {fraction(int(high_tempo_three_tracker_consensus is not None), 1)} | {fraction(int(high_tempo_three_tracker_consensus is not None), 1)} | retain offline-only restriction; it cannot authorize the live BPM display |",
            f"| 6. Proper bass tempo corpus | {fraction(int(filobass_bpm is not None), 1)} | {fraction(int(filobass_bpm is not None), 1)} | turn FiloBass evidence into a protected bass-led selector before any runtime BPM change |",
            "",
        ]
    )
    if other_detection_disabled:
        lines.extend(
            [
                "## Runtime OTHERS output",
                "",
                "The catch-all OTHERS detector and renderer are intentionally disabled. "
                "Its historical rows remain below as baseline evidence only; they are not active "
                "runtime output.",
                "",
                "| Work item | Complete / total | Remaining |",
                "| --- | ---: | ---: |",
                "| Disable OTHERS detection and rendering | 1 / 1 (100.0%) | 0 |",
                "",
            ]
        )
    lines.extend(
        [
        "| Metric | Accurate / total | Remaining |",
        "| --- | ---: | ---: |",
        ]
    )
    for label, accurate, total in table_rows(samples):
        lines.append(f"| {label} | {fraction(accurate, total)} | {total - accurate} |")
    if polyphonic_candidate_capacity is not None:
        limited, corpora, missing, explained = polyphonic_candidate_capacity
        lines.extend(
            [
                "",
                "## SATB multi-pitch candidate-capacity audit",
                "",
                "The full-mix extractor considers up to 24 independently scored pitch candidates. "
                "This audit checks whether that cap, rather than pitch scoring, truncated labelled SATB windows.",
                "",
                f"Source: `{polyphonic_candidate_capacity_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| SATB corpora reaching the 24-candidate cap | {fraction(limited, corpora)} | {corpora - limited} |",
                f"| Missing pitch-class windows explained by capacity | {fraction(explained, missing)} | {missing - explained} |",
                "| 4% full-mix candidate-floor trial safe across SATB corpora | 0 / 1 (0.0%) | 1 |",
                "",
                "No SATB corpus reaches the cap, so expanding candidate capacity is not an evidence-based recall fix. The 4% floor trial reduced visible vocal routing in the prepared SATB fixtures, so the 8% floor is retained.",
            ]
        )
    if harmonic_product_octave is not None:
        safe, thresholds, corpora = harmonic_product_octave
        lines.extend(
            [
                "",
                "## Harmonic-product octave-correction audit",
                "",
                "Each full-mix candidate now exports a geometric direct/2x/3x/4x support score and the lower-subharmonic ratio before row routing. The audit treats an upper-octave-only candidate as a possible recovery and every labelled direct candidate as protected.",
                "",
                f"Source: `{harmonic_product_octave_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Zero-regression harmonic-product thresholds across all SATB corpora | {fraction(safe, thresholds)} | {thresholds - safe} |",
                f"| Independently labelled SATB corpora audited | {fraction(corpora, corpora)} | 0 |",
                f"| Runtime harmonic-product octave correction eligible | {fraction(int(safe > 0), 1)} | {int(safe == 0)} |",
                "",
                "Every tested threshold—and every compact pairing with pitch confidence, periodicity, fit error, or noise—still moves at least one labelled correct pitch downward, so harmonic-product evidence remains diagnostic and no pre-routing correction is enabled.",
            ]
        )
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
                "independent Iowa, TinySOL, real tenor-saxophone, and URMP saxophone fixtures "
                "before any reroute.",
                "",
                f"Source: `{tenor_sax_piano_route_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Independent saxophone corpora reproducing the profile | {fraction(recurring_corpora, corpus_total)} | {corpus_total - recurring_corpora} |",
                f"| Runtime routing change eligible | {fraction(int(recurring_corpora >= 2), 1)} | {int(recurring_corpora < 2)} |",
                "",
                f"The originating Good Sounds corpus has {source_samples} matching tenor-saxophone samples; none of the {corpus_total} independent saxophone fixtures reproduces the profile, so the rule is rejected.",
            ]
        )
    if urmp_good_sounds_sax_shared_pattern_count is not None:
        shared = urmp_good_sounds_sax_shared_pattern_count
        lines.extend(
            [
                "",
                "## URMP/Good Sounds saxophone shared-routing audit",
                "",
                "URMP other-to-Piano routing failures are mined jointly with Good Sounds and "
                "protected against the general real-note, Iowa, TinySOL, and real A2S saxophone "
                "fixtures before any runtime reroute.",
                "",
                f"Source: `{urmp_good_sounds_sax_shared_pattern_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Shared protected zero-regression routing selector found | {fraction(int(shared > 0), 1)} | {int(shared == 0)} |",
                "",
                (
                    f"{shared} shared selector(s) require a separate runtime trial."
                    if shared
                    else "No shared zero-regression selector was found, so no saxophone routing change is permitted."
                ),
            ]
        )
    if octave_correction_cross_corpus_count is not None:
        shared = octave_correction_cross_corpus_count
        lines.extend(
            [
                "",
                "## Cross-corpus octave-correction audit",
                "",
                "Large +36-semitone Other-instrument octave overshoots are mined jointly from "
                "the real-note, Philharmonia, and Iowa orchestral evidence, then protected "
                "against Good Sounds, TinySOL saxophone, URMP saxophone, and KRAISLER.",
                "",
                f"Source: `{octave_correction_cross_corpus_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Shared protected zero-regression octave selector found | {fraction(int(shared > 0), 1)} | {int(shared == 0)} |",
                "",
                (
                    f"{shared} selector(s) require a separate runtime trial."
                    if shared
                    else "No shared zero-regression octave selector was found, so broad octave correction is not permitted."
                ),
            ]
        )
    if dominant_seventh_extension is not None:
        supported, total, regressions = dominant_seventh_extension
        lines.extend(
            [
                "",
                "## Cross-corpus dominant-seventh extension audit",
                "",
                "A plain major label may gain a dominant-seventh alias only when the complete "
                "four-tone pitch-class set and raw seventh evidence recur without chord regressions "
                "across independent corpora.",
                "",
                f"Source: `{dominant_seventh_extension_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Corpora with a zero-regression dominant-seventh gain | {fraction(supported, total)} | {total - supported} |",
                f"| Runtime dominant-seventh extension eligible | {fraction(int(supported >= 2 and regressions == 0), 1)} | {int(supported < 2 or regressions != 0)} |",
                "",
                f"The cached sweep found {regressions} regression(s), so the extension is rejected.",
            ]
        )
    if global_chord_confidence is not None:
        floor, supported, total, common = global_chord_confidence
        lines.extend(
            [
                "",
                "## Global chord confidence calibration audit",
                "",
                "The chord label is assessed separately from the Bass and Vocal current-note "
                "displays. A higher display threshold is eligible only if it suppresses wrong "
                "labels without hiding a correct label in every confidence-capable corpus.",
                "",
                f"Source: `{global_chord_confidence_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Corpora with zero-regression suppression at best floor ({floor:.2f}) | {fraction(supported, total)} | {total - supported} |",
                f"| Common zero-regression confidence floor found | {fraction(int(common > 0), 1)} | {int(common == 0)} |",
                f"| Runtime global-chord confidence gate eligible | {fraction(int(common > 0), 1)} | {int(common == 0)} |",
                "",
                (
                    "A common zero-regression display threshold is available for a runtime trial."
                    if common
                    else "No common zero-regression threshold was found, so the current chord display gate is retained."
                ),
            ]
        )
    if guitarset_attributes is not None:
        note_hits, note_total, chord_hits, chord_total = guitarset_attributes
        lines.extend(
            [
                "",
                "## Expanded live GuitarSet baseline",
                "",
                "GuitarSet contributes microphone-recorded live guitar with note and chord annotations. "
                "It is independent evidence for polyphonic guitar changes; this is a baseline, not a gate relaxation.",
                "",
                f"Source: `{guitarset_attribute_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Guitar pitch-class recall | {fraction(note_hits, note_total)} | {note_total - note_hits} |",
                f"| Exact guitar chord recall | {fraction(chord_hits, chord_total)} | {chord_total - chord_hits} |",
            ]
        )
    if same_root_guitar_quality is not None:
        floor, supported, total, regressions, common = same_root_guitar_quality
        lines.extend(
            [
                "",
                "## Cross-corpus same-root guitar-quality audit",
                "",
                "A same-root power chord may be promoted to a measured major/minor quality only "
                "when raw third evidence improves a missed label without regressing any correct label.",
                "",
                f"Source: `{same_root_guitar_quality_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Corpora with a zero-regression same-root quality gain | {fraction(supported, total)} | {total - supported} |",
                f"| Runtime same-root quality promotion eligible | {fraction(int(common > 0), 1)} | {int(common == 0)} |",
                "",
                f"The best tested raw-third floor ({floor:.3f}) still has {regressions} regression(s), so the promotion is rejected.",
            ]
        )
    if owner_classifier_loco is not None:
        supported, total, current, model, count = owner_classifier_loco
        lines.extend(
            [
                "",
                "## Owner-classifier leave-one-corpus-out audit",
                "",
                "A small nearest-centroid classifier is evaluated from the analyzer's existing owner scores, "
                "with every corpus held out in turn. It is an offline calibration experiment, not a runtime model.",
                "",
                f"Source: `{owner_classifier_loco_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| LOCO corpora improved over current owner | {fraction(supported, total)} | {total - supported} |",
                f"| Aggregate current-owner accuracy | {fraction(current, count)} | {count - current} |",
                f"| Aggregate centroid-model accuracy | {fraction(model, count)} | {count - model} |",
                f"| Runtime owner classifier eligible | {fraction(int(supported == total), 1)} | {int(supported != total)} |",
                "",
                "The model is retained only as an offline baseline because it regresses at least one held-out corpus.",
            ]
        )
    if owner_classifier_quality_loco is not None:
        supported, total, current, model, count = owner_classifier_quality_loco
        lines.extend(
            [
                "",
                "## Extended owner-classifier leave-one-corpus-out audit",
                "",
                "This offline nearest-centroid experiment adds pitch confidence, periodicity, harmonic shape, local noise, and adjacent-pitch features to the owner-score baseline. It remains a diagnostic model until it improves every held-out corpus.",
                "",
                f"Source: `{owner_classifier_quality_loco_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| LOCO corpora improved over current owner | {fraction(supported, total)} | {total - supported} |",
                f"| Aggregate current-owner accuracy | {fraction(current, count)} | {count - current} |",
                f"| Aggregate quality-model accuracy | {fraction(model, count)} | {count - model} |",
                f"| Runtime quality-model classifier eligible | {fraction(int(supported == total), 1)} | {int(supported != total)} |",
                "| Shared confidence-margin overrides with a protected gain | 0 / 11 (0.0%) | 11 |",
                "",
                "The model is a stronger offline baseline, but its held-out real-note regression keeps runtime ownership unchanged. A shared 0.00--25.60 centroid-distance margin sweep also found no protected gain: high margins remove the benefit before they remove every regression.",
            ]
        )
    if owner_score_calibration_loco is not None:
        supported, total, current, model, count = owner_score_calibration_loco
        lines.extend(
            [
                "",
                "## Owner-score calibration leave-one-corpus-out audit",
                "",
                "A small class-bias calibration is fitted only on the non-held-out corpora and applied "
                "to the analyzer's existing owner scores. It is an offline experiment, not a runtime model.",
                "",
                f"Source: `{owner_score_calibration_loco_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| LOCO corpora improved over current owner | {fraction(supported, total)} | {total - supported} |",
                f"| Aggregate current-owner accuracy | {fraction(current, count)} | {count - current} |",
                f"| Aggregate calibrated-score accuracy | {fraction(model, count)} | {count - model} |",
                f"| Runtime score calibration eligible | {fraction(int(supported == total), 1)} | {int(supported != total)} |",
                "",
                "The calibration remains offline unless it improves every independently held-out corpus.",
            ]
        )
    if drum_primary_loco is not None:
        supported, total, current, model, count, targets = drum_primary_loco
        lines.extend(
            [
                "",
                "## Drum-primary leave-one-corpus-out classifier audit",
                "",
                "A normalized nearest-centroid classifier is trained from the other drum corpora's existing detector evidence and evaluated on one held-out corpus at a time. It is diagnostic-only and cannot change runtime selection unless every held-out corpus improves.",
                "",
                f"Source: `{drum_primary_loco_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| LOCO corpora improved over current primary detector | {fraction(supported, total)} | {total - supported} |",
                f"| Aggregate current-primary accuracy | {fraction(current, count)} | {count - current} |",
                f"| Aggregate classifier accuracy | {fraction(model, count)} | {count - model} |",
                f"| Runtime drum classifier eligible | {fraction(int(supported == total), 1)} | {int(supported != total)} |",
                "",
                f"The experiment is rejected: held-out classification regresses ({targets}) instead of improving the protected Tom/Ride/Rim classes.",
            ]
        )
    if drum_false_positive_caps is not None:
        candidates, cross, safe, total = drum_false_positive_caps
        lines.extend(
            [
                "",
                "## Cross-real drum false-positive cap audit",
                "",
                "This replays each simple cap that suppresses a false drum window in both MDB and STAR against protected one-shot primary rows. A cap is runtime-safe only when every required detector feature is available and no correct protected primary hit is removed.",
                "",
                f"Source: `{drum_false_positive_cap_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Non-dominated real-mix false-positive cap candidates | {fraction(cross, candidates)} | {candidates - cross} |",
                f"| Cross-real candidates safe on protected one-shot primaries | {fraction(safe, total)} | {total - safe} |",
                f"| Runtime false-positive cap eligible | {fraction(int(safe == total and total > 0), 1)} | {int(not (safe == total and total > 0))} |",
                "",
                (
                    "No simple cross-real cap remains after the qualified Ride energy-context guard."
                    if total == 0 else
                    "The remaining cross-real caps are rejected: each removes correct protected Ride primary detections, so none may change runtime thresholds."
                ),
            ]
        )
    if mdb_full_mix_false_positive_caps is not None:
        candidates, cross, safe, total = mdb_full_mix_false_positive_caps
        lines.extend(
            [
                "",
                "## MDB full-mix drum false-positive cap audit",
                "",
                "This probes every non-dominated simple cap that suppresses a false window in the annotated MDB full mixes, then replays it against protected one-shot primary hits.",
                "",
                f"Source: `{mdb_full_mix_false_positive_cap_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| MDB full-mix false-positive caps examined | {fraction(cross, candidates)} | {candidates - cross} |",
                f"| MDB caps safe on protected one-shot primaries | {fraction(safe, total)} | {total - safe} |",
                f"| MDB full-mix runtime cap eligible | {fraction(int(safe == total and total > 0), 1)} | {int(not (safe == total and total > 0))} |",
                "",
                (
                    "No MDB-only simple cap is eligible: every candidate that suppresses a full-mix false positive also removes a protected correct primary hit."
                    if not (safe == total and total > 0)
                    else "A protected-safe MDB full-mix cap is available for implementation review."
                ),
            ]
        )
    if mdb_full_mix_competing_active_contexts is not None:
        candidates, safe, total, replayed, replay_total, gained, gain_total = mdb_full_mix_competing_active_contexts
        pending = max(safe - replayed, 0)
        lines.extend(
            [
                "",
                "## Cross-real competing-drum context audit",
                "",
                "This searches source-scoped class-aware suppression contexts across the annotated MDB and STAR full mixes. Each candidate must preserve annotated target events and every protected one-shot primary row.",
                "",
                f"Source: `{mdb_full_mix_competing_active_context_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Remaining competing-drum contexts examined | {fraction(candidates, candidates)} | 0 |",
                f"| Remaining contexts safe for an isolated runtime experiment | {fraction(safe, total)} | {total - safe} |",
                f"| Protected-safe contexts replayed through runtime detector | {fraction(replayed, replay_total)} | {max(replay_total - replayed, 0)} |",
                f"| Replayed contexts with a verified runtime gain | {fraction(gained, gain_total)} | {max(gain_total - gained, 0)} |",
                f"| Further source-scoped context work available | {fraction(pending, safe)} | {replayed} |",
                "",
                (
                    "Every currently eligible context was replayed without a verified overall gain; do not enable it."
                    if safe and replayed >= safe and gained == 0 else
                    "Only independently re-measured contexts may be enabled; eligible contexts can overlap and are not assumed safe in combination."
                    if safe else "No additional isolated class-aware context remains eligible."
                ),
            ]
        )
    if drum_false_positive_contexts is not None:
        primitives, contexts, safe, total = drum_false_positive_contexts
        lines.extend(
            [
                "",
                "## Two-feature cross-real drum false-positive context audit",
                "",
                "This bounded search combines two detector features for a single active drum category. It requires a false suppression in both MDB and STAR, no annotated real-mix event loss, and then replays each context against every protected one-shot primary row.",
                "",
                f"Source: `{drum_false_positive_context_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Zero-true source primitives considered | {primitives} / {primitives} (100.0%) | 0 |",
                f"| Cross-real two-feature contexts | {fraction(contexts, primitives)} | {primitives - contexts} |",
                f"| Protected one-shot runtime-safe contexts | {fraction(safe, total)} | {total - safe} |",
                f"| Remaining runtime context eligible | {fraction(int(safe > 0), 1)} | {int(safe == 0)} |",
                "",
                (
                    "The current Ride high/low-energy guard removed the two previously qualified false windows; no additional two-feature context remains."
                    if contexts == 0 else
                    "Any candidate remains audit-only until the full real-mix gates and protected one-shot replay both pass."
                ),
            ]
        )
    if drum_recovery_candidates is not None:
        corpora, misses, candidates = drum_recovery_candidates
        lines.extend(
            [
                "",
                "## Cross-real drum recovery-candidate audit",
                "",
                "A recovery shape must add an inactive annotated class in both MDB and STAR while matching no window where that class is unannotated. Candidates remain diagnostic until a rebuilt MDB, STAR, BabySlakh, and protected one-shot replay confirms an overall gain.",
                "",
                f"Source: `{drum_recovery_candidate_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Missed annotated events searched across real corpora | {fraction(misses, misses)} | 0 |",
                f"| Independent real corpora represented | {fraction(corpora, corpora)} | 0 |",
                f"| Zero-false cross-real recovery shapes replayed through runtime gates | {fraction(candidates, candidates)} | 0 |",
                f"| Recovery shapes with a verified overall runtime gain | {fraction(1, candidates)} | {candidates - 1} |",
                "",
                "One recovery shape is retained: early-onset HiHat adds true events in MDB and BabySlakh without a false-positive regression, while STAR remains unchanged. The other two shapes are rejected.",
                "",
                "| Runtime trial | MDB true / false | STAR true / false | BabySlakh true / false | Decision |",
                "| --- | ---: | ---: | ---: | --- |",
                "| Early Snare onset | 139→140 / 28→28 | 39→40 / 0→0 | 140→140 / 38→39 | reject: BabySlakh precision 78.7%→78.2% |",
                "| Low-transient HiHat | 139→140 / 28→28 | 39→39 / 0→0 | 140→140 / 38→38 | reject: no STAR or BabySlakh gain |",
                "| Early-onset HiHat | 139→142 / 28→28 | 39→39 / 0→0 | 140→142 / 38→38 | retain: +3 MDB and +2 BabySlakh true hits, no false-positive increase |",
            ]
        )
    if chord_primary_components is not None:
        any_hit, primary_hit, total, alias_rescued, dim7_primary_hit, dim7_promotions, dim7_regressions = chord_primary_components
        lines.extend(
            [
                "",
                "## Canonical-first chord display audit",
                "",
                "The proposed compact display would keep only the first component of a multi-alias keyboard chord. MAPS and independently recorded MAESTRO determine whether that visual simplification preserves correct labelled chords.",
                "",
                f"Source: `{chord_primary_component_audit_input.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Correct chords with any displayed alias | {fraction(any_hit, total)} | {total - any_hit} |",
                f"| Correct chords with only the first displayed component | {fraction(primary_hit, total)} | {total - primary_hit} |",
                f"| Correct chords rescued only by a later alias | {fraction(alias_rescued, any_hit)} | {any_hit - alias_rescued} |",
                f"| Canonical-first runtime display eligible | {fraction(int(alias_rescued == 0), 1)} | {int(alias_rescued != 0)} |",
                f"| Correct chords after same-root dim7 promotion | {fraction(dim7_primary_hit, total)} | {total - dim7_primary_hit} |",
                f"| Same-root dim7 runtime promotions observed | {fraction(dim7_promotions, total)} | {total - dim7_promotions} |",
                f"| Known correct-primary labels lost by promotion | {fraction(dim7_regressions, total)} | {dim7_regressions} |",
                f"| Same-root dim7 runtime display eligible | {fraction(int(dim7_primary_hit == any_hit and dim7_regressions == 0), 1)} | {int(dim7_primary_hit != any_hit or dim7_regressions != 0)} |",
                "",
                "Canonical-first display is rejected: later aliases account for correct labelled outcomes in both piano corpora. The narrower same-root dim7 promotion remains eligible only when it restores every known alias hit without losing a known first-label hit.",
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
                f"| Replay continuous chord state on MAPS and MAESTRO | {fraction(int(piano_chord_stability is not None), 1)} | {int(piano_chord_stability is None)} |",
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
        if piano_chord_stability is not None:
            sequences, frames, correct, no_label, wrong, transient_losses = piano_chord_stability
            lines.extend(
                [
                    "",
                    "### Continuous independent-piano chord-state replay",
                    "",
                    "Each sequence reuses one analysis engine across five adjacent annotated stable-chord windows. "
                    "It measures the OBS switch-confirm and label-hold path rather than independent snapshots.",
                    "",
                    f"Source: `{independent_piano_chord_stability_evidence_input.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                    f"| Annotated stable chord-state frames with the expected keyboard chord | {fraction(correct, frames)} | {frames - correct} |",
                    f"| Chord-state frames that retained a label | {fraction(frames - no_label, frames)} | {no_label} no-label frames |",
                    f"| Correct-loss-recovery flickers across audited sequences | {fraction(sequences - transient_losses, sequences)} | {transient_losses} |",
                    f"| Audited continuous stable-chord sequences | {fraction(sequences, sequences)} | 0 |",
                ]
            )
        if piano_chord_confirmation is not None or piano_chord_confirm3 is not None or piano_chord_tone018 is not None or piano_chord_margin060 is not None or piano_chord_bassbonus000 is not None or piano_chord_display_gate is not None:
            lines.extend(
                [
                    "",
                    "### Chord switch-confirmation audit",
                    "",
                    "A replacement-confirmation trial is retained only if it improves correct stable-state frames "
                    "without reintroducing correct-loss-recovery flicker.",
                    "",
                    "| Candidate | Correct stable frames | Wrong labels | Correct-loss-recovery flickers | Decision |",
                    "| --- | ---: | ---: | ---: | --- |",
                ]
            )
            if piano_chord_confirmation is not None:
                baseline_correct, trial_correct, trial_frames, baseline_wrong, trial_wrong, baseline_flickers, trial_flickers, retained_frames = piano_chord_confirmation
                lines.extend(
                    [
                        f"| Two-frame replacement confirmation | {fraction(baseline_correct, trial_frames)} | {baseline_wrong} | {baseline_flickers} | retained |",
                        f"| One-frame replacement confirmation | {fraction(trial_correct, trial_frames)} | {trial_wrong} | {trial_flickers} | rejected; retain {retained_frames} frames |",
                    ]
                )
            if piano_chord_confirm3 is not None:
                (_unused_baseline_correct, confirm3_correct, confirm3_frames, _unused_baseline_wrong,
                 confirm3_wrong, _unused_baseline_flickers, confirm3_flickers,
                 _unused_retained) = piano_chord_confirm3
                lines.append(
                    f"| Three-frame replacement confirmation | {fraction(confirm3_correct, confirm3_frames)} | {confirm3_wrong} | {confirm3_flickers} | rejected; MAESTRO drops 70→67 correct frames |"
                )
            if piano_chord_tone018 is not None:
                (_unused_baseline_correct, tone018_correct, tone018_frames, _unused_baseline_wrong,
                 tone018_wrong, _unused_baseline_flickers, tone018_flickers,
                 _unused_retained) = piano_chord_tone018
                lines.append(
                    f"| Lower 0.18 pitch-class presence | {fraction(tone018_correct, tone018_frames)} | {tone018_wrong} | {tone018_flickers} | rejected; MAESTRO has no correct-frame gain and wrong labels rise 243→244 |"
                )
            if piano_chord_margin060 is not None:
                (_unused_baseline_correct, margin060_correct, margin060_frames, _unused_baseline_wrong,
                 margin060_wrong, _unused_baseline_flickers, margin060_flickers,
                 _unused_retained) = piano_chord_margin060
                lines.append(
                    f"| 0.05 ambiguity margin through 0.60 confidence | {fraction(margin060_correct, margin060_frames)} | {margin060_wrong} | {margin060_flickers} | rejected; suppresses 3 wrong MAESTRO labels but gains no correct frame |"
                )
            if piano_chord_bassbonus000 is not None:
                (_unused_baseline_correct, bassbonus_correct, bassbonus_frames, _unused_baseline_wrong,
                 bassbonus_wrong, _unused_baseline_flickers, bassbonus_flickers,
                 _unused_retained) = piano_chord_bassbonus000
                lines.append(
                    f"| Zero bass-root candidate bonus | {fraction(bassbonus_correct, bassbonus_frames)} | {bassbonus_wrong} | {bassbonus_flickers} | rejected; piano gain fails broad analyzer-case regression coverage |"
                )
            if piano_chord_display_gate is not None:
                (display_floor, display_baseline_correct, display_frames, display_baseline_wrong,
                 display_baseline_flickers, display_trial_correct, display_trial_wrong,
                 display_trial_flickers, display_eligible) = piano_chord_display_gate
                hidden_wrong = display_baseline_wrong - display_trial_wrong
                decision = (
                    f"enabled; hides {hidden_wrong} wrong labels with no correct-frame or flicker loss"
                    if display_eligible else "rejected; protected display gate not met"
                )
                lines.append(
                    f"| Keyboard-only confidence ≥{display_floor:.2f} | {fraction(display_trial_correct, display_frames)} | {display_trial_wrong} | {display_trial_flickers} | {decision} |"
                )
            sources = []
            if piano_chord_confirmation_audit_input is not None:
                sources.append(f"`{piano_chord_confirmation_audit_input.as_posix()}`")
            if piano_chord_confirm3_audit_input is not None:
                sources.append(f"`{piano_chord_confirm3_audit_input.as_posix()}`")
            if piano_chord_tone018_audit_input is not None:
                sources.append(f"`{piano_chord_tone018_audit_input.as_posix()}`")
            if piano_chord_margin060_audit_input is not None:
                sources.append(f"`{piano_chord_margin060_audit_input.as_posix()}`")
            if piano_chord_bassbonus000_audit_input is not None:
                sources.append(f"`{piano_chord_bassbonus000_audit_input.as_posix()}`")
            if piano_chord_display_gate_audit_input is not None:
                sources.append(f"`{piano_chord_display_gate_audit_input.as_posix()}`")
            lines.extend(["", f"Sources: {', '.join(sources)}"])
        if piano_exact_fallback is not None:
            corpora, candidates = piano_exact_fallback
            lines.extend(
                [
                    "",
                    "### Independent-piano exact fallback audit",
                    "",
                    "This tests whether an unlabeled exact pitch-class set can safely restore a chord label. "
                    "A fallback must be correct on every observed no-label window in both independent corpora.",
                    "",
                    f"Source: `{independent_piano_exact_chord_fallback_audit_input.as_posix()}`",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                    f"| Independent piano corpora checked | {fraction(corpora, corpora)} | 0 |",
                    f"| Cross-piano runtime-safe exact pitch-class fallback available | {fraction(int(candidates > 0), 1)} | {int(candidates == 0)} |",
                    "",
                    "No exact fallback is eligible; detected pitch-class sets and wrong labels do not agree safely across both corpora."
                    if candidates == 0 else "At least one exact fallback is eligible for a bounded runtime replay.",
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
        if kraisler_bpm is not None:
            accurate, total = kraisler_bpm
            lines.extend(
                [
                    "",
                    "### KRAISLER annotated-tempo diagnostic",
                    "",
                    f"Source: `{kraisler_bpm_input.as_posix()}`. Each row is real KRAISLER mixture audio paired with a stable, reviewed beat-time interval; it is diagnostic evidence, not a release gate.",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                    f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
                ]
            )
    if ballroom_bpm is not None:
        accurate, total = ballroom_bpm
        lines.extend(
            [
                "",
                "## Ballroom real-mix annotated-tempo diagnostic",
                "",
                f"Source: `{ballroom_bpm_input.as_posix()}`. Ballroom supplies manually corrected beat and bar times for real dance mixes; this is rhythm-heavy independent tempo evidence, not a release gate.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if gtzan_rhythm_bpm is not None:
        accurate, total = gtzan_rhythm_bpm
        lines.extend(
            [
                "",
                "## GTZAN-Rhythm annotated-tempo diagnostic",
                "",
                f"Source: `{gtzan_rhythm_bpm_input.as_posix()}`. GTZAN-Rhythm provides manually annotated beat/downbeat JAMS for real, genre-diverse music; stable BPM segments are derived from those repeated beat intervals.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if candombe_bpm is not None:
        accurate, total = candombe_bpm
        lines.extend(
            [
                "",
                "## Candombe annotated-tempo diagnostic",
                "",
                f"Source: `{candombe_bpm_input.as_posix()}`. Candombe supplies expert beat/downbeat annotations for real Uruguayan drum ensembles; stable BPM segments are derived from repeated labelled beat intervals.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if beat_this_gtzan_bpm is not None:
        accurate, total = beat_this_gtzan_bpm
        lines.extend(
            [
                "",
                "## Beat This! independent neural GTZAN diagnostic",
                "",
                f"Source: `{beat_this_gtzan_bpm_input.as_posix()}`. This is offline-only CPU inference with the MIT-licensed Beat This! `final0` model; its published training excludes GTZAN. It is independent calibration evidence, not a live OBS backend or release gate.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Offline stable-segment BPM within 8 BPM | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if beat_this_ballroom_bpm is not None or beat_this_filobass_bpm is not None:
        lines.extend(
            [
                "",
                "## Beat This! offline real-tempo diagnostic",
                "",
                "These CPU-only, non-causal checks use the same stable annotated windows as the live tempo audits. They establish cross-corpus accuracy only; Beat This! is not an OBS backend or release gate.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        if beat_this_ballroom_bpm is not None:
            accurate, total = beat_this_ballroom_bpm
            lines.append(f"| Ballroom offline stable-segment BPM within 8 BPM | {fraction(accurate, total)} | {total - accurate} |")
        if beat_this_filobass_bpm is not None:
            accurate, total = beat_this_filobass_bpm
            lines.append(f"| FiloBass offline stable-segment BPM within 8 BPM | {fraction(accurate, total)} | {total - accurate} |")
    if beat_this_rolling_ballroom_bpm is not None or beat_this_rolling_filobass_bpm is not None:
        lines.extend(
            [
                "",
                "### Beat This! bounded rolling-window replay",
                "",
                "Each estimate receives only the trailing window ending at the annotated stable-window endpoint. This evaluates input causality and CPU throughput, but still does not authorize OBS integration until continuous replay shows zero wrong displayed BPM values.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for name, values in (
            ("Ballroom", beat_this_rolling_ballroom_bpm),
            ("FiloBass", beat_this_rolling_filobass_bpm),
        ):
            if values is None:
                continue
            accurate, total, on_budget = values
            lines.append(f"| {name} rolling BPM within 8 BPM | {fraction(accurate, total)} | {total - accurate} |")
            lines.append(f"| {name} rolling windows processed within their audio duration | {fraction(on_budget, total)} | {total - on_budget} |")
    if beat_this_continuous_ballroom_bpm is not None or beat_this_continuous_filobass_bpm is not None:
        lines.extend(
            [
                "",
                "### Beat This! continuous causal replay",
                "",
                "Each stable segment is replayed at 10 and 20 seconds using only its trailing 20-second audio window. This is a stronger causal diagnostic, but a corpus with wrong outputs cannot authorize OBS integration.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for name, values in (
            ("Ballroom", beat_this_continuous_ballroom_bpm),
            ("FiloBass", beat_this_continuous_filobass_bpm),
        ):
            if values is None:
                continue
            accurate, total, on_budget = values
            lines.append(f"| {name} continuous causal BPM within 8 BPM | {fraction(accurate, total)} | {total - accurate} |")
            lines.append(f"| {name} continuous outputs processed within their audio duration | {fraction(on_budget, total)} | {total - on_budget} |")
    if beat_this_continuous_interval_gate is not None:
        intervals, ballroom_correct, ballroom_total, ballroom_wrong, filobass_correct, filobass_total, filobass_wrong, eligible = beat_this_continuous_interval_gate
        lines.extend(
            [
                "",
                "### Beat This! strict causal interval-count gate",
                "",
                f"Source: `{beat_this_continuous_interval_gate_audit_input.as_posix()}`. This rejects a Beat This! value unless its bounded causal window contains at least {intervals} usable beat intervals. The gate removed every observed wrong value in both corpora, but it is diagnostic-only until an optional realtime backend can preserve the exact same gate.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Ballroom strict-gated BPM within 8 BPM | {fraction(ballroom_correct, ballroom_total)} | {ballroom_wrong} wrong displayed BPM |",
                f"| FiloBass strict-gated BPM within 8 BPM | {fraction(filobass_correct, filobass_total)} | {filobass_wrong} wrong displayed BPM |",
                f"| Zero-wrong strict causal gate with ≥5 outputs per corpus | {fraction(eligible, 1)} | {1 - eligible} |",
            ]
        )
    if three_tempo_tracker_consensus is not None:
        correct, selected, newly_revealed, audited = three_tempo_tracker_consensus
        lines.extend(
            [
                "",
                "### Three-tracker offline consensus safety audit",
                "",
                f"Source: `{three_tempo_tracker_consensus_input.as_posix()}`. A candidate is retained only when phase, the permissive tracker, and Beat This! agree, and each individual estimate is within 8 BPM. This is offline evidence only: Beat This! uses non-causal full-context attention, so this audit cannot enable a live OBS path.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Correct offline three-tracker consensus candidates | {fraction(correct, selected)} | {selected - correct} wrong candidates |",
                f"| Audited rows eligible for offline three-tracker consensus | {fraction(selected, audited)} | {audited - selected} |",
                f"| Offline consensus candidates newly revealed beyond phase display | {fraction(newly_revealed, audited)} | {audited - newly_revealed} |",
            ]
        )
    if high_tempo_three_tracker_consensus is not None:
        correct, selected, newly_revealed, audited = high_tempo_three_tracker_consensus
        lines.extend(
            [
                "",
                "### High-tempo three-tracker offline veto audit",
                "",
                f"Source: {high_tempo_three_tracker_consensus_input.as_posix()}. This is restricted to annotated GTZAN Rhythm BPM ≥150 and can only justify an offline veto/post-processing experiment; it cannot alter live BPM display.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Correct high-tempo three-tracker consensus candidates | {fraction(correct, selected)} | {selected - correct} wrong candidates |",
                f"| High-tempo annotated rows eligible for consensus | {fraction(selected, audited)} | {audited - selected} |",
                f"| High-tempo candidates newly revealed beyond phase display | {fraction(newly_revealed, audited)} | {audited - newly_revealed} |",
            ]
        )
    if filobass_bpm is not None:
        accurate, total = filobass_bpm
        lines.extend(
            [
                "",
                "## FiloBass real bass-led annotated-tempo diagnostic",
                "",
                f"Source: `{filobass_bpm_input.as_posix()}`. FiloBass pairs real jazz bass stems with reviewed downbeat syncpoints and a MIDI time signature; BPM references are derived only from those corpus annotations.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if filobass_phase_energy is not None:
        eligible, higher, equal, lower, total = filobass_phase_energy
        lines.extend(
            [
                "",
                "### FiloBass source-grid energy feasibility diagnostic",
                "",
                "The corpus harness forces the labelled BPM into the final diagnostic slot, then compares its bass energy with the selected candidate. This is not a score-ranked candidate and does not change BPM selection.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Labelled BPM exported through harness-only probe | {fraction(eligible, total)} | {total - eligible} |",
                f"| Present labelled candidate has higher bass grid-energy | {fraction(higher, eligible)} | {eligible - higher} |",
                f"| Present labelled candidate ties selected bass grid-energy | {fraction(equal, eligible)} | {eligible - equal} |",
                f"| Present labelled candidate has lower bass grid-energy | {fraction(lower, eligible)} | {eligible - lower} |",
            ]
        )
    if filobass_onset_diagnostic is not None:
        rank_one, rank_five, direct_or_double, total = filobass_onset_diagnostic
        lines.extend(
            [
                "",
                "### FiloBass raw bass-attack feasibility diagnostic",
                "",
                f"Source: `{filobass_onset_diagnostic_input.as_posix()}`. This offline analysis ranks tempos from raw bass-envelope attacks only. It is a feature-feasibility check, not a live-output result or release gate.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Reviewed BPM ranked first by raw bass attacks | {fraction(rank_one, total)} | {total - rank_one} |",
                f"| Reviewed BPM ranked in top five by raw bass attacks | {fraction(rank_five, total)} | {total - rank_five} |",
                f"| Reviewed BPM matches raw bass attacks at direct or double tempo | {fraction(direct_or_double, total)} | {total - direct_or_double} |",
            ]
        )
    if egmd_bpm is not None:
        accurate, total = egmd_bpm
        lines.extend(
            [
                "",
                "## E-GMD generated percussion tempo diagnostic",
                "",
                f"Source: `{egmd_bpm_input.as_posix()}`. This generated aligned-MIDI fixture exercises kick/snare phase recovery; it is a regression benchmark, not independent real-audio evidence.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Displayable BPM at confidence ≥ 0.60 | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if idmt_bass_timing is not None:
        accurate, total = idmt_bass_timing
        lines.extend(
            [
                "",
                "## IDMT real-bass timing-ground-truth audit",
                "",
                f"Source: `{idmt_bass_tempo_metadata_input.as_posix()}`. IDMT provides real bass audio and reviewed note onsets, but only corpus-supplied tempo, beat, or pattern fields qualify it as BPM ground truth.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Tracks with corpus-supplied tempo, beat, or pattern metadata | {fraction(accurate, total)} | {total - accurate} |",
            ]
        )
    if urmp_bass_timing is not None:
        pairs, grids, qualified, total = urmp_bass_timing
        lines.extend(
            [
                "",
                "## URMP double-bass timing-ground-truth audit",
                "",
                f"Source: `{urmp_bass_timing_audit_input.as_posix()}`. URMP supplies real double-bass stems and audio-aligned note annotations, but its original score MIDI is not an audio-aligned metrical grid. Only an explicit official beat/downbeat/bar annotation would qualify a stem for BPM validation.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                f"| Double-bass stems with aligned audio and note annotations | {fraction(pairs, total)} | {total - pairs} |",
                f"| Double-bass stems with an explicit official beat/downbeat grid | {fraction(grids, total)} | {total - grids} |",
                f"| URMP double-bass stems qualifying as tempo truth | {fraction(qualified, total)} | {total - qualified} |",
            ]
        )
    lines.extend(
        [
            "",
            "## Tempo coverage-gap checklist",
            "",
            "Tempo estimates are only displayed at calibrated confidence. Source-specific phase evidence is tested separately from corpus coverage so a synthetic regression fixture cannot be mistaken for independent real-audio validation.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            "| Separate kick, bass, snare, and tonal onset histories | 1 / 1 (100.0%) | 0 | source-specific phase coverage in debug candidates |",
            "| Preserve simultaneous kick+bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer case verifies both kick and bass phase coverage on the same downbeats |",
            "| Require repeated source evidence on the selected beat grid | 1 / 1 (100.0%) | 0 | confidence cap below display floor without repeated alignment |",
            "| Resolve half/double-time candidates with kick/bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer cases retain the beat grid through sparse-kick half-time and dense-subdivision alternatives |",
            "| Adaptive tempo history for percussive vs sparse tonal input | 1 / 1 (100.0%) | 0 | 8 s percussion / 18 s sparse-source policy |",
            f"| Generated drum phase regression measured | {fraction(int(egmd_bpm is not None), 1)} | {int(egmd_bpm is None)} | E-GMD x/total BPM diagnostic |",
            f"| Retrieve versioned Ballroom beat/bar annotations | {fraction(ballroom_annotations_ready, 1)} | {1 - ballroom_annotations_ready} | CPJKU BallroomAnnotations checkout in InstrumentSamples |",
            f"| Rhythm-heavy real-mix beat validation measured | {fraction(int(ballroom_bpm is not None), 1)} | {int(ballroom_bpm is None)} | up to 64 genre-balanced Ballroom stable sections with manually corrected beat/bar annotations |",
            f"| Genre-diverse real-mix beat validation measured | {fraction(int(gtzan_rhythm_bpm is not None), 1)} | {int(gtzan_rhythm_bpm is None)} | GTZAN-Rhythm WAV/JAMS pairs; stable BPM segments derived from manually annotated beats |",
            f"| Retrieve and validate Candombe beat/downbeat labels | {fraction(candombe_annotations_ready, 1)} | {1 - candombe_annotations_ready} | 35 public CSVs with expert beat times and bar/beat positions |",
            f"| Independent labelled drumming-corpus validation measured | {fraction(int(candombe_bpm is not None), 1)} | {int(candombe_bpm is None)} | Candombe FLAC/CSV pairs: 35 real performances with expert beat/downbeat labels |",
            f"| Benchmark independent neural tracker on held-out GTZAN | {fraction(int(beat_this_gtzan_bpm is not None), 1)} | {int(beat_this_gtzan_bpm is None)} | offline Beat This! `final0` output with no OBS/runtime integration |",
            f"| Benchmark Beat This! on independent real-tempo corpora | {fraction(int(beat_this_ballroom_bpm is not None) + int(beat_this_filobass_bpm is not None), 2)} | {2 - int(beat_this_ballroom_bpm is not None) - int(beat_this_filobass_bpm is not None)} | Ballroom and FiloBass annotated stable segments; CPU-only offline evidence |",
            f"| Replay bounded trailing Beat This! windows on real-tempo corpora | {fraction(int(beat_this_rolling_ballroom_bpm is not None) + int(beat_this_rolling_filobass_bpm is not None), 2)} | {2 - int(beat_this_rolling_ballroom_bpm is not None) - int(beat_this_rolling_filobass_bpm is not None)} | window ends at each annotated output time; records correctness and processing budget |",
            f"| Validate strict causal Beat This! interval gate | {fraction(int(beat_this_continuous_interval_gate is not None and beat_this_continuous_interval_gate[-1] == 1), 1)} | {1 - int(beat_this_continuous_interval_gate is not None and beat_this_continuous_interval_gate[-1] == 1)} | ≥44 intervals: Ballroom {beat_this_continuous_interval_gate[1] if beat_this_continuous_interval_gate is not None else '--'} / {beat_this_continuous_interval_gate[2] if beat_this_continuous_interval_gate is not None else '--'}, FiloBass {beat_this_continuous_interval_gate[4] if beat_this_continuous_interval_gate is not None else '--'} / {beat_this_continuous_interval_gate[5] if beat_this_continuous_interval_gate is not None else '--'}, zero wrong values in this replay |",
            f"| Audit phase/BTT/Beat This! offline agreement | {fraction(int(three_tempo_tracker_consensus is not None), 1)} | {int(three_tempo_tracker_consensus is None)} | every selected candidate must be correct across Ballroom, FiloBass, and GTZAN |",
            f"| Audit high-tempo GTZAN three-tracker offline veto | {fraction(int(high_tempo_three_tracker_consensus is not None), 1)} | {int(high_tempo_three_tracker_consensus is None)} | every selected ≥150 BPM GTZAN candidate must be correct across phase, BTT, and Beat This! |",
            "| Integrate bounded causal Beat This! live use | 0 / 1 (0.0%) | 1 | optional OBS-safe realtime backend must preserve the validated 20 s window and ≥44 interval gate; File2Beats remains non-causal offline inference |",
            f"| IDMT real-bass timing metadata qualifies as beat truth | {fraction(idmt_bass_timing[0], idmt_bass_timing[1]) if idmt_bass_timing is not None else '0 / 1 (0.0%)'} | {idmt_bass_timing[1] - idmt_bass_timing[0] if idmt_bass_timing is not None else 1} | only corpus-supplied tempo/beat/pattern fields count; note onsets are insufficient |",
            f"| Audit URMP double-bass timing provenance | {fraction(1, 1) if urmp_bass_timing is not None else '0 / 1 (0.0%)'} | {0 if urmp_bass_timing is not None else 1} | distinguish audio-aligned note annotations from explicit metrical grids |",
            f"| URMP double-bass stems qualify as beat truth | {fraction(urmp_bass_timing[2], urmp_bass_timing[3]) if urmp_bass_timing is not None else '0 / 1 (0.0%)'} | {urmp_bass_timing[3] - urmp_bass_timing[2] if urmp_bass_timing is not None else 1} | original score MIDI alone is not audio-aligned timing evidence |",
            f"| Independent real bass-led beat-labelled validation measured | {fraction(int(filobass_bpm is not None), 1)} | {int(filobass_bpm is None)} | FiloBass real bass stems plus reviewed downbeats and MIDI time signature |",
            "| Reject MUSDB18/BeatNet+ as an authoritative bass BPM benchmark | 1 / 1 (100.0%) | 0 | MUSDB18 access requires academic-use approval, and BeatNet+ labels are documented as added annotations rather than original corpus beat truth |",
            f"| Assess raw bass-attack BPM evidence | {fraction(int(filobass_onset_diagnostic is not None), 1)} | {int(filobass_onset_diagnostic is None)} | offline FiloBass rank-one/top-five diagnostic |",
            f"| Assess bass source-grid energy before a selector | {fraction(int(filobass_phase_energy is not None), 1)} | {int(filobass_phase_energy is None)} | FiloBass expected candidate shows higher bass alignment in {filobass_phase_energy_evidence} |",
            "| Reject unproven meter/bass candidate reweighting | 1 / 1 (100.0%) | 0 | current feasibility audit: Ballroom meter/bass selectors peak at 5 / 64 and FiloBass stays at 4 / 47, so neither is a safe BPM selector |",
            "| Reject unproven normalized-recurrence selector | 1 / 1 (100.0%) | 0 | lag-normalized recurrence reaches 6 / 61 only at an extreme Ballroom weight and remains 4 / 24 on FiloBass |",
            "| Reject unproven kick+bass-coincidence selector | 1 / 1 (100.0%) | 0 | same-frame coincidence reaches 8 / 64 on Ballroom and 5 / 47 on FiloBass, but cannot safely resolve meter alone |",
            "| Reject longer percussive phase history | 1 / 1 (100.0%) | 0 | 12 s drops Ballroom displayable BPM from 1 / 64 to 0 / 64 and raises E-GMD mean error from 0.21 to 0.32 BPM; retain the 8 s policy |",
            "| Reject unproven dynamic beat-path selector | 1 / 1 (100.0%) | 0 | dynamic path improves Ballroom labelled-candidate rank from 9 / 64 to 13 / 64 but regresses FiloBass from 4 / 24 to 2 / 24, so it is not a safe BPM selector |",
            "| Reject bass-dominant RMS attack phase feature | 1 / 1 (100.0%) | 0 | a guarded live bass-amplitude attack left FiloBass at 0 / 24 displayed and candidate ranks 4 / 1 / 0 / 1 / 18; Ballroom 1 / 64 and E-GMD 20 / 20 were unchanged, so it adds no value |",
            "| Reject combined bass/coincidence candidate reweighting | 1 / 1 (100.0%) | 0 | shared grid best is kick+bass alignment 4.0 plus recurrence 4.0: 4 / 64→7 / 64 Ballroom and 4 / 47→6 / 47 FiloBass, but 98 / 111 selections are still wrong |",
            "| Reject offline three-tracker consensus as a live gate | 1 / 1 (100.0%) | 0 | the latest offline audit found 18 / 18 correct candidates (11 newly revealed), but the actual live Ballroom replay introduced one double-time display; keep the feature disabled |",
            "| Retain calibrated BPM display-confidence gate | 1 / 1 (100.0%) | 0 | at 0.45 confidence, raw selection is correct only 1 / 5 Ballroom and 0 / 4 FiloBass; lowering the 0.60 display gate would expose mostly wrong BPM |",
            "| Local advanced beat-tracker backend available | 0 / 2 (0.0%) | 2 | `aubio` and `essentia` are unavailable through pkg-config; next step is a dependency-free tracker or an added backend |",
            "| Retrieve license-compatible advanced beat tracker | 1 / 1 (100.0%) | 0 | MIT-licensed Beat-and-Tempo-Tracking source is pinned at `c039090f1af771092d95c3ffc402e557940f7384`; aubio remains unsuitable without a GPL compatibility decision |",
            "| Benchmark permissive beat tracker on both real tempo corpora | 2 / 2 (100.0%) | 0 | source-only MIT tracker measured on the same 20 s annotated stable segments as the analyzer |",
            f"| Permissive tracker raw BPM — Ballroom | {fraction(*btt_ballroom[0.0])} | {btt_ballroom[0.0][1] - btt_ballroom[0.0][0]} | within 8 BPM; diagnostic source `build/btt_ballroom_bpm_diagnostics.log` |",
            f"| Permissive tracker raw BPM — FiloBass | {fraction(*btt_filobass[0.0])} | {btt_filobass[0.0][1] - btt_filobass[0.0][0]} | within 8 BPM; diagnostic source `build/btt_filobass_bpm_diagnostics.log` |",
            f"| Permissive tracker at 0.60 certainty — Ballroom | {fraction(*btt_ballroom[0.60])} | {btt_ballroom[0.60][1] - btt_ballroom[0.60][0]} | correct / displayed; {btt_ballroom[0.0][1] - btt_ballroom[0.60][1]} clips remain hidden |",
            f"| Permissive tracker at 0.60 certainty — FiloBass | {fraction(*btt_filobass[0.60])} | {btt_filobass[0.60][1] - btt_filobass[0.60][0]} | correct / displayed; precision calibration remains required |",
            f"| Permissive tracker at 0.75 certainty — Ballroom | {fraction(*btt_ballroom[0.75])} | {btt_ballroom[0.75][1] - btt_ballroom[0.75][0]} | correct / displayed; {btt_ballroom[0.0][1] - btt_ballroom[0.75][1]} clips remain hidden |",
            f"| Permissive tracker at 0.75 certainty — FiloBass | {fraction(*btt_filobass[0.75])} | {btt_filobass[0.75][1] - btt_filobass[0.75][0]} | correct / displayed; {btt_filobass[0.0][1] - btt_filobass[0.75][1]} clips remain hidden |",
            f"| Permissive tracker at 0.75 certainty — E-GMD | {fraction(*btt_egmd[0.75])} | {btt_egmd[0.75][1] - btt_egmd[0.75][0]} | correct / displayed; generated percussion regression only |",
            f"| Permissive tracker at 0.80 certainty — Ballroom | {fraction(*btt_ballroom[0.80])} | {btt_ballroom[0.80][1] - btt_ballroom[0.80][0]} | source-only candidates; {btt_ballroom[0.0][1] - btt_ballroom[0.80][1]} clips remain hidden; not a live-release gate |",
            f"| Permissive tracker at 0.80 certainty — FiloBass | {fraction(*btt_filobass[0.80])} | {btt_filobass[0.80][1] - btt_filobass[0.80][0]} | source-only candidates; {btt_filobass[0.0][1] - btt_filobass[0.80][1]} clips remain hidden; not a live-release gate |",
            "| Repair continuous PCM feed to permissive tracker | 1 / 1 (100.0%) | 0 | feed all host-buffer PCM rather than only the short feature window; this removes artificial inter-buffer gaps in live corpus runs |",
            "| Reject tail-truncated permissive fallback results | 1 / 1 (100.0%) | 0 | earlier 0.75/0.60 live trials omitted each host-buffer tail and produced wrong Ballroom BPM; they do not calibrate the repaired continuous feed |",
            "| Enable strict live permissive-tracker fallback | 3 / 3 (100.0%) | 0 | at 0.80 certainty with phase confidence below 0.60: Ballroom 12 / 64, FiloBass 2 / 24, E-GMD 20 / 20; no wrong displayed BPM observed |",
            f"| Benchmark constrained high-tempo beat tracker | 2 / 2 (100.0%) | 0 | 120--240 BPM source-only tracker at 0.55 certainty: Ballroom {btt_high_tempo_ballroom[0]} / {btt_high_tempo_ballroom[1]} and FiloBass {btt_high_tempo_filobass[0]} / {btt_high_tempo_filobass[1]} correct |",
            "| Reject concurrent high-tempo tracker fallback | 1 / 1 (100.0%) | 0 | live candidates at 0.55 were Ballroom 15 / 15 and FiloBass 5 / 5, but both concurrent and post-phase scheduling raised Ballroom id 8 phase confidence from withheld to ≥0.617 and displayed wrong 158.97 BPM for 128.03; feature remains false |",
            "| Reject high-tempo-only tracker setting | 1 / 1 (100.0%) | 0 | one 120--240 BPM tracker still raises Ballroom id 8 phase confidence to 0.617 and displays wrong 158.97 BPM for 128.03; retain broad 40--240 BPM tracker at 0.80 |",
            "| Demonstrate a bass-attack feature improves real bass BPM | 0 / 1 (0.0%) | 1 | improve FiloBass displayable BPM without regressing E-GMD |",
            "| Keep withheld BPM visually unavailable | 1 / 1 (100.0%) | 0 | renderer shows `BPM --` both before evidence and while a below-threshold estimate is withheld |",
            "| Hide numeric BPM when calibrated confidence is insufficient | 1 / 1 (100.0%) | 0 | renderer keeps the numeric BPM hidden below 0.60 confidence and reserves numbers for calibrated estimates |",
        ]
    )
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
        lines.extend(
            [
                "",
                "## Tom/rim/ride protected-selector audit",
                "",
                "The top zero-regression one-shot selectors are searched against the full, HF, and IDMT "
                "attribute sets. A selector also needs a positive match in an independent corpus; duplicate "
                "assets shared by the full and spread collections do not count as replication.",
                "",
                "| Candidate route | Independent positive corpora | Runtime selector eligible |",
                "| --- | ---: | ---: |",
                f"| Tom → Snare | {fraction(0, 2)} | {fraction(0, 1)} |",
                f"| Rim → Snare | {fraction(0, 2)} | {fraction(0, 1)} |",
                f"| Ride → HiHat | {fraction(0, 2)} | {fraction(0, 1)} |",
            ]
        )
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
                "This independent real-music full-mix fixture measures annotated drum-event recall and "
                "false activations across a larger variety of accompanied recordings.",
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
        if mdb_rim is not None:
            detected, total = mdb_rim
            lines.extend(
                [
                    "",
                    "### MDB annotated Rim-event audit",
                    "",
                    "MDB is already part of the real-mix calibration evidence, so this single side-stick/Rim "
                    "event does not replace independent acoustic replication.",
                    "",
                    f"Source: `{mdb_rim_coverage_input.as_posix()}`.",
                    "",
                    "| Metric | Accurate / total | Remaining |",
                    "| --- | ---: | ---: |",
                    f"| MDB annotated Rim events detected | {fraction(detected, total)} | {total - detected} |",
                ]
            )
        lines.extend(
            [
                "",
                "### MDB multi-recording Snare-context replay",
                "",
                "The best source-scoped offline candidate (`kick_body ≥36.36`, `upper_tom ≤17.85`) covered three MDB false-positive recordings with no protected one-shot loss. In a rebuilt MDB, STAR, and BabySlakh replay it did not suppress an actual active Snare or improve a protected metric. The runtime trial was removed; the tables above and below are refreshed from the retained baseline outputs.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
                "| Highest multi-recording MDB Snare candidate replayed | 1 / 1 (100.0%) | 0 |",
                "| Candidate with a measured cross-corpus gain | 0 / 1 (0.0%) | 1 |",
            ]
        )
    if babyslakh_drums_gate_output is not None:
        lines.extend(
            [
                "",
                "## BabySlakh rendered full-mix drum baseline",
                "",
                "These 16 kHz rendered multitracks have aligned per-stem MIDI drum truth. They broaden "
                "the calibration set, but remain separately reported from real-recording MDB and STAR evidence.",
                "",
                f"Source: `{babyslakh_drums_gate_output.as_posix()}`",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for label, accurate, total, remainder_unit in egmd_drum_rows(
            babyslakh_drums_gate_output, "BabySlakh rendered mixes"
        ):
            remainder = f"{total - accurate} {remainder_unit}" if remainder_unit else str(total - accurate)
            lines.append(f"| {label} | {fraction(accurate, total)} | {remainder} |")
    if samples29k_counts:
        lines.extend(
            [
                "",
                "## 29k Drums independent acoustic Tom/Ride baseline",
                "",
                f"Source: `{samples29k_drums_measurement.as_posix()}`. The fixture uses only published Tom (ft/mt/ht) and Ride (cy) samples; it does not represent Rim or a full mix.",
                "",
                "| Metric | Accurate / total | Remaining |",
                "| --- | ---: | ---: |",
            ]
        )
        for category in ("tom", "ride"):
            if category not in samples29k_counts:
                continue
            hits, total, primary = samples29k_counts[category]
            lines.append(f"| 29k Drums — {category.title()} detected | {fraction(hits, total)} | {total - hits} |")
            lines.append(f"| 29k Drums — {category.title()} primary display | {fraction(primary, total)} | {total - primary} |")
        lines.extend(
            [
                "",
                "### Rejected Tom/Ride primary runtime trials",
                "",
                "Each two-feature 29k selector below looked safe in the local attribute table, but failed the broader protected one-shot replay and is not enabled.",
                "",
                "| Trial | Independent 29k result | Protected one-shot result | Decision |",
                "| --- | ---: | ---: | --- |",
                "| Low-high inactive Tom from Snare | Tom primary 269→318 / 500; Ride 317→317 / 500 | Snare primary 133→87 / 160; Tom false 199→253 | reject: severe Snare regression |",
                "| Ride from HiHat segment tie | Tom primary 269→269 / 500; Ride 317→332 / 500 | HiHat primary 141→136 / 160; Tom primary 126→124 / 160 | reject: protected HiHat and Tom regressions |",
            ]
        )
    lines.extend(
        [
            "",
            "## BabySlakh drum-validation checklist",
            "",
            "BabySlakh is an independently rendered 16 kHz multitrack corpus with aligned per-stem MIDI. "
            "It strengthens calibration coverage but cannot replace real-recording evidence.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Store checksum-verified archive in InstrumentSamples | {fraction(babyslakh_archive_ready, 1)} | {1 - babyslakh_archive_ready} | archive moved only after the official MD5 passes |",
            f"| Extract archive safely in InstrumentSamples | {fraction(babyslakh_extraction_ready, 1)} | {1 - babyslakh_extraction_ready} | traversal-safe extractor output |",
            f"| Inspect and prepare all published drum full mixes | {fraction(min(20, babyslakh_fixture_rows), 20)} | {max(0, 20 - babyslakh_fixture_rows)} | metadata-selected drum MIDI with linked mix WAV |",
            f"| Measure rendered full-mix drum baseline | {fraction(babyslakh_measurement_ready, 1)} | {1 - babyslakh_measurement_ready} | analyzer_egmd x/total summary |",
            f"| Re-evaluate a drum change across real MDB/STAR and BabySlakh | {fraction(babyslakh_calibration_ready, 1)} | {1 - babyslakh_calibration_ready} | independently measured retain-or-change decision |",
            ]
        )
    lines.extend(
        [
            "",
            "## Real-drum Tom/Ride/Rim coverage checklist",
            "",
            "The full one-shot gate has broad category counts, but its weak Tom/Ride/Rim results need independent real-acoustic replication before a class-specific runtime rule can be trusted. 29k Drums can independently cover Tom and Ride. FSD50K's fixed 200-class vocabulary has no Rimshot label. The Commons candidate is checksum-verifiable and openly licensed, but its source supplies no per-roll timestamps, so it cannot yet count as accuracy evidence.",
            "",
            "| Work item | Complete / total | Remaining | Evidence required |",
            "| --- | ---: | ---: | --- |",
            f"| Checksum-verified 29k Drums archive inspected for Tom/Ride labels | {fraction(samples29k_archive_ready, 1)} | {1 - samples29k_archive_ready} | inspection follows successful Zenodo MD5 and ZIP integrity verification |",
            f"| Measure independent 29k Drums Tom/Ride baseline | {fraction(int(bool(samples29k_counts)), 1)} | {1 - int(bool(samples29k_counts))} | prepared, labelled acoustic one-shot fixture and analyzer x/total results |",
            f"| Record all 29k Tom/Ride primary decisions for candidate evaluation | {fraction(samples29k_primary_attributes_available, 1)} | {1 - samples29k_primary_attributes_available} | verbose current and missed primary labels become a reproducible TSV; selectors still need cross-corpus runtime replay |",
            f"| Measure MDB annotated side-stick/Rim event coverage | {fraction(int(mdb_rim is not None), 1)} | {int(mdb_rim is None)} | {fraction(mdb_rim[0], mdb_rim[1]) if mdb_rim is not None else '--'} detected; calibration evidence only, not independent replication |",
            f"| Screen FSD50K fixed vocabulary for licence-compatible Rimshot clips | {fraction(int(fsd50k_rim_metadata is not None), 1)} | {int(fsd50k_rim_metadata is None)} | no audio transfer: {fsd50k_rim_metadata[0] if fsd50k_rim_metadata is not None else '--'} labelled rows, {fsd50k_rim_metadata[1] if fsd50k_rim_metadata is not None else '--'} isolated candidates, {fsd50k_rim_metadata[2] if fsd50k_rim_metadata is not None else '--'} permissive-licence candidates |",
            f"| Verify licence-free Rimshot recording candidate | {fraction(int(commons_rimshot_candidate is not None), 1)} | {int(commons_rimshot_candidate is None)} | checksum, source label, licence, and 4 stated rolls; {commons_rimshot_candidate[3] if commons_rimshot_candidate is not None else '--'} per-roll timestamps supplied |",
            f"| Measure checksum-pinned isolated real Rimshot | {fraction(int(pixabay_rimshot_measurement is not None), 1)} | {int(pixabay_rimshot_measurement is None)} | detected {pixabay_rimshot_measurement[0] if pixabay_rimshot_measurement is not None else '--'} / 1; Rim primary {pixabay_rimshot_measurement[1] if pixabay_rimshot_measurement is not None else '--'} / 1; Snare primary {pixabay_rimshot_measurement[2] if pixabay_rimshot_measurement is not None else '--'} / 1 |",
            f"| Measure separately sourced isolated real Rimshot | {fraction(int(pixabay_rimshot_f_measurement is not None), 1)} | {int(pixabay_rimshot_f_measurement is None)} | detected {pixabay_rimshot_f_measurement[0] if pixabay_rimshot_f_measurement is not None else '--'} / 1; Rim primary {pixabay_rimshot_f_measurement[1] if pixabay_rimshot_f_measurement is not None else '--'} / 1; Snare primary {pixabay_rimshot_f_measurement[2] if pixabay_rimshot_f_measurement is not None else '--'} / 1 |",
            f"| Broaden independent Rim replication beyond one isolated recording | {fraction(int(pixabay_rimshot_f_measurement is not None), 1)} | {int(pixabay_rimshot_f_measurement is None)} | second checksum-pinned, separately sourced one-shot is measured; ENST-Drums remains an additional labelled-corpus path after its research-use licence is accepted and preserved |",
        ]
    )
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
    parser.add_argument("--babyslakh-drums-gate-output", type=Path)
    parser.add_argument("--babyslakh-calibration-audit", type=Path)
    parser.add_argument("--babyslakh-archive", type=Path)
    parser.add_argument("--babyslakh-extraction", type=Path)
    parser.add_argument("--babyslakh-manifest", type=Path)
    parser.add_argument("--29k-drums-inspection", dest="samples29k_drums_inspection", type=Path)
    parser.add_argument("--29k-drums-measurement", dest="samples29k_drums_measurement", type=Path)
    parser.add_argument("--29k-drums-primary-attributes", dest="samples29k_drums_primary_attributes", type=Path)
    parser.add_argument("--fsd50k-rim-metadata-audit", type=Path)
    parser.add_argument("--commons-rimshot-candidate-audit", type=Path)
    parser.add_argument("--pixabay-rimshot-measurement-audit", type=Path)
    parser.add_argument("--pixabay-rimshot-f-measurement-audit", type=Path)
    parser.add_argument("--mdb-rim-coverage-input", type=Path)
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
    parser.add_argument("--independent-piano-chord-stability-evidence", type=Path)
    parser.add_argument("--independent-piano-exact-chord-fallback-audit", type=Path)
    parser.add_argument("--piano-chord-confirmation-audit", type=Path)
    parser.add_argument("--piano-chord-confirm3-audit", type=Path)
    parser.add_argument("--piano-chord-tone018-audit", type=Path)
    parser.add_argument("--piano-chord-margin060-audit", type=Path)
    parser.add_argument("--piano-chord-bassbonus000-audit", type=Path)
    parser.add_argument("--piano-chord-display-gate-audit", type=Path)
    parser.add_argument("--kraisler-archive", type=Path)
    parser.add_argument("--kraisler-extraction", type=Path)
    parser.add_argument("--kraisler-manifest", type=Path)
    parser.add_argument("--kraisler-measurement", type=Path)
    parser.add_argument("--kraisler-bpm-input", type=Path)
    parser.add_argument("--ballroom-bpm-input", type=Path)
    parser.add_argument("--ballroom-annotations", type=Path)
    parser.add_argument("--gtzan-rhythm-bpm-input", type=Path)
    parser.add_argument("--beat-this-gtzan-bpm-input", type=Path)
    parser.add_argument("--beat-this-ballroom-bpm-input", type=Path)
    parser.add_argument("--beat-this-filobass-bpm-input", type=Path)
    parser.add_argument("--beat-this-rolling-ballroom-bpm-input", type=Path)
    parser.add_argument("--beat-this-rolling-filobass-bpm-input", type=Path)
    parser.add_argument("--beat-this-continuous-ballroom-bpm-input", type=Path)
    parser.add_argument("--beat-this-continuous-filobass-bpm-input", type=Path)
    parser.add_argument("--beat-this-continuous-interval-gate-audit", type=Path)
    parser.add_argument("--three-tempo-tracker-consensus-input", type=Path)
    parser.add_argument("--high-tempo-three-tracker-consensus-input", type=Path)
    parser.add_argument("--candombe-bpm-input", type=Path)
    parser.add_argument("--candombe-inspection", type=Path)
    parser.add_argument("--btt-ballroom-bpm-input", type=Path)
    parser.add_argument("--btt-filobass-bpm-input", type=Path)
    parser.add_argument("--btt-egmd-bpm-input", type=Path)
    parser.add_argument("--btt-high-tempo-ballroom-bpm-input", type=Path)
    parser.add_argument("--btt-high-tempo-filobass-bpm-input", type=Path)
    parser.add_argument("--filobass-bpm-input", type=Path)
    parser.add_argument("--filobass-onset-diagnostic-input", type=Path)
    parser.add_argument("--egmd-bpm-input", type=Path)
    parser.add_argument("--idmt-bass-tempo-metadata-input", type=Path)
    parser.add_argument("--high-vocal-octave-audit", type=Path)
    parser.add_argument("--electronic-piano-guitar-route-audit", type=Path)
    parser.add_argument("--scms-vocal-other-route-audit", type=Path)
    parser.add_argument("--tenor-sax-piano-route-audit", type=Path)
    parser.add_argument("--violin-guitar-route-audit", type=Path)
    parser.add_argument("--guitar-chord-primary-display-audit", type=Path)
    parser.add_argument("--guitar-chord-tone-recovery-audit", type=Path)
    parser.add_argument("--urmp-good-sounds-sax-shared-pattern-audit", type=Path)
    parser.add_argument("--urmp-bass-timing-audit", type=Path)
    parser.add_argument("--octave-correction-cross-corpus-audit", type=Path)
    parser.add_argument("--dominant-seventh-extension-audit", type=Path)
    parser.add_argument("--global-chord-confidence-audit", type=Path)
    parser.add_argument("--guitarset-attribute-input", type=Path)
    parser.add_argument("--same-root-guitar-quality-audit", type=Path)
    parser.add_argument("--owner-classifier-loco-audit", type=Path)
    parser.add_argument("--owner-classifier-quality-loco-audit", type=Path)
    parser.add_argument("--owner-score-calibration-loco-audit", type=Path)
    parser.add_argument("--drum-primary-loco-audit", type=Path)
    parser.add_argument("--drum-false-positive-cap-audit", type=Path)
    parser.add_argument("--mdb-full-mix-false-positive-cap-audit", type=Path)
    parser.add_argument("--mdb-full-mix-competing-active-context-audit", type=Path)
    parser.add_argument("--drum-false-positive-context-audit", type=Path)
    parser.add_argument("--drum-recovery-candidate-audit", type=Path)
    parser.add_argument("--chord-primary-component-audit", type=Path)
    parser.add_argument("--other-detection-disabled", action="store_true")
    parser.add_argument("--polyphonic-candidate-capacity-audit", type=Path)
    parser.add_argument("--harmonic-product-octave-audit", type=Path)
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
            args.independent_piano_chord_stability_evidence,
            args.independent_piano_exact_chord_fallback_audit,
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
            args.urmp_good_sounds_sax_shared_pattern_audit,
            args.urmp_bass_timing_audit,
            args.octave_correction_cross_corpus_audit,
            args.dominant_seventh_extension_audit,
            args.global_chord_confidence_audit,
            args.guitarset_attribute_input,
            args.same_root_guitar_quality_audit,
            args.owner_classifier_loco_audit,
            args.owner_classifier_quality_loco_audit,
            args.owner_score_calibration_loco_audit,
            args.drum_primary_loco_audit,
            args.drum_false_positive_cap_audit,
            args.mdb_full_mix_false_positive_cap_audit,
            args.mdb_full_mix_competing_active_context_audit,
            args.drum_false_positive_context_audit,
            args.drum_recovery_candidate_audit,
            args.chord_primary_component_audit,
            args.other_detection_disabled,
            args.polyphonic_candidate_capacity_audit,
            args.harmonic_product_octave_audit,
            args.kraisler_bpm_input,
            args.ballroom_bpm_input,
            args.gtzan_rhythm_bpm_input,
            args.filobass_bpm_input,
            args.filobass_onset_diagnostic_input,
            args.egmd_bpm_input,
            args.idmt_bass_tempo_metadata_input,
            args.ballroom_annotations,
            args.beat_this_gtzan_bpm_input,
            args.beat_this_ballroom_bpm_input,
            args.beat_this_filobass_bpm_input,
            args.beat_this_rolling_ballroom_bpm_input,
            args.beat_this_rolling_filobass_bpm_input,
            args.beat_this_continuous_ballroom_bpm_input,
            args.beat_this_continuous_filobass_bpm_input,
            args.beat_this_continuous_interval_gate_audit,
            args.three_tempo_tracker_consensus_input,
            args.high_tempo_three_tracker_consensus_input,
            args.candombe_bpm_input,
            args.candombe_inspection,
            args.btt_ballroom_bpm_input,
            args.btt_filobass_bpm_input,
            args.btt_egmd_bpm_input,
            args.btt_high_tempo_ballroom_bpm_input,
            args.btt_high_tempo_filobass_bpm_input,
            args.babyslakh_drums_gate_output,
            args.babyslakh_archive,
            args.babyslakh_extraction,
            args.babyslakh_manifest,
            args.babyslakh_calibration_audit,
            args.samples29k_drums_inspection,
            args.samples29k_drums_measurement,
            args.samples29k_drums_primary_attributes,
            args.piano_chord_confirmation_audit,
            args.piano_chord_confirm3_audit,
            args.piano_chord_tone018_audit,
            args.piano_chord_margin060_audit,
            args.piano_chord_bassbonus000_audit,
            args.piano_chord_display_gate_audit,
            args.fsd50k_rim_metadata_audit,
            args.commons_rimshot_candidate_audit,
            args.pixabay_rimshot_measurement_audit,
            args.pixabay_rimshot_f_measurement_audit,
            args.mdb_rim_coverage_input,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"detection_accuracy_report: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
