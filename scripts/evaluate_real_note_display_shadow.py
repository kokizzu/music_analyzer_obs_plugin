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
    if rule == "weak_target_shadow_owned":
        return owner_is_shadow and target_is_weak and shadow_score >= 0.18
    if rule == "runtime_guitar_bass_guarded":
        return (
            target_row == "bass"
            and shadow_row == "guitar"
            and shadow_score >= 0.18
            and target_score <= shadow_score * 0.20
            and target_level <= shadow_level * 0.80
            and pitch_confidence >= 0.78
            and periodicity >= 0.70
            and fit_error <= 0.08
            and noise <= 0.45
        )
    if rule == "runtime_guitar_bass_measured":
        return (
            target_row == "bass"
            and shadow_row == "guitar"
            and owner_is_shadow
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.15
            and target_level <= shadow_level * 0.72
            and periodicity >= 0.66
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
    if rule == "runtime_other_bass_legacy":
        return (
            target_row == "bass"
            and shadow_row == "other"
            and shadow_score >= 0.24
            and target_score <= shadow_score * 0.50
            and target_level <= shadow_level * 0.66
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
    raise ValueError(f"unknown simulation rule `{rule}`")


def print_simulations(title: str, records: list[dict[str, str]], source_breakdown: bool) -> None:
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
        "runtime_guitar_bass_guarded",
        "runtime_guitar_bass_measured",
        "runtime_keyboard_bass_weak",
        "runtime_keyboard_bass_dominant",
        "runtime_keyboard_bass_guarded",
        "runtime_other_bass_legacy",
        "runtime_other_bass_guarded",
    ):
        extra_hits = [record for record in extras if shadow_rule_matches(record, rule)]
        protected_hits = [record for record in protected if shadow_rule_matches(record, rule)]
        total_hits = len(extra_hits) + len(protected_hits)
        print(
            f"  {rule:28s} extras={len(extra_hits)}/{len(extras)} "
            f"protected={len(protected_hits)}/{len(protected)} "
            f"precision={pct(len(extra_hits), total_hits)} protected_rate={pct(len(protected_hits), len(protected))}"
        )
        if source_breakdown and total_hits > 0:
            print(f"    extras_sources {source_counts(extra_hits)}")
            print(f"    protected_sources {source_counts(protected_hits)}")


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


def print_threshold_search(
    title: str,
    records: list[dict[str, str]],
    shadow_score_thresholds: list[float],
    score_ratios: list[float],
    level_ratios: list[float],
    target_level_thresholds: list[float | None],
    max_protected: int,
    limit: int,
    examples: int,
    min_pitch_confidence: float | None,
    min_periodicity: float | None,
    max_fit_error: float | None,
    max_noise: float | None,
    owner_mode: str,
) -> None:
    extras = [record for record in records if record["protected"] == "0"]
    protected = [record for record in records if record["protected"] == "1"]
    matches: list[tuple[int, int, float, float, float, float | None]] = []
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
                    if extra_hits > 0 and protected_hits <= max_protected:
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

    print(f"\n{title} threshold search max_protected={max_protected}")
    if not matches:
        print("  no matching thresholds")
        return
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
    for (
        protected_hits,
        extra_hits,
        min_shadow_score,
        score_ratio,
        level_ratio,
        target_level_ceiling,
    ) in matches[: max(0, limit)]:
        line = (
            f"  protected={protected_hits}/{len(protected)} extras={extra_hits}/{len(extras)} "
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
        print(line)
        if examples <= 0:
            continue
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
    parser.add_argument("--examples", type=int, default=8)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print counts and simulations without per-field ranges or example rows",
    )
    parser.add_argument(
        "--source-breakdown",
        action="store_true",
        help="include per-source hit counts for each simulated suppression rule",
    )
    parser.add_argument(
        "--threshold-search",
        action="store_true",
        help="search score/level threshold triples for low-risk shadow suppression",
    )
    parser.add_argument("--max-protected", type=int, default=2)
    parser.add_argument("--threshold-limit", type=int, default=12)
    parser.add_argument(
        "--threshold-examples",
        type=int,
        default=0,
        help="print this many matching extra rows under each threshold-search result",
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
            if args.summary_only:
                print_group_summary(f"{shadow_row}->same-pitch {target_row} extras", extras)
                print_group_summary(f"{shadow_row}->same-pitch {target_row} protected", protected)
            else:
                print_group(f"{shadow_row}->same-pitch {target_row} extras", extras, args.examples)
                print_group(f"{shadow_row}->same-pitch {target_row} protected", protected, args.examples)
            print_simulations(f"{shadow_row}->same-pitch {target_row}", records, args.source_breakdown)
            if args.threshold_search:
                print_threshold_search(
                    f"{shadow_row}->same-pitch {target_row}",
                    records,
                    args.shadow_score_thresholds,
                    args.score_ratios,
                    args.level_ratios,
                    args.target_level_thresholds,
                    args.max_protected,
                    args.threshold_limit,
                    args.threshold_examples,
                    args.min_pitch_confidence,
                    args.min_periodicity,
                    args.max_fit_error,
                    args.max_noise,
                    args.threshold_owner_mode,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
