#!/usr/bin/env python3
"""Inspect generated instrument sample full-mix owner buckets."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics


FIELDS = [
    "midi",
    "expected_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "debug_conf",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
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
]

ROW_DUMP_FIELDS = [
    "kind",
    "status",
    "family",
    "expected_family",
    "program_name",
    "note",
    "midi",
    "path",
    "window_ms",
    "detected_expected_row",
    "detected_anywhere",
    "debug_note",
    "debug_owner",
    "debug_conf",
    "nearest_debug_note",
    "nearest_debug_delta",
    "nearest_debug_abs_delta",
    "nearest_debug_owner",
    "nearest_debug_conf",
    "miss_reason",
    "owner",
    "owner_source",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_note",
    "raw_expected_rank",
    "bass_score",
    "keyboard_score",
    "guitar_score",
    "vocal_score",
    "other_score",
    "spectral_level",
    "pitch_confidence",
    "periodicity",
    "harmonicity",
    "fit_error",
    "noise",
    "debug_count",
    "debug_candidates",
]

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


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def midi_from_note(value: str) -> int | None:
    match = NOTE_RE.match(value or "")
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def parse_debug_candidates(value: str) -> list[tuple[str, int, str, float]]:
    candidates: list[tuple[str, int, str, float]] = []
    if not value:
        return candidates
    for item in value.split(","):
        fields = item.split("/")
        if len(fields) < 3:
            continue
        note = fields[0]
        midi = midi_from_note(note)
        if midi is None:
            continue
        try:
            confidence = float(fields[2])
        except ValueError:
            confidence = 0.0
        candidates.append((note, midi, fields[1], confidence))
    return candidates


def nearest_debug_candidate(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    expected = as_float(row, "midi")
    if expected is None:
        return "", "", "", "", ""
    expected_midi = int(round(expected))
    candidates = parse_debug_candidates(row.get("debug_candidates", ""))
    debug_midi = midi_from_note(row.get("debug_note", ""))
    if debug_midi is not None:
        try:
            debug_confidence = float(row.get("debug_conf", "") or "0")
        except ValueError:
            debug_confidence = 0.0
        candidates.append(
            (row.get("debug_note", ""), debug_midi, row.get("debug_owner", ""), debug_confidence)
        )
    if not candidates:
        return "", "", "", "", ""
    note, midi, owner, confidence = min(
        candidates,
        key=lambda candidate: (abs(candidate[1] - expected_midi), -candidate[3], candidate[0]),
    )
    delta = midi - expected_midi
    return note, str(delta), str(abs(delta)), owner, f"{confidence:.6f}"


def miss_reason(row: dict[str, str], nearest_abs_delta: str) -> str:
    if row.get("status") == "hit":
        return "hit"
    if row.get("detected_anywhere") == "1":
        return "ownership"
    raw_rank = as_float(row, "raw_expected_rank")
    cent = as_float(row, "raw_tuned_abs_cent_offset")
    if raw_rank is not None and raw_rank >= 4.0:
        return "weak_expected_rank"
    if raw_rank is not None and raw_rank <= 1.0 and cent is not None and cent > 9.0:
        return "strict_tuning_reject"
    try:
        nearest_delta = int(nearest_abs_delta)
    except ValueError:
        nearest_delta = 99
    if nearest_delta <= 1:
        return "adjacent_candidate"
    if cent is not None and cent > 9.0:
        return "detuned"
    return "unresolved"


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * fraction))
    return values[index]


def compact_counter(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def owner_target(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family == "piano":
        return "piano"
    if family == "guitar":
        return "guitar"
    if family == "vocals":
        return "vocals"
    if family in {"strings", "synth"}:
        return "other"
    if family == "bass":
        return "bass"
    return family or "unknown"


DISPLAY_LEVEL_FIELDS = {
    "bass": "bass_level",
    "piano": "piano_level",
    "guitar": "guitar_level",
    "vocals": "vocal_level",
    "other": "other_level",
}


def target_display_hit(row: dict[str, str], target: str) -> bool:
    if row.get("status") != "hit" or row.get("detected_expected_row") != "1":
        return False
    field = DISPLAY_LEVEL_FIELDS.get(target)
    return field is not None and (as_float(row, field) or 0.0) > 0.0


def owner_and_source(row: dict[str, str]) -> tuple[str, str]:
    target = owner_target(row)
    if target_display_hit(row, target):
        return target, "display"
    return row.get("debug_owner", "") or "none", "debug"


def bucket_key(row: dict[str, str]) -> tuple[str, str, str]:
    target = owner_target(row)
    owner, _source = owner_and_source(row)
    status = "owner_hit" if owner == target else "owner_miss"
    return row.get("family", "unknown"), status, owner


def derive_row(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    note, delta, abs_delta, owner, confidence = nearest_debug_candidate(row)
    result["nearest_debug_note"] = note
    result["nearest_debug_delta"] = delta
    result["nearest_debug_abs_delta"] = abs_delta
    result["nearest_debug_owner"] = owner
    result["nearest_debug_conf"] = confidence
    result["miss_reason"] = miss_reason(row, abs_delta)
    result["owner"], result["owner_source"] = owner_and_source(row)
    return result


def print_bucket(key: tuple[str, str, str], rows: list[dict[str, str]], examples: int) -> None:
    family, status, owner = key
    print()
    print(f"{status}:{family}->{owner} rows={len(rows)}")
    print(f"  programs {compact_counter(collections.Counter(row.get('program_name', '') for row in rows))}")
    print(f"  notes {compact_counter(collections.Counter(row.get('note', '') for row in rows))}")
    print(f"  raw_best {compact_counter(collections.Counter(row.get('raw_local_best_note', '') for row in rows))}")
    for field in FIELDS:
        values = sorted(value for row in rows if (value := as_float(row, field)) is not None)
        if not values:
            continue
        print(
            f"  {field:26s} min={values[0]:7.3f} q25={quantile(values, 0.25):7.3f} "
            f"med={statistics.median(values):7.3f} q75={quantile(values, 0.75):7.3f} "
            f"max={values[-1]:7.3f}"
        )
    for row in rows[:examples]:
        print(
            "  example "
            f"{row.get('family', '')} {row.get('program_name', '')} {row.get('note', '')} "
            f"{row.get('path', '')} owner={owner_and_source(row)[0]} source={owner_and_source(row)[1]} "
            f"debug_owner={row.get('debug_owner', '') or 'none'} "
            f"scores=b:{row.get('bass_score', '')},k:{row.get('keyboard_score', '')},g:{row.get('guitar_score', '')},"
            f"v:{row.get('vocal_score', '')},o:{row.get('other_score', '')} "
            f"raw={row.get('raw_expected_ratio', '')}/{row.get('raw_tuned_ratio', '')}"
        )


def dump_rows(rows: list[dict[str, str]], *, misses_only: bool, limit: int) -> None:
    printed = 0
    print("\t".join(ROW_DUMP_FIELDS))
    for row in rows:
        if misses_only and bucket_key(row)[1] != "owner_miss":
            continue
        derived = derive_row(row)
        print("\t".join(derived.get(field, "") for field in ROW_DUMP_FIELDS))
        printed += 1
        if limit > 0 and printed >= limit:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--examples", type=int, default=4)
    parser.add_argument(
        "--dump-rows",
        action="store_true",
        help="print compact per-note detected attributes as TSV and skip bucket summaries",
    )
    parser.add_argument(
        "--misses-only",
        action="store_true",
        help="with --dump-rows, print only owner-miss note rows",
    )
    parser.add_argument(
        "--dump-limit",
        type=int,
        default=0,
        help="maximum rows to print in --dump-rows mode; 0 means all",
    )
    args = parser.parse_args()

    all_note_rows = [
        row
        for row in load_rows(args.path)
        if row.get("kind") == "note"
    ]
    if args.dump_rows:
        dump_rows(all_note_rows, misses_only=args.misses_only, limit=max(0, args.dump_limit))
        return 0

    rows = all_note_rows

    print(f"inspect_instrument_sample_owner_buckets: note rows {len(rows)}")
    counts = collections.Counter(bucket_key(row) for row in rows)
    print("owner buckets " + " ".join(f"{'/'.join(key)}={count}" for key, count in counts.most_common(args.top)))

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        grouped[bucket_key(row)].append(row)

    for key, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[: args.top]:
        print_bucket(key, group, max(0, args.examples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
