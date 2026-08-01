#!/usr/bin/env python3
"""Evaluate same-pitch display-row shadow opportunities in real-note TSVs."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import pathlib
import re
import statistics


NOTE_BASE = {
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
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")
NOTE_CELL_RE = re.compile(r"([A-G]#?-?\d+):([0-9.]+)")
ThresholdMatch = tuple[int, int, float, float, float, float | None]

ROW_FOR_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
}

ROW_NOTE_FIELDS = {
    "bass": "bass_notes",
    "guitar": "guitar_notes",
    "piano": "piano_notes",
    "vocals": "vocal_notes",
    "other": "other_notes",
}

ROW_VISUAL_NOTE_FIELDS = {
    "bass": "bass_visual_notes",
    "guitar": "guitar_visual_notes",
    "piano": "piano_visual_notes",
    "vocals": "vocal_visual_notes",
    "other": "other_visual_notes",
}
ROW_NAMES = tuple(ROW_NOTE_FIELDS)

ROW_SCORE_FIELDS = {
    "bass": "bass_score",
    "guitar": "guitar_score",
    "piano": "keyboard_score",
    "vocals": "vocal_score",
    "other": "other_score",
}

NUMERIC_FIELDS = [
    "target_level",
    "shadow_level",
    "target_score",
    "shadow_score",
    "debug_conf",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "centroid",
    "slope",
    "noise",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "raw_expected_ratio",
    "raw_expected_rank",
]

ROW_OWNER_ALIASES = {
    "bass": {"bass"},
    "guitar": {"guitar"},
    "piano": {"keyboard", "piano"},
    "vocals": {"vocal", "vocals"},
    "other": {"other"},
}

SIMULATION_RULES = (
    "owner_shadow_score2_level",
    "owner_shadow_score15_level",
    "score2_level_no_owner",
    "runtime_keyboard_vocal_weak",
    "weak_target_shadow_owned",
    "runtime_guitar_bass_measured",
    "runtime_keyboard_bass_weak",
    "runtime_keyboard_bass_dominant",
    "runtime_keyboard_bass_guarded",
    "runtime_vocal_bass_owned",
    "runtime_other_bass_legacy",
    "runtime_other_bass_measured",
    "runtime_other_bass_guarded",
    "runtime_other_vocal_measured",
    "runtime_other_vocal_cpp_guarded",
)


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note or "")
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def parse_note_cells(value: str) -> list[tuple[int, float]]:
    cells: list[tuple[int, float]] = []
    for note, level_text in NOTE_CELL_RE.findall(value or ""):
        midi = midi_from_note(note)
        if midi is None:
            continue
        try:
            level = float(level_text)
        except ValueError:
            continue
        cells.append((midi, level))
    return cells


def exact_level(row: dict[str, str], row_name: str, midi: int) -> float:
    visual_field = ROW_VISUAL_NOTE_FIELDS[row_name]
    field = visual_field if visual_field in row else ROW_NOTE_FIELDS[row_name]
    return max((level for candidate_midi, level in parse_note_cells(row.get(field, "")) if candidate_midi == midi), default=0.0)


def as_float(row: dict[str, str], field: str) -> float | None:
    try:
        text = row.get(field, "")
    except KeyError:
        return None
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def as_int(row: dict[str, str], field: str) -> int | None:
    value = as_float(row, field)
    if value is None:
        return None
    return int(round(value))


def record_debug_midi(record: dict[str, str]) -> int | None:
    value = as_int(record, "debug_midi")
    if value is not None:
        return value
    return midi_from_note(record.get("debug_note", ""))


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def med(values: list[float]) -> str:
    if not values:
        return "--"
    ordered = sorted(values)
    return (
        f"min={ordered[0]:.3f} q25={quantile(ordered, 0.25):.3f} "
        f"med={statistics.median(ordered):.3f} q75={quantile(ordered, 0.75):.3f} "
        f"max={ordered[-1]:.3f}"
    )


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{numerator * 100.0 / denominator:.1f}%"


def gain_per_protected(extra_hits: int, protected_hits: int) -> str:
    if protected_hits <= 0:
        return "inf" if extra_hits > 0 else "0.00"
    return f"{extra_hits / protected_hits:.2f}"


def suppression_utility_text(extra_hits: int, protected_hits: int) -> str:
    return (
        f"net_hits={extra_hits - protected_hits} "
        f"gain_per_protected={gain_per_protected(extra_hits, protected_hits)}"
    )


def source_counts(records: list[dict[str, str]], limit: int = 5) -> str:
    counts = collections.Counter(record["source_key"] for record in records)
    if not counts:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counts.most_common(limit))


def parse_float_list(value: str) -> list[float]:
    out: list[float] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(float(part))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid float `{part}` in `{value}`") from exc
    if not out:
        raise argparse.ArgumentTypeError("expected at least one float")
    return out


def parse_optional_float_list(value: str) -> list[float | None]:
    out: list[float | None] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if part.lower() in {"none", "off", "-"}:
            out.append(None)
            continue
        try:
            out.append(float(part))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid float `{part}` in `{value}`") from exc
    if not out:
        raise argparse.ArgumentTypeError("expected at least one float or `none`")
    return out


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def best_same_midi_debug(rows: list[dict[str, str]], midi: int, target_row: str) -> dict[str, str] | None:
    score_field = ROW_SCORE_FIELDS[target_row]
    best: dict[str, str] | None = None
    best_score = -1.0
    for row in rows:
        debug_midi = as_int(row, "debug_midi")
        if debug_midi is None:
            debug_midi = midi_from_note(row.get("debug_note", ""))
        if debug_midi != midi:
            continue
        score = as_float(row, score_field) or 0.0
        confidence = as_float(row, "debug_conf") or 0.0
        combined = score + confidence * 0.01
        if combined > best_score:
            best = row
            best_score = combined
    return best


def build_record(
    context: dict[str, str],
    debug: dict[str, str] | None,
    target_row: str,
    shadow_row: str,
    midi: int,
) -> dict[str, str]:
    record = dict(context)
    record["target_row"] = target_row
    record["shadow_row"] = shadow_row
    record["target_level"] = f"{exact_level(context, target_row, midi):.6f}"
    record["shadow_level"] = f"{exact_level(context, shadow_row, midi):.6f}"
    expected_row = ROW_FOR_FAMILY.get(context.get("family", ""), context.get("family", ""))
    record["expected_row"] = expected_row
    record["protected"] = "1" if expected_row == target_row else "0"
    record["source_key"] = f"{context.get('family', 'unknown')}/{context.get('source', 'unknown')}"
    if debug:
        for field in (
            "debug_note",
            "debug_midi",
            "debug_owner",
            "debug_conf",
            "spectral_level",
            "pitch_confidence",
            "periodicity",
            "harmonicity",
            "fit_error",
            "centroid",
            "slope",
            "noise",
            "partial2",
            "partial3",
            "partial4",
            "partial5",
            "raw_expected_ratio",
            "raw_expected_rank",
        ):
            record[field] = debug.get(field, "")
        target_score_field = ROW_SCORE_FIELDS[target_row]
        shadow_score_field = ROW_SCORE_FIELDS[shadow_row]
        record["target_score"] = debug.get(target_score_field, "")
        record["shadow_score"] = debug.get(shadow_score_field, "")
    else:
        record["debug_note"] = ""
        record["debug_midi"] = ""
        record["debug_owner"] = ""
        record["target_score"] = ""
        record["shadow_score"] = ""
    return record


def owner_matches(row_name: str, owner: str) -> bool:
    aliases = ROW_OWNER_ALIASES.get(row_name, {row_name})
    return (owner or "").strip().lower() in aliases


def measured_other_owned_low_confidence_vocal_partial_supported(record: dict[str, str]) -> bool:
    return (
        owner_matches("other", record.get("debug_owner", ""))
        and (as_float(record, "pitch_confidence") or 0.0) <= 0.468
        and (as_float(record, "noise") or 0.0) <= 0.028
        and (as_float(record, "partial2") or 0.0) >= 0.884
    )


def measured_owned_formant_vocal_partial_supported(record: dict[str, str]) -> bool:
    midi = record_debug_midi(record)
    if midi is None or midi < 50 or midi > 84:
        return False

    owner = record.get("debug_owner", "")
    third = as_float(record, "partial3") or 0.0
    fourth = as_float(record, "partial4") or 0.0
    sparse_other_or_guitar_formant = (
        (owner_matches("other", owner) or owner_matches("guitar", owner))
        and (as_float(record, "adjacent_lower_ratio") or 0.0) <= 0.279
        and third >= 1.218
        and fourth <= 0.740
    )
    periodic_named_formant = (
        (
            owner_matches("other", owner)
            or owner_matches("guitar", owner)
            or owner.strip().lower() in {"amb", "ambiguous"}
        )
        and (as_float(record, "noise") or 0.0) <= 0.133
        and third >= 1.214
        and (as_float(record, "periodicity") or 0.0) >= 0.699
    )
    return sparse_other_or_guitar_formant or periodic_named_formant


def measured_keyboard_owned_vocal_body_supported(record: dict[str, str]) -> bool:
    if not owner_matches("piano", record.get("debug_owner", "")):
        return False
    midi = record_debug_midi(record)
    if midi is None or midi < 50 or midi > 84:
        return False

    keyboard_score = as_float(record, "shadow_score") or as_float(record, "keyboard_score") or 0.0
    guitar_score = as_float(record, "guitar_score") or 0.0
    vocal_score = as_float(record, "target_score") or as_float(record, "vocal_score") or 0.0
    other_score = as_float(record, "other_score") or 0.0
    second = as_float(record, "partial2") or 0.0
    third = as_float(record, "partial3") or 0.0
    fourth = as_float(record, "partial4") or 0.0
    fifth = as_float(record, "partial5") or 0.0
    rounded_mid_body = (
        keyboard_score >= 0.69
        and keyboard_score <= 0.86
        and guitar_score >= 0.14
        and guitar_score <= 0.32
        and vocal_score <= 0.020
        and other_score <= 0.020
        and (as_float(record, "spectral_level") or 0.0) >= 0.62
        and (as_float(record, "pitch_confidence") or 0.0) >= 0.60
        and (as_float(record, "periodicity") or 0.0) >= 0.78
        and (as_float(record, "fit_error") or 0.0) <= 0.12
        and (as_float(record, "centroid") or 0.0) >= 0.17
        and (as_float(record, "centroid") or 0.0) <= 0.36
        and (as_float(record, "slope") or 0.0) >= 0.21
        and (as_float(record, "slope") or 0.0) <= 0.62
        and second >= 0.13
        and second <= 0.40
        and third >= 0.12
        and third <= 0.42
        and fourth <= 0.32
        and fifth <= 0.18
    )
    octave_alias_body = (
        keyboard_score >= 0.78
        and guitar_score >= 0.15
        and guitar_score <= 0.23
        and vocal_score <= 0.020
        and other_score <= 0.020
        and (as_float(record, "spectral_level") or 0.0) >= 0.70
        and (as_float(record, "pitch_confidence") or 0.0) >= 0.66
        and (as_float(record, "periodicity") or 0.0) >= 0.81
        and (as_float(record, "fit_error") or 0.0) <= 0.10
        and (as_float(record, "slope") or 0.0) >= 0.24
        and (as_float(record, "slope") or 0.0) <= 0.38
        and second >= 0.13
        and second <= 0.22
        and third >= 0.12
        and third <= 0.31
        and fourth <= 0.30
        and fifth <= 0.08
    )
    return rounded_mid_body or octave_alias_body


def measured_other_owned_harmonic_vocal_body_supported(record: dict[str, str]) -> bool:
    if not owner_matches("other", record.get("debug_owner", "")):
        return False
    midi = record_debug_midi(record)
    if midi is None or midi < 50 or midi > 84:
        return False

    second = as_float(record, "partial2") or 0.0
    third = as_float(record, "partial3") or 0.0
    fourth = as_float(record, "partial4") or 0.0
    fifth = as_float(record, "partial5") or 0.0
    return (
        (as_float(record, "other_score") or 0.0) >= 0.82
        and (as_float(record, "keyboard_score") or 0.0) >= 0.035
        and (as_float(record, "keyboard_score") or 0.0) <= 0.12
        and (as_float(record, "guitar_score") or 0.0) <= 0.11
        and (as_float(record, "vocal_score") or 0.0) <= 0.020
        and (as_float(record, "spectral_level") or 0.0) >= 0.74
        and (as_float(record, "pitch_confidence") or 0.0) >= 0.50
        and (as_float(record, "periodicity") or 0.0) >= 0.56
        and (as_float(record, "harmonicity") or 0.0) >= 1.80
        and (as_float(record, "fit_error") or 0.0) <= 0.86
        and (as_float(record, "centroid") or 0.0) >= 0.49
        and (as_float(record, "centroid") or 0.0) <= 0.66
        and (as_float(record, "slope") or 0.0) >= 1.10
        and (as_float(record, "slope") or 0.0) <= 2.40
        and (as_float(record, "noise") or 0.0) <= 0.36
        and second >= 0.30
        and second <= 0.58
        and third >= 0.30
        and third <= 1.10
        and fourth >= 0.50
        and fourth <= 2.20
        and fifth >= 0.18
        and fifth <= 1.45
    )


def cxx_vocal_shadow_preserve_guard(record: dict[str, str]) -> bool:
    return (
        measured_owned_formant_vocal_partial_supported(record)
        or measured_other_owned_low_confidence_vocal_partial_supported(record)
        or measured_keyboard_owned_vocal_body_supported(record)
        or measured_other_owned_harmonic_vocal_body_supported(record)
    )


def shadow_rule_matches(record: dict[str, str], rule: str) -> bool:
    target_score = as_float(record, "target_score") or 0.0
    shadow_score = as_float(record, "shadow_score") or 0.0
    target_level = as_float(record, "target_level") or 0.0
    shadow_level = as_float(record, "shadow_level") or 0.0
    debug_owner = record.get("debug_owner", "")
    target_row = record.get("target_row", "")
    shadow_row = record.get("shadow_row", "")
    pitch_confidence = as_float(record, "pitch_confidence") or 0.0
    periodicity = as_float(record, "periodicity") or 0.0
    fit_error = as_float(record, "fit_error") or 0.0
    noise = as_float(record, "noise") or 0.0

    if shadow_level <= 1.0e-6:
        return False

    owner_is_shadow = owner_matches(shadow_row, debug_owner)
    target_is_weak = target_score <= 0.10 and target_level <= 0.45
    shadow_score_dominant = shadow_score >= 0.24 and target_score <= shadow_score * 0.50
    shadow_level_dominant = target_level <= shadow_level * 0.72
    shadow_score_clear = shadow_score >= 0.18 and target_score <= shadow_score * 0.67
    shadow_level_clear = target_level <= shadow_level * 0.90

    if rule == "owner_shadow_score2_level":
        return owner_is_shadow and shadow_score_dominant and shadow_level_clear
    if rule == "owner_shadow_score15_level":
        return owner_is_shadow and shadow_score_clear and shadow_level_clear
    if rule == "score2_level_no_owner":
        return shadow_score_dominant and shadow_level_dominant
    if rule == "runtime_keyboard_vocal_weak":
        return (
            target_row == "vocals"
            and shadow_row == "piano"
            and owner_is_shadow
            and target_is_weak
            and shadow_score >= 0.18
        )
    if rule == "weak_target_shadow_owned":
        return owner_is_shadow and target_is_weak and shadow_score >= 0.18
    if rule == "runtime_guitar_bass_measured":
        return (
            target_row == "bass"
            and shadow_row == "guitar"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.15
            and target_level <= shadow_level * 0.68
            and noise <= 0.60
        )
    if rule == "runtime_keyboard_bass_weak":
        return (
            target_row == "bass"
            and shadow_row == "piano"
            and owner_is_shadow
            and target_level <= 0.45
            and target_score <= 0.10
            and shadow_score >= 0.18
        )
    if rule == "runtime_keyboard_bass_dominant":
        return (
            target_row == "bass"
            and shadow_row == "piano"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.50
            and target_level <= shadow_level * 0.68
        )
    if rule == "runtime_keyboard_bass_guarded":
        return (
            target_row == "bass"
            and shadow_row == "piano"
            and owner_is_shadow
            and shadow_score >= 0.18
            and target_score <= shadow_score * 0.20
            and target_level <= shadow_level * 0.80
            and pitch_confidence >= 0.78
            and periodicity >= 0.70
            and fit_error <= 0.08
            and noise <= 0.45
        )
    if rule == "runtime_vocal_bass_owned":
        return (
            target_row == "bass"
            and shadow_row == "vocals"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.50
            and target_level <= shadow_level * 0.94
        )
    if rule == "runtime_other_bass_legacy":
        return (
            target_row == "bass"
            and shadow_row == "other"
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.50
            and target_level <= shadow_level * 0.80
        )
    if rule == "runtime_other_bass_measured":
        return (
            target_row == "bass"
            and shadow_row == "other"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.50
            and target_level <= shadow_level * 0.90
        )
    if rule == "runtime_other_bass_guarded":
        return (
            target_row == "bass"
            and shadow_row == "other"
            and shadow_score >= 0.18
            and target_score <= shadow_score * 0.20
            and target_level <= shadow_level * 0.80
            and pitch_confidence >= 0.78
            and periodicity >= 0.70
            and fit_error <= 0.08
            and noise <= 0.45
        )
    if rule == "runtime_other_vocal_measured":
        return (
            target_row == "vocals"
            and shadow_row == "other"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.15
            and target_level <= shadow_level * 0.48
        )
    if rule == "runtime_other_vocal_cpp_guarded":
        return shadow_rule_matches(record, "runtime_other_vocal_measured") and not cxx_vocal_shadow_preserve_guard(
            record
        )
    raise ValueError(f"unknown simulation rule `{rule}`")


def format_example_record(record: dict[str, str], prefix: str = "example") -> str:
    return (
        f"  {prefix} "
        f"{record.get('sample_id', '')}@{record.get('buffer', '')} "
        f"src={record.get('source_key', '')} expected={record.get('expected_note', '')}/"
        f"{record.get('expected_midi', '')} target={record.get('target_row', '')}:"
        f"{record.get('target_level', '')} shadow={record.get('shadow_row', '')}:"
        f"{record.get('shadow_level', '')} debug={record.get('debug_note', '')}/"
        f"{record.get('debug_owner', '')} target_score={record.get('target_score', '')} "
        f"shadow_score={record.get('shadow_score', '')}"
    )


def print_simulations(
    title: str,
    records: list[dict[str, str]],
    source_breakdown: bool,
    simulation_examples: int,
) -> None:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    print(f"\n{title} suppressor simulations")
    if not records:
        print("  no records")
        return

    for rule in SIMULATION_RULES:
        extra_hits = [record for record in extras if shadow_rule_matches(record, rule)]
        protected_hits = [record for record in protected if shadow_rule_matches(record, rule)]
        total_hits = len(extra_hits) + len(protected_hits)
        print(
            f"  {rule:28s} extras={len(extra_hits)}/{len(extras)} "
            f"protected={len(protected_hits)}/{len(protected)} "
            f"precision={pct(len(extra_hits), total_hits)} "
            f"protected_rate={pct(len(protected_hits), len(protected))} "
            f"{suppression_utility_text(len(extra_hits), len(protected_hits))}"
        )
        if source_breakdown and total_hits > 0:
            print(f"    extras_sources {source_counts(extra_hits)}")
            print(f"    protected_sources {source_counts(protected_hits)}")
        if simulation_examples > 0:
            for record in extra_hits[:simulation_examples]:
                print(format_example_record(record, "extra"))
            for record in protected_hits[:simulation_examples]:
                print(format_example_record(record, "protected"))


def best_safe_simulation(records: list[dict[str, str]]) -> tuple[str, int, int] | None:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    best: tuple[str, int, int] | None = None
    for rule in SIMULATION_RULES:
        extra_hits = sum(1 for record in extras if shadow_rule_matches(record, rule))
        protected_hits = sum(1 for record in protected if shadow_rule_matches(record, rule))
        if extra_hits <= 0 or protected_hits > 0:
            continue
        if best is None or extra_hits > best[1]:
            best = (rule, extra_hits, protected_hits)
    return best


def simulation_result(records: list[dict[str, str]], rule: str) -> tuple[str, int, int]:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    extra_hits = sum(1 for record in extras if shadow_rule_matches(record, rule))
    protected_hits = sum(1 for record in protected if shadow_rule_matches(record, rule))
    return (rule, extra_hits, protected_hits)


def threshold_rule_matches(
    record: dict[str, str],
    min_shadow_score: float,
    score_ratio: float,
    level_ratio: float,
    target_level_ceiling: float | None,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> bool:
    target_score = as_float(record, "target_score") or 0.0
    shadow_score = as_float(record, "shadow_score") or 0.0
    target_level = as_float(record, "target_level") or 0.0
    shadow_level = as_float(record, "shadow_level") or 0.0
    pitch_confidence = as_float(record, "pitch_confidence")
    periodicity = as_float(record, "periodicity")
    fit_error = as_float(record, "fit_error")
    noise = as_float(record, "noise")
    debug_owner = record.get("debug_owner", "")
    target_row = record.get("target_row", "")
    shadow_row = record.get("shadow_row", "")
    if owner_mode == "shadow" and not owner_matches(shadow_row, debug_owner):
        return False
    if owner_mode == "target" and not owner_matches(target_row, debug_owner):
        return False
    if owner_mode == "not-target" and owner_matches(target_row, debug_owner):
        return False
    if min_pitch_confidence is not None and (
        pitch_confidence is None or pitch_confidence < min_pitch_confidence
    ):
        return False
    if min_periodicity is not None and (periodicity is None or periodicity < min_periodicity):
        return False
    if max_fit_error is not None and (fit_error is None or fit_error > max_fit_error):
        return False
    if max_noise is not None and (noise is None or noise > max_noise):
        return False
    return (
        shadow_level > 1.0e-6
        and shadow_score >= min_shadow_score
        and target_score <= shadow_score * score_ratio
        and target_level <= shadow_level * level_ratio
        and (target_level_ceiling is None or target_level <= target_level_ceiling)
    )


def threshold_search_matches(
    records: list[dict[str, str]],
    shadow_score_thresholds: list[float],
    score_ratios: list[float],
    level_ratios: list[float],
    target_level_thresholds: list[float | None],
    max_protected: int,
    min_extra_hits: int,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> list[ThresholdMatch]:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    matches: list[ThresholdMatch] = []
    for min_shadow_score in shadow_score_thresholds:
        for score_ratio in score_ratios:
            for level_ratio in level_ratios:
                for target_level_ceiling in target_level_thresholds:
                    extra_hits = sum(
                        1
                        for record in extras
                        if threshold_rule_matches(
                            record,
                            min_shadow_score,
                            score_ratio,
                            level_ratio,
                            target_level_ceiling,
                            min_pitch_confidence,
                            min_periodicity,
                            max_fit_error,
                            max_noise,
                            owner_mode,
                        )
                    )
                    protected_hits = sum(
                        1
                        for record in protected
                        if threshold_rule_matches(
                            record,
                            min_shadow_score,
                            score_ratio,
                            level_ratio,
                            target_level_ceiling,
                            min_pitch_confidence,
                            min_periodicity,
                            max_fit_error,
                            max_noise,
                            owner_mode,
                        )
                    )
                    if extra_hits >= min_extra_hits and protected_hits <= max_protected:
                        matches.append(
                            (
                                protected_hits,
                                extra_hits,
                                min_shadow_score,
                                score_ratio,
                                level_ratio,
                                target_level_ceiling,
                        )
                    )

    matches.sort(
        key=lambda item: (
            item[0],
            -item[1],
            item[2],
            item[3],
            item[4],
            9.0 if item[5] is None else item[5],
        )
    )
    return matches


def threshold_match_text(
    match: ThresholdMatch,
    extras_total: int,
    protected_total: int,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> str:
    protected_hits, extra_hits, min_shadow_score, score_ratio, level_ratio, target_level_ceiling = match
    line = (
        f"protected={protected_hits}/{protected_total} extras={extra_hits}/{extras_total} "
        f"min_shadow_score={min_shadow_score:.2f} score_ratio={score_ratio:.2f} "
        f"level_ratio={level_ratio:.2f}"
    )
    if target_level_ceiling is not None:
        line += f" target_level_max={target_level_ceiling:.2f}"
    if min_pitch_confidence is not None:
        line += f" min_pitch_confidence={min_pitch_confidence:.2f}"
    if min_periodicity is not None:
        line += f" min_periodicity={min_periodicity:.2f}"
    if max_fit_error is not None:
        line += f" max_fit_error={max_fit_error:.2f}"
    if max_noise is not None:
        line += f" max_noise={max_noise:.2f}"
    if owner_mode != "any":
        line += f" owner_mode={owner_mode}"
    line += f" {suppression_utility_text(extra_hits, protected_hits)}"
    return line


def print_threshold_search(
    title: str,
    records: list[dict[str, str]],
    matches: list[ThresholdMatch],
    max_protected: int,
    min_extra_hits: int,
    limit: int,
    examples: int,
    protected_examples: int,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> None:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    print(f"\n{title} threshold search max_protected={max_protected} min_extra_hits={min_extra_hits}")
    if not matches:
        print("  no matching thresholds")
        return
    for (
        protected_hits,
        extra_hits,
        min_shadow_score,
        score_ratio,
        level_ratio,
        target_level_ceiling,
    ) in matches[: max(0, limit)]:
        match = (protected_hits, extra_hits, min_shadow_score, score_ratio, level_ratio, target_level_ceiling)
        print(
            "  "
            + threshold_match_text(
                match,
                len(extras),
                len(protected),
                min_pitch_confidence,
                min_periodicity,
                max_fit_error,
                max_noise,
                owner_mode,
            )
        )
        if examples > 0:
            matching_extras = [
                record
                for record in extras
                if threshold_rule_matches(
                    record,
                    min_shadow_score,
                    score_ratio,
                    level_ratio,
                    target_level_ceiling,
                    min_pitch_confidence,
                    min_periodicity,
                    max_fit_error,
                    max_noise,
                    owner_mode,
                )
            ]
            for record in matching_extras[:examples]:
                print(
                    "    extra "
                    f"{record.get('sample_id', '')}@{record.get('buffer', '')} "
                    f"src={record.get('source_key', '')} expected={record.get('expected_note', '')}/"
                    f"{record.get('expected_midi', '')} target={record.get('target_row', '')}:"
                    f"{record.get('target_level', '')} shadow={record.get('shadow_row', '')}:"
                    f"{record.get('shadow_level', '')} debug={record.get('debug_note', '')}/"
                    f"{record.get('debug_owner', '')} target_score={record.get('target_score', '')} "
                    f"shadow_score={record.get('shadow_score', '')}"
                )
        if protected_examples <= 0:
            continue
        matching_protected = [
            record
            for record in protected
            if threshold_rule_matches(
                record,
                min_shadow_score,
                score_ratio,
                level_ratio,
                target_level_ceiling,
                min_pitch_confidence,
                min_periodicity,
                max_fit_error,
                max_noise,
                owner_mode,
            )
        ]
        for record in matching_protected[:protected_examples]:
            print(
                "    protected "
                f"{record.get('sample_id', '')}@{record.get('buffer', '')} "
                f"src={record.get('source_key', '')} expected={record.get('expected_note', '')}/"
                f"{record.get('expected_midi', '')} target={record.get('target_row', '')}:"
                f"{record.get('target_level', '')} shadow={record.get('shadow_row', '')}:"
                f"{record.get('shadow_level', '')} debug={record.get('debug_note', '')}/"
                f"{record.get('debug_owner', '')} target_score={record.get('target_score', '')} "
                f"shadow_score={record.get('shadow_score', '')}"
                )


def print_ranked_threshold_summary(
    opportunities: list[tuple[str, int, int, ThresholdMatch]],
    limit: int,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> None:
    print("\nranked threshold-search opportunities")
    if not opportunities:
        print("  no matching thresholds")
        return

    best_by_route: dict[str, tuple[str, int, int, ThresholdMatch]] = {}
    for opportunity in opportunities:
        route = opportunity[0]
        current = best_by_route.get(route)
        if current is None:
            best_by_route[route] = opportunity
            continue
        _route, extras_total, protected_total, match = opportunity
        _cur_route, cur_extras_total, cur_protected_total, cur_match = current
        key = (
            match[0],
            -match[1],
            -(match[1] / max(1, extras_total)),
            match[2],
            match[3],
            match[4],
            9.0 if match[5] is None else match[5],
        )
        current_key = (
            cur_match[0],
            -cur_match[1],
            -(cur_match[1] / max(1, cur_extras_total)),
            cur_match[2],
            cur_match[3],
            cur_match[4],
            9.0 if cur_match[5] is None else cur_match[5],
        )
        if key < current_key:
            best_by_route[route] = opportunity

    ranked = sorted(
        best_by_route.values(),
        key=lambda item: (
            item[3][0],
            -item[3][1],
            -(item[3][1] / max(1, item[1])),
            item[3][2],
            item[3][3],
            item[3][4],
            9.0 if item[3][5] is None else item[3][5],
        ),
    )
    for route, extras_total, protected_total, match in ranked[: max(0, limit)]:
        print(
            f"  {route} "
            + threshold_match_text(
                match,
                extras_total,
                protected_total,
                min_pitch_confidence,
                min_periodicity,
                max_fit_error,
                max_noise,
                owner_mode,
            )
        )


def print_compact_route_summary(
    route_summaries: list[dict[str, object]],
    threshold_search: bool,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> None:
    print("\ncompact route summary")
    if not route_summaries:
        print("  no routes")
        return

    routes_with_extras = sum(1 for summary in route_summaries if int(summary["extras_total"]) > 0)
    safe_simulation_routes = sum(1 for summary in route_summaries if summary["safe_simulation"] is not None)
    safe_threshold_routes = sum(1 for summary in route_summaries if summary["best_threshold"] is not None)
    safe_simulation_extra_hits = sum(
        int(summary["safe_simulation"][1])
        for summary in route_summaries
        if summary["safe_simulation"] is not None
    )
    safe_threshold_extra_hits = sum(
        int(summary["best_threshold"][1])
        for summary in route_summaries
        if summary["best_threshold"] is not None
    )
    safe_threshold_protected_hits = sum(
        int(summary["best_threshold"][0])
        for summary in route_summaries
        if summary["best_threshold"] is not None
    )
    searched_routes = sum(1 for summary in route_summaries if bool(summary["threshold_searched"]))
    no_safe_threshold_routes = searched_routes - safe_threshold_routes
    print(
        f"  routes={len(route_summaries)} routes_with_extras={routes_with_extras} "
        f"safe_simulation_routes={safe_simulation_routes} "
        f"safe_simulation_extra_hits={safe_simulation_extra_hits}"
    )
    if threshold_search:
        print(
            f"  safe_threshold_routes={safe_threshold_routes} "
            f"no_safe_threshold_routes={no_safe_threshold_routes} "
            f"safe_threshold_extra_hits={safe_threshold_extra_hits} "
            f"safe_threshold_protected_hits={safe_threshold_protected_hits}"
        )

    ranked = sorted(
        route_summaries,
        key=lambda summary: (
            0 if summary["best_threshold"] is not None else 1,
            -int(summary["best_threshold"][1]) if summary["best_threshold"] is not None else 0,
            0 if summary["safe_simulation"] is not None else 1,
            -int(summary["extras_total"]),
            str(summary["route"]),
        ),
    )
    for summary in ranked:
        route = str(summary["route"])
        extras_total = int(summary["extras_total"])
        extras_samples = int(summary["extras_samples"])
        protected_total = int(summary["protected_total"])
        protected_samples = int(summary["protected_samples"])
        line = (
            f"  {route} extras={extras_total}/{extras_samples} "
            f"protected={protected_total}/{protected_samples}"
        )
        safe_simulation = summary["safe_simulation"]
        if safe_simulation is not None:
            rule, extra_hits, protected_hits = safe_simulation
            line += f" simulation={rule}:{extra_hits}/{protected_hits}"
        else:
            line += " simulation=none"
        best_threshold = summary["best_threshold"]
        if threshold_search:
            if best_threshold is None:
                line += " threshold=none"
            else:
                line += " threshold="
                line += threshold_match_text(
                    best_threshold,
                    extras_total,
                    protected_total,
                    min_pitch_confidence,
                    min_periodicity,
                    max_fit_error,
                    max_noise,
                    owner_mode,
                )
        if safe_simulation is not None:
            _rule, extra_hits, protected_hits = safe_simulation
            extra_hits = int(extra_hits)
            protected_hits = int(protected_hits)
            line += (
                f" simulation_net_hits={extra_hits - protected_hits} "
                f"simulation_gain_per_protected={gain_per_protected(extra_hits, protected_hits)}"
            )
        guarded_simulation = summary["guarded_simulation"]
        if guarded_simulation is not None:
            rule, extra_hits, protected_hits = guarded_simulation
            line += f" guarded={rule}:{extra_hits}/{protected_hits}"
        print(line)


def compact_route_summary(payload: tuple[object, ...]) -> dict[str, object]:
    (
        route,
        records,
        threshold_search,
        shadow_score_thresholds,
        score_ratios,
        level_ratios,
        target_level_thresholds,
        max_protected,
        min_threshold_extra_hits,
        min_pitch_confidence,
        min_periodicity,
        max_fit_error,
        max_noise,
        owner_mode,
    ) = payload
    route_text = str(route)
    route_records = list(records)
    extras = [record for record in route_records if record["protected"] == "0"]
    protected = [record for record in route_records if record["protected"] == "1"]
    matches: list[ThresholdMatch] = []
    if bool(threshold_search):
        matches = threshold_search_matches(
            route_records,
            list(shadow_score_thresholds),
            list(score_ratios),
            list(level_ratios),
            list(target_level_thresholds),
            int(max_protected),
            int(min_threshold_extra_hits),
            min_pitch_confidence,
            min_periodicity,
            max_fit_error,
            max_noise,
            str(owner_mode),
        )
    return {
        "route": route_text,
        "extras_total": len(extras),
        "extras_samples": len({record.get("sample_id", "") for record in extras}),
        "protected_total": len(protected),
        "protected_samples": len({record.get("sample_id", "") for record in protected}),
        "safe_simulation": best_safe_simulation(route_records),
        "guarded_simulation": (
            simulation_result(route_records, "runtime_other_vocal_cpp_guarded")
            if route_text == "other->same-pitch vocals"
            else None
        ),
        "best_threshold": matches[0] if matches else None,
        "threshold_searched": bool(threshold_search),
    }


def print_group(title: str, records: list[dict[str, str]], examples: int) -> None:
    print(f"\n{title} rows={len(records)} samples={len({r.get('sample_id', '') for r in records})}")
    if not records:
        return
    by_source = collections.Counter(r["source_key"] for r in records)
    by_owner = collections.Counter(r.get("debug_owner", "") or "--" for r in records)
    print("  sources " + " ".join(f"{key}={value}" for key, value in by_source.most_common(8)))
    print("  debug_owner " + " ".join(f"{key}={value}" for key, value in by_owner.most_common(8)))
    for field in NUMERIC_FIELDS:
        values = [value for r in records if (value := as_float(r, field)) is not None]
        if values:
            print(f"  {field:18s} {med(values)}")
    for record in records[:examples]:
        print(format_example_record(record))


def print_group_summary(title: str, records: list[dict[str, str]]) -> None:
    print(f"\n{title} rows={len(records)} samples={len({r.get('sample_id', '') for r in records})}")
    if not records:
        return
    by_source = collections.Counter(r["source_key"] for r in records)
    by_owner = collections.Counter(r.get("debug_owner", "") or "--" for r in records)
    print("  sources " + " ".join(f"{key}={value}" for key, value in by_source.most_common(5)))
    print("  debug_owner " + " ".join(f"{key}={value}" for key, value in by_owner.most_common(5)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument("--target-row", action="append", default=[])
    parser.add_argument("--shadow-row", default="piano")
    parser.add_argument("--min-target-level", type=float, default=0.01)
    parser.add_argument("--min-shadow-level", type=float, default=0.01)
    parser.add_argument("--examples", "--show-examples", dest="examples", type=int, default=8)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print counts and simulations without per-field ranges or example rows",
    )
    parser.add_argument(
        "--compact-routes",
        action="store_true",
        help="print one ranked summary line per display-row route instead of per-route blocks",
    )
    parser.add_argument(
        "--source-breakdown",
        action="store_true",
        help="include per-source hit counts for each simulated suppression rule",
    )
    parser.add_argument(
        "--simulation-examples",
        type=int,
        default=0,
        help="print this many matching extra/protected rows under each simulated suppression rule",
    )
    parser.add_argument(
        "--threshold-search",
        action="store_true",
        help="search score/level threshold triples for low-risk shadow suppression",
    )
    parser.add_argument("--max-protected", type=int, default=2)
    parser.add_argument(
        "--min-threshold-extra-hits",
        type=int,
        default=1,
        help="minimum extra rows a threshold-search result must suppress before it is reported",
    )
    parser.add_argument("--threshold-limit", "--top-routes", dest="threshold_limit", type=int, default=12)
    parser.add_argument(
        "--threshold-examples",
        type=int,
        default=0,
        help="print this many matching extra rows under each threshold-search result",
    )
    parser.add_argument(
        "--threshold-protected-examples",
        type=int,
        default=0,
        help="print this many matching protected rows under each threshold-search result",
    )
    parser.add_argument(
        "--shadow-score-thresholds",
        type=parse_float_list,
        default=parse_float_list("0.24,0.28,0.30,0.32,0.36,0.40,0.45,0.50,0.55,0.60,0.70"),
    )
    parser.add_argument(
        "--score-ratios",
        type=parse_float_list,
        default=parse_float_list("0.50,0.45,0.40,0.35,0.30,0.25,0.20,0.15"),
    )
    parser.add_argument(
        "--level-ratios",
        type=parse_float_list,
        default=parse_float_list("0.72,0.68,0.64,0.60,0.56,0.52,0.48,0.44,0.40,0.35,0.30"),
    )
    parser.add_argument(
        "--target-level-thresholds",
        type=parse_optional_float_list,
        default=parse_optional_float_list("none"),
        help="optional absolute target-level ceilings to include in threshold search",
    )
    parser.add_argument(
        "--min-pitch-confidence",
        type=float,
        default=None,
        help="optional minimum pitch confidence required for threshold-search matches",
    )
    parser.add_argument(
        "--min-periodicity",
        type=float,
        default=None,
        help="optional minimum periodicity required for threshold-search matches",
    )
    parser.add_argument(
        "--max-fit-error",
        type=float,
        default=None,
        help="optional maximum harmonic fit error required for threshold-search matches",
    )
    parser.add_argument(
        "--max-noise",
        type=float,
        default=None,
        help="optional maximum local noise required for threshold-search matches",
    )
    parser.add_argument(
        "--threshold-owner-mode",
        choices=["any", "shadow", "target", "not-target"],
        default="any",
        help="optional debug-owner requirement for threshold-search matches",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="parallel route workers for --compact-routes output",
    )
    args = parser.parse_args()

    rows = load_rows(pathlib.Path(args.path))
    grouped: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        grouped[(row.get("sample_id", ""), row.get("buffer", ""))].append(row)

    target_rows = list(ROW_NAMES) if "all" in args.target_row else (args.target_row or ["bass", "guitar", "other"])
    shadow_rows = list(ROW_NAMES) if args.shadow_row == "all" else [args.shadow_row]
    for target_row in target_rows:
        if target_row not in ROW_NOTE_FIELDS:
            raise SystemExit(f"unknown target row `{target_row}`")
    for shadow_row in shadow_rows:
        if shadow_row not in ROW_NOTE_FIELDS:
            raise SystemExit(f"unknown shadow row `{shadow_row}`")

    threshold_opportunities: list[tuple[str, int, int, ThresholdMatch]] = []
    threshold_route_count = 0
    route_summaries: list[dict[str, object]] = []
    compact_route_tasks: list[tuple[object, ...]] = []
    for shadow_row in shadow_rows:
        records_by_target: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
        for (_sample_id, _buffer), group_rows in grouped.items():
            context = group_rows[0]
            midi = as_int(context, "expected_midi")
            if midi is None:
                continue
            shadow_level = exact_level(context, shadow_row, midi)
            if shadow_level < args.min_shadow_level:
                continue
            for target_row in target_rows:
                if target_row == shadow_row:
                    continue
                target_level = exact_level(context, target_row, midi)
                if target_level < args.min_target_level:
                    continue
                debug = best_same_midi_debug(group_rows, midi, shadow_row)
                records_by_target[target_row].append(
                    build_record(context, debug, target_row, shadow_row, midi)
                )

        for target_row in target_rows:
            if target_row == shadow_row:
                continue
            records = records_by_target[target_row]
            extras = [record for record in records if record["protected"] == "0"]
            protected = [record for record in records if record["protected"] == "1"]
            route = f"{shadow_row}->same-pitch {target_row}"
            if args.compact_routes:
                compact_route_tasks.append(
                    (
                        route,
                        records,
                        args.threshold_search,
                        args.shadow_score_thresholds,
                        args.score_ratios,
                        args.level_ratios,
                        args.target_level_thresholds,
                        args.max_protected,
                        args.min_threshold_extra_hits,
                        args.min_pitch_confidence,
                        args.min_periodicity,
                        args.max_fit_error,
                        args.max_noise,
                        args.threshold_owner_mode,
                    )
                )
                continue
            if not args.compact_routes:
                if args.summary_only:
                    print_group_summary(f"{route} extras", extras)
                    print_group_summary(f"{route} protected", protected)
                else:
                    print_group(f"{route} extras", extras, args.examples)
                    print_group(f"{route} protected", protected, args.examples)
                print_simulations(route, records, args.source_breakdown, args.simulation_examples)
            matches: list[ThresholdMatch] = []
            if args.threshold_search:
                threshold_route_count += 1
                matches = threshold_search_matches(
                    records,
                    args.shadow_score_thresholds,
                    args.score_ratios,
                    args.level_ratios,
                    args.target_level_thresholds,
                    args.max_protected,
                    args.min_threshold_extra_hits,
                    args.min_pitch_confidence,
                    args.min_periodicity,
                    args.max_fit_error,
                    args.max_noise,
                    args.threshold_owner_mode,
                )
                extras_total = sum(1 for record in records if record["protected"] == "0")
                protected_total = sum(1 for record in records if record["protected"] == "1")
                threshold_opportunities.extend(
                    (route, extras_total, protected_total, match) for match in matches
                )
                if not args.compact_routes:
                    print_threshold_search(
                        route,
                        records,
                        matches,
                        args.max_protected,
                        args.min_threshold_extra_hits,
                        args.threshold_limit,
                        args.threshold_examples,
                        args.threshold_protected_examples,
                        args.min_pitch_confidence,
                        args.min_periodicity,
                        args.max_fit_error,
                        args.max_noise,
                        args.threshold_owner_mode,
                    )
    if args.compact_routes:
        if args.jobs > 1 and len(compact_route_tasks) > 1:
            with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as executor:
                route_summaries = list(executor.map(compact_route_summary, compact_route_tasks))
        else:
            route_summaries = [compact_route_summary(task) for task in compact_route_tasks]
        print_compact_route_summary(
            route_summaries,
            args.threshold_search,
            args.min_pitch_confidence,
            args.min_periodicity,
            args.max_fit_error,
            args.max_noise,
            args.threshold_owner_mode,
        )
    if args.threshold_search and threshold_route_count > 1 and not args.compact_routes:
        print_ranked_threshold_summary(
            threshold_opportunities,
            args.threshold_limit,
            args.min_pitch_confidence,
            args.min_periodicity,
            args.max_fit_error,
            args.max_noise,
            args.threshold_owner_mode,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
