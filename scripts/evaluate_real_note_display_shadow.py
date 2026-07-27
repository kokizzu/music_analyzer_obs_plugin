#!/usr/bin/env python3
"""Evaluate same-pitch display-row shadow opportunities in real-note TSVs."""

from __future__ import annotations

import argparse
import collections
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
    field = ROW_NOTE_FIELDS[row_name]
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


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def best_same_midi_debug(rows: list[dict[str, str]], midi: int, target_row: str) -> dict[str, str] | None:
    score_field = ROW_SCORE_FIELDS[target_row]
    best: dict[str, str] | None = None
    best_score = -1.0
    for row in rows:
        if as_int(row, "debug_midi") != midi:
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
        record["debug_owner"] = ""
        record["target_score"] = ""
        record["shadow_score"] = ""
    return record


def owner_matches(row_name: str, owner: str) -> bool:
    aliases = ROW_OWNER_ALIASES.get(row_name, {row_name})
    return (owner or "").strip().lower() in aliases


def shadow_rule_matches(record: dict[str, str], rule: str) -> bool:
    target_score = as_float(record, "target_score") or 0.0
    shadow_score = as_float(record, "shadow_score") or 0.0
    target_level = as_float(record, "target_level") or 0.0
    shadow_level = as_float(record, "shadow_level") or 0.0
    debug_owner = record.get("debug_owner", "")
    shadow_row = record.get("shadow_row", "")

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
    if rule == "weak_target_shadow_owned":
        return owner_is_shadow and target_is_weak and shadow_score >= 0.18
    raise ValueError(f"unknown simulation rule `{rule}`")


def print_simulations(title: str, records: list[dict[str, str]]) -> None:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    print(f"\n{title} suppressor simulations")
    if not records:
        print("  no records")
        return

    for rule in (
        "owner_shadow_score2_level",
        "owner_shadow_score15_level",
        "score2_level_no_owner",
        "weak_target_shadow_owned",
    ):
        extra_hits = [record for record in extras if shadow_rule_matches(record, rule)]
        protected_hits = [record for record in protected if shadow_rule_matches(record, rule)]
        total_hits = len(extra_hits) + len(protected_hits)
        print(
            f"  {rule:28s} extras={len(extra_hits)}/{len(extras)} "
            f"protected={len(protected_hits)}/{len(protected)} "
            f"precision={pct(len(extra_hits), total_hits)} protected_rate={pct(len(protected_hits), len(protected))}"
        )


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
        print(
            "  example "
            f"{record.get('sample_id', '')}@{record.get('buffer', '')} "
            f"src={record.get('source_key', '')} expected={record.get('expected_note', '')}/"
            f"{record.get('expected_midi', '')} target={record.get('target_row', '')}:"
            f"{record.get('target_level', '')} shadow={record.get('shadow_row', '')}:"
            f"{record.get('shadow_level', '')} debug={record.get('debug_note', '')}/"
            f"{record.get('debug_owner', '')} target_score={record.get('target_score', '')} "
            f"shadow_score={record.get('shadow_score', '')}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="build/real_note_full_mix_attributes.tsv")
    parser.add_argument("--target-row", action="append", default=[])
    parser.add_argument("--shadow-row", default="piano")
    parser.add_argument("--min-target-level", type=float, default=0.01)
    parser.add_argument("--min-shadow-level", type=float, default=0.01)
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    rows = load_rows(pathlib.Path(args.path))
    grouped: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        grouped[(row.get("sample_id", ""), row.get("buffer", ""))].append(row)

    target_rows = args.target_row or ["bass", "guitar", "other"]
    records_by_target: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for (_sample_id, _buffer), group_rows in grouped.items():
        context = group_rows[0]
        midi = as_int(context, "expected_midi")
        if midi is None:
            continue
        if args.shadow_row not in ROW_NOTE_FIELDS:
            raise SystemExit(f"unknown shadow row `{args.shadow_row}`")
        shadow_level = exact_level(context, args.shadow_row, midi)
        if shadow_level < args.min_shadow_level:
            continue
        for target_row in target_rows:
            if target_row == args.shadow_row:
                continue
            if target_row not in ROW_NOTE_FIELDS:
                raise SystemExit(f"unknown target row `{target_row}`")
            target_level = exact_level(context, target_row, midi)
            if target_level < args.min_target_level:
                continue
            debug = best_same_midi_debug(group_rows, midi, target_row)
            records_by_target[target_row].append(
                build_record(context, debug, target_row, args.shadow_row, midi)
            )

    for target_row in target_rows:
        records = records_by_target[target_row]
        extras = [record for record in records if record["protected"] == "0"]
        protected = [record for record in records if record["protected"] == "1"]
        print_group(f"{args.shadow_row}->same-pitch {target_row} extras", extras, args.examples)
        print_group(f"{args.shadow_row}->same-pitch {target_row} protected", protected, args.examples)
        print_simulations(f"{args.shadow_row}->same-pitch {target_row}", records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
