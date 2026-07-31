#!/usr/bin/env python3
"""Measure octave/harmonic display aliases in real-note full-mix TSV rows."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import pathlib
import re
import sys


NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")
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

ROW_NOTE_FIELDS = {
    "bass": ("bass_visual_notes", "bass_notes"),
    "guitar": ("guitar_visual_notes", "guitar_notes"),
    "piano": ("piano_visual_notes", "piano_notes"),
    "vocals": ("vocal_visual_notes", "vocal_notes"),
    "other": ("other_visual_notes", "other_notes"),
    "amb": ("amb_visual_notes", "amb_notes"),
}

EXPECTED_ROW = {
    "bass": "bass",
    "guitar": "guitar",
    "piano": "piano",
    "vocals": "vocals",
    "other": "other",
    "strings": "other",
    "synth": "other",
}

HARMONIC_INTERVALS = (12, 19, 24, 28, 31, 36, 40, 43, 47, 48, 49, 51, 52, 55, 57, 58, 60)
DEFAULT_DETAIL_FIELDS = (
    "raw_expected_ratio",
    "raw_tuned_abs_cent_offset",
    "pitch_confidence",
    "harmonicity",
    "fit_error",
    "spectral_level",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
)
DEFAULT_PROFILE_FIELDS = (
    "route",
    "expected_route",
    "interval",
    "shadow_level:0.05",
    "support_level:0.05",
    "level_delta:0.05",
    "level_ratio:0.25",
    "raw_expected_ratio:0.25",
    "raw_tuned_abs_cent_offset:3",
    "pitch_confidence:0.10",
    "harmonicity:0.10",
    "fit_error:0.05",
    "guitar_score:0.10",
    "keyboard_score:0.10",
    "other_score:0.10",
)


@dataclass(frozen=True)
class NoteLevel:
    row: str
    note: str
    midi: int
    level: float


@dataclass(frozen=True)
class Alias:
    shadow: NoteLevel
    support: NoteLevel
    interval: int


@dataclass(frozen=True)
class AliasRecord:
    category: str
    row: dict[str, str]
    alias: Alias


@dataclass(frozen=True)
class ThresholdRule:
    debug_relation: str
    owner_mode: str
    interval_mode: str
    max_guitar_score: float | None
    min_non_guitar_score: float | None
    min_harmonicity: float | None
    max_shadow_support_ratio: float | None
    min_support_level: float | None
    max_fit_error: float | None
    max_noise: float | None


@dataclass(frozen=True)
class ThresholdMatch:
    rule: ThresholdRule
    positive: int
    protected: int
    other: int


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def pitch_class(midi: int) -> int:
    return (midi % 12 + 12) % 12


def parse_note_levels(row: dict[str, str], row_name: str) -> list[NoteLevel]:
    fields = ROW_NOTE_FIELDS.get(row_name)
    if not fields:
        return []

    value = ""
    for field in fields:
        value = row.get(field, "")
        if value:
            break

    notes: list[NoteLevel] = []
    seen: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part or part == "--":
            continue
        note, _, level_text = part.partition(":")
        note = note.strip()
        midi = midi_from_note(note)
        if midi is None:
            continue
        try:
            level = float(level_text) if level_text else 1.0
        except ValueError:
            level = 0.0
        if midi in seen:
            continue
        seen.add(midi)
        notes.append(NoteLevel(row_name, note, midi, level))
    return notes


def expected_row(row: dict[str, str]) -> str:
    family = row.get("family", "")
    return EXPECTED_ROW.get(family, family or "unknown")


def source_key(row: dict[str, str]) -> str:
    family = row.get("family", "") or "unknown"
    source = row.get("source", "") or row.get("nsynth_family", "") or "unknown"
    return f"{family}/{source}"


def group_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("sample_id", ""), row.get("buffer", "")


def interval_supported(interval: int, mode: str, tolerance: int) -> bool:
    if interval <= 0:
        return False
    if mode == "octave":
        return interval % 12 == 0
    if mode == "same-pitch-class":
        return interval % 12 == 0
    return any(abs(interval - candidate) <= tolerance for candidate in HARMONIC_INTERVALS)


def find_alias(
    row: dict[str, str],
    shadow_row: str,
    support_rows: list[str],
    min_shadow_level: float,
    min_support_level: float,
    min_interval: int,
    max_interval: int,
    interval_mode: str,
    interval_tolerance: int,
) -> Alias | None:
    shadows = parse_note_levels(row, shadow_row)
    supports: list[NoteLevel] = []
    for support_row in support_rows:
        supports.extend(parse_note_levels(row, support_row))

    best: Alias | None = None
    best_score = -1.0
    for shadow in shadows:
        if shadow.level < min_shadow_level:
            continue
        for support in supports:
            if support.level < min_support_level:
                continue
            interval = shadow.midi - support.midi
            if interval < min_interval or interval > max_interval:
                continue
            if interval_mode in {"octave", "same-pitch-class"} and pitch_class(shadow.midi) != pitch_class(support.midi):
                continue
            if not interval_supported(interval, interval_mode, interval_tolerance):
                continue
            score = (shadow.level - support.level * 0.5) + interval * 0.001
            if score > best_score:
                best = Alias(shadow, support, interval)
                best_score = score
    return best


def read_groups(path: pathlib.Path) -> dict[tuple[str, str], list[dict[str, str]]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            groups[group_key(row)].append(row)
    return groups


def first_group_row(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        return {}
    return rows[0]


def print_counter(label: str, counter: Counter[str], top: int) -> None:
    if not counter:
        print(f"{label} --")
        return
    print(label, " ".join(f"{key}={value}" for key, value in counter.most_common(top)))


def as_float_text(value: str) -> float | None:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def row_float(row: dict[str, str], field: str) -> float | None:
    return as_float_text(row.get(field, ""))


def row_int(row: dict[str, str], field: str) -> int | None:
    value = row_float(row, field)
    if value is None:
        return None
    return int(round(value))


def owner_key(row: dict[str, str]) -> str:
    owner = (row.get("debug_owner", "") or "").strip().lower()
    if owner == "keyboard":
        return "piano"
    if owner == "ambiguous":
        return "amb"
    if owner == "vocal":
        return "vocals"
    return owner


def alias_text(alias: Alias) -> str:
    return (
        f"{alias.shadow.row}:{alias.shadow.note}:{alias.shadow.level:.2f}"
        f"<-{alias.support.row}:{alias.support.note}:{alias.support.level:.2f}"
        f"/+{alias.interval}"
    )


def derived_value(row: dict[str, str], alias: Alias, field: str) -> str:
    if field == "route":
        return f"{source_key(row)}->{alias.shadow.row}"
    if field == "expected_route":
        return f"{expected_row(row)}->{alias.shadow.row}"
    if field == "visual_route":
        return f"{row.get('visual_first_row', '') or row.get('first_row', '')}->{alias.shadow.row}"
    if field == "interval":
        return str(alias.interval)
    if field == "shadow_row":
        return alias.shadow.row
    if field == "support_row":
        return alias.support.row
    if field == "shadow_note":
        return alias.shadow.note
    if field == "support_note":
        return alias.support.note
    if field == "shadow_midi":
        return str(alias.shadow.midi)
    if field == "support_midi":
        return str(alias.support.midi)
    if field == "shadow_level":
        return f"{alias.shadow.level:.6f}"
    if field == "support_level":
        return f"{alias.support.level:.6f}"
    if field == "level_delta":
        return f"{alias.shadow.level - alias.support.level:.6f}"
    if field == "level_ratio":
        if alias.support.level <= 0:
            return ""
        return f"{alias.shadow.level / alias.support.level:.6f}"
    if field == "support_ratio":
        if alias.shadow.level <= 0:
            return ""
        return f"{alias.support.level / alias.shadow.level:.6f}"
    if field == "support_advantage":
        return f"{alias.support.level - alias.shadow.level:.6f}"
    if field == "debug_relation":
        debug_midi = row_int(row, "debug_midi")
        if debug_midi is None:
            return "missing"
        if debug_midi == alias.shadow.midi:
            return "shadow"
        if debug_midi == alias.support.midi:
            return "support"
        if pitch_class(debug_midi) == pitch_class(alias.shadow.midi):
            return "same-pitch-class"
        return "other"
    if field == "debug_owner":
        return owner_key(row)
    if field == "non_guitar_score":
        scores = [
            row_float(row, "bass_score") or 0.0,
            row_float(row, "keyboard_score") or 0.0,
            row_float(row, "vocal_score") or 0.0,
            row_float(row, "other_score") or 0.0,
        ]
        return f"{max(scores):.6f}"
    return row.get(field, "")


def parse_profile_spec(spec: str) -> tuple[str, Decimal | None]:
    field, separator, width_text = spec.partition(":")
    if not field:
        raise SystemExit(f"invalid profile field `{spec}`")
    if not separator:
        return field, None
    try:
        width = Decimal(width_text)
    except InvalidOperation as exc:
        raise SystemExit(f"invalid profile bucket width `{width_text}`") from exc
    if width <= 0:
        raise SystemExit(f"invalid profile bucket width `{width_text}`; must be positive")
    return field, width


def bucket_value(value_text: str, width: Decimal | None) -> str:
    if width is None:
        return value_text or "-"
    try:
        value = Decimal(value_text)
    except InvalidOperation:
        return "-"
    places = max(0, -width.as_tuple().exponent)
    bucket_index = (value / width).to_integral_value(rounding=ROUND_FLOOR)
    low = bucket_index * width
    high = low + width
    return f"{low:.{places}f}-{high:.{places}f}"


def detail_text(row: dict[str, str], alias: Alias, detail_fields: list[str]) -> str:
    fields = [
        f"sample_id={row.get('sample_id', '')}",
        f"buffer={row.get('buffer', '')}",
        f"family={row.get('family', '')}",
        f"source={row.get('source', '')}",
        f"expected={expected_row(row)}/{row.get('expected_note', '')}",
        f"visual={row.get('visual_first_row', '') or row.get('first_row', '')}",
        f"alias={alias_text(alias)}",
    ]
    for field in detail_fields:
        value = derived_value(row, alias, field)
        if value:
            fields.append(f"{field}={value}")
    return "\t".join(fields)


def owner_mode_matches(owner: str, mode: str) -> bool:
    if mode == "any":
        return True
    if mode == "guitar":
        return owner == "guitar"
    if mode == "non-guitar":
        return owner != "guitar"
    if mode == "other":
        return owner == "other"
    if mode == "piano":
        return owner == "piano"
    if mode == "other-or-piano":
        return owner in {"other", "piano"}
    if mode == "non-guitar-non-amb":
        return owner not in {"guitar", "amb"}
    raise AssertionError(mode)


def debug_relation_matches(relation: str, mode: str) -> bool:
    if mode == "any":
        return True
    return relation == mode


def interval_mode_matches(interval: int, mode: str) -> bool:
    if mode == "any":
        return True
    if mode == "exact12":
        return interval == 12
    if mode == "max24":
        return interval <= 24
    if mode == "max36":
        return interval <= 36
    if mode == "min24":
        return interval >= 24
    raise AssertionError(mode)


def threshold_rule_matches(record: AliasRecord, rule: ThresholdRule) -> bool:
    row = record.row
    alias = record.alias
    if not debug_relation_matches(derived_value(row, alias, "debug_relation"), rule.debug_relation):
        return False
    if not owner_mode_matches(owner_key(row), rule.owner_mode):
        return False
    if not interval_mode_matches(alias.interval, rule.interval_mode):
        return False

    guitar_score = row_float(row, "guitar_score")
    non_guitar_score = as_float_text(derived_value(row, alias, "non_guitar_score"))
    harmonicity = row_float(row, "harmonicity")
    fit_error = row_float(row, "fit_error")
    noise = row_float(row, "noise")
    shadow_support_ratio = as_float_text(derived_value(row, alias, "level_ratio"))

    if rule.max_guitar_score is not None and (
        guitar_score is None or guitar_score > rule.max_guitar_score
    ):
        return False
    if rule.min_non_guitar_score is not None and (
        non_guitar_score is None or non_guitar_score < rule.min_non_guitar_score
    ):
        return False
    if rule.min_harmonicity is not None and (
        harmonicity is None or harmonicity < rule.min_harmonicity
    ):
        return False
    if rule.max_shadow_support_ratio is not None and (
        shadow_support_ratio is None or shadow_support_ratio > rule.max_shadow_support_ratio
    ):
        return False
    if rule.min_support_level is not None and alias.support.level < rule.min_support_level:
        return False
    if rule.max_fit_error is not None and (fit_error is None or fit_error > rule.max_fit_error):
        return False
    if rule.max_noise is not None and (noise is None or noise > rule.max_noise):
        return False
    return True


def rule_parts(rule: ThresholdRule) -> list[str]:
    parts = [
        f"debug_relation={rule.debug_relation}",
        f"owner={rule.owner_mode}",
        f"interval={rule.interval_mode}",
    ]
    if rule.max_guitar_score is not None:
        parts.append(f"max_guitar_score={rule.max_guitar_score:.2f}")
    if rule.min_non_guitar_score is not None:
        parts.append(f"min_non_guitar_score={rule.min_non_guitar_score:.2f}")
    if rule.min_harmonicity is not None:
        parts.append(f"min_harmonicity={rule.min_harmonicity:.2f}")
    if rule.max_shadow_support_ratio is not None:
        parts.append(f"max_shadow_support_ratio={rule.max_shadow_support_ratio:.2f}")
    if rule.min_support_level is not None:
        parts.append(f"min_support_level={rule.min_support_level:.2f}")
    if rule.max_fit_error is not None:
        parts.append(f"max_fit_error={rule.max_fit_error:.2f}")
    if rule.max_noise is not None:
        parts.append(f"max_noise={rule.max_noise:.2f}")
    return parts


def rule_complexity(rule: ThresholdRule) -> int:
    return sum(
        1
        for value in (
            rule.max_guitar_score,
            rule.min_non_guitar_score,
            rule.min_harmonicity,
            rule.max_shadow_support_ratio,
            rule.min_support_level,
            rule.max_fit_error,
            rule.max_noise,
        )
        if value is not None
    ) + (0 if rule.debug_relation == "any" else 1) + (0 if rule.owner_mode == "any" else 1) + (
        0 if rule.interval_mode == "any" else 1
    )


def generate_threshold_rules() -> list[ThresholdRule]:
    debug_relations = ("shadow",)
    owner_modes = ("non-guitar", "other-or-piano", "other", "piano")
    interval_modes = ("any", "exact12", "max24")
    max_guitar_scores: tuple[float | None, ...] = (None, 0.20, 0.42)
    min_non_guitar_scores: tuple[float | None, ...] = (None, 0.70)
    min_harmonicities: tuple[float | None, ...] = (None, 1.00)
    max_shadow_support_ratios: tuple[float | None, ...] = (None, 1.00)
    min_support_levels: tuple[float | None, ...] = (None, 0.65, 0.80)
    max_fit_errors: tuple[float | None, ...] = (None, 0.18)
    max_noises: tuple[float | None, ...] = (None, 0.35)

    rules: list[ThresholdRule] = []
    for debug_relation in debug_relations:
        for owner_mode in owner_modes:
            for interval_mode in interval_modes:
                for max_guitar_score in max_guitar_scores:
                    for min_non_guitar_score in min_non_guitar_scores:
                        for min_harmonicity in min_harmonicities:
                            for max_shadow_support_ratio in max_shadow_support_ratios:
                                for min_support_level in min_support_levels:
                                    for max_fit_error in max_fit_errors:
                                        for max_noise in max_noises:
                                            rules.append(
                                                ThresholdRule(
                                                    debug_relation,
                                                    owner_mode,
                                                    interval_mode,
                                                    max_guitar_score,
                                                    min_non_guitar_score,
                                                    min_harmonicity,
                                                    max_shadow_support_ratio,
                                                    min_support_level,
                                                    max_fit_error,
                                                    max_noise,
                                                )
                                            )
    return rules


def threshold_search(
    records: list[AliasRecord],
    min_positive: int,
    max_protected: int,
) -> list[ThresholdMatch]:
    matches: list[ThresholdMatch] = []
    positive_records = [record for record in records if record.category == "positive"]
    protected_records = [record for record in records if record.category == "protected"]
    other_records = [record for record in records if record.category == "other"]
    for rule in generate_threshold_rules():
        protected = 0
        for record in protected_records:
            if threshold_rule_matches(record, rule):
                protected += 1
                if protected > max_protected:
                    break
        if protected > max_protected:
            continue

        positive = sum(1 for record in positive_records if threshold_rule_matches(record, rule))
        if positive < min_positive:
            continue
        other = sum(1 for record in other_records if threshold_rule_matches(record, rule))
        if positive >= min_positive and protected <= max_protected:
            matches.append(ThresholdMatch(rule, positive, protected, other))

    matches.sort(
        key=lambda match: (
            match.protected,
            -match.positive,
            match.other,
            rule_complexity(match.rule),
            " ".join(rule_parts(match.rule)),
        )
    )
    return matches


def print_threshold_search(
    records: list[AliasRecord],
    matches: list[ThresholdMatch],
    limit: int,
    examples: int,
    detail_fields: list[str],
) -> None:
    totals = Counter(record.category for record in records)
    print(
        "threshold_search:"
        f" candidates={len(matches)}"
        f" positive_total={totals['positive']}"
        f" protected_total={totals['protected']}"
        f" other_total={totals['other']}"
    )
    for match in matches[: max(0, limit)]:
        rule = match.rule
        print(
            "threshold_rule"
            f" positive={match.positive}/{totals['positive']}"
            f" protected={match.protected}/{totals['protected']}"
            f" other={match.other}/{totals['other']}"
            " "
            + " ".join(rule_parts(rule))
        )
        if examples <= 0:
            continue
        printed: Counter[str] = Counter()
        for record in records:
            if printed[record.category] >= examples:
                continue
            if not threshold_rule_matches(record, rule):
                continue
            print(f"threshold_{record.category}\t{detail_text(record.row, record.alias, detail_fields)}")
            printed[record.category] += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--shadow-row", choices=sorted(ROW_NOTE_FIELDS), default="guitar")
    parser.add_argument(
        "--support-row",
        action="append",
        dest="support_rows",
        choices=sorted(ROW_NOTE_FIELDS),
        help="support row to compare against; repeatable",
    )
    parser.add_argument("--min-shadow-level", type=float, default=0.68)
    parser.add_argument("--min-support-level", type=float, default=0.45)
    parser.add_argument("--min-interval", type=int, default=12)
    parser.add_argument("--max-interval", type=int, default=60)
    parser.add_argument(
        "--interval-mode",
        choices=("octave", "same-pitch-class", "harmonic"),
        default="same-pitch-class",
    )
    parser.add_argument("--interval-tolerance", type=int, default=1)
    parser.add_argument("--examples", type=int, default=6)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument(
        "--details",
        action="store_true",
        help="print structured detail lines for sampled positive/protected/other aliases",
    )
    parser.add_argument(
        "--detail-field",
        action="append",
        default=None,
        help="row or derived field to include in --details output; repeatable",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="print bucketed profiles for positive/protected/other aliases",
    )
    parser.add_argument(
        "--profile-field",
        action="append",
        default=None,
        help=(
            "row or derived field to profile, optionally FIELD:WIDTH for numeric buckets; "
            "repeatable"
        ),
    )
    parser.add_argument(
        "--threshold-search",
        action="store_true",
        help="search simple guitar alias suppression thresholds over positive/protected alias records",
    )
    parser.add_argument(
        "--search-min-positive",
        type=int,
        default=8,
        help="minimum positive alias hits required for threshold-search output",
    )
    parser.add_argument(
        "--search-max-protected",
        type=int,
        default=0,
        help="maximum protected guitar alias hits allowed for threshold-search output",
    )
    parser.add_argument("--search-limit", type=int, default=12, help="threshold-search rules to print")
    parser.add_argument(
        "--search-examples",
        type=int,
        default=2,
        help="examples per category to print under each threshold-search rule",
    )
    args = parser.parse_args()

    support_rows = args.support_rows or ["piano", "other"]
    if args.shadow_row in support_rows:
        print("shadow row must not also be a support row", file=sys.stderr)
        return 2

    groups = read_groups(args.path)
    alias_groups = 0
    positive_visual = 0
    protected_visual = 0
    other_alias = 0
    positive_routes: Counter[str] = Counter()
    protected_routes: Counter[str] = Counter()
    alias_routes: Counter[str] = Counter()
    interval_counts: Counter[str] = Counter()
    examples: list[str] = []
    protected_examples: list[str] = []
    other_examples: list[str] = []
    detail_fields = args.detail_field or list(DEFAULT_DETAIL_FIELDS)
    profile_specs = [parse_profile_spec(spec) for spec in (args.profile_field or DEFAULT_PROFILE_FIELDS)]
    profile_counters: dict[str, dict[str, Counter[str]]] = {
        "positive": defaultdict(Counter),
        "protected": defaultdict(Counter),
        "other": defaultdict(Counter),
    }
    records: list[AliasRecord] = []

    def record_profile(category: str, row: dict[str, str], alias: Alias) -> None:
        if not args.profile:
            return
        for field, width in profile_specs:
            value = bucket_value(derived_value(row, alias, field), width)
            profile_counters[category][field][value] += 1

    for rows in groups.values():
        row = first_group_row(rows)
        alias = find_alias(
            row,
            args.shadow_row,
            support_rows,
            args.min_shadow_level,
            args.min_support_level,
            args.min_interval,
            args.max_interval,
            args.interval_mode,
            args.interval_tolerance,
        )
        if alias is None:
            continue

        alias_groups += 1
        expected = expected_row(row)
        visual_first = row.get("visual_first_row", "") or row.get("first_row", "")
        route = f"{source_key(row)}->{args.shadow_row}"
        alias_routes[route] += 1
        interval_counts[str(alias.interval)] += 1

        example = (
            f"{row.get('sample_id', '')}@{row.get('buffer', '')}"
            f" expected={expected}/{row.get('expected_note', '')}"
            f" visual={visual_first} alias={alias_text(alias)}"
        )
        if visual_first == args.shadow_row and expected != args.shadow_row:
            positive_visual += 1
            positive_routes[route] += 1
            record_profile("positive", row, alias)
            records.append(AliasRecord("positive", row, alias))
            if len(examples) < args.examples:
                examples.append(detail_text(row, alias, detail_fields) if args.details else example)
        elif visual_first == args.shadow_row and expected == args.shadow_row:
            protected_visual += 1
            protected_routes[route] += 1
            record_profile("protected", row, alias)
            records.append(AliasRecord("protected", row, alias))
            if len(protected_examples) < args.examples:
                protected_examples.append(
                    detail_text(row, alias, detail_fields) if args.details else example
                )
        else:
            other_alias += 1
            record_profile("other", row, alias)
            records.append(AliasRecord("other", row, alias))
            if args.details and len(other_examples) < args.examples:
                other_examples.append(detail_text(row, alias, detail_fields) if args.details else example)

    print(
        "measure_real_note_octave_display_aliases:"
        f" groups={len(groups)} alias_groups={alias_groups}"
        f" positive_visual={positive_visual} protected_visual={protected_visual}"
        f" other_alias={other_alias}"
    )
    print_counter("positive_routes", positive_routes, args.top)
    print_counter("protected_routes", protected_routes, args.top)
    print_counter("alias_routes", alias_routes, args.top)
    print_counter("intervals", interval_counts, args.top)
    if args.profile:
        for category in ("positive", "protected", "other"):
            for field, _width in profile_specs:
                print_counter(f"{category}_profile {field}", profile_counters[category][field], args.top)
    for example in examples:
        print(f"positive_example\t{example}")
    for example in protected_examples:
        print(f"protected_example\t{example}")
    for example in other_examples:
        print(f"other_example\t{example}")
    if args.threshold_search:
        matches = threshold_search(records, args.search_min_positive, args.search_max_protected)
        print_threshold_search(
            records,
            matches,
            args.search_limit,
            args.search_examples,
            detail_fields,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
