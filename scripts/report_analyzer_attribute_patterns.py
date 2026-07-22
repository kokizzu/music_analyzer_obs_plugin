#!/usr/bin/env python3
"""Print a compact pattern report from analyzer attribute row dumps."""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics


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
DRUMS = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
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


def float_or(row: dict[str, str], field: str, default: float) -> float:
    value = as_float(row, field)
    return default if value is None else value


def midi_from_note(note: str) -> int | None:
    match = NOTE_RE.match(note)
    if not match:
        return None
    return NOTE_BASE[match.group(1)] + (int(match.group(2)) + 1) * 12


def compact(counter: collections.Counter[str], limit: int) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def unique_sample_count(rows: list[dict[str, str]], field: str) -> int:
    return len({row.get(field, "") for row in rows if row.get(field, "")})


def ratio(count: int, total: int) -> str:
    if total <= 0:
        return "0/0"
    return f"{count}/{total} ({count * 100.0 / total:.1f}%)"


def median(values: list[float]) -> str:
    if not values:
        return "--"
    return f"{statistics.median(values):.3f}".rstrip("0").rstrip(".")


def short_path(value: str, max_parts: int = 3) -> str:
    if not value:
        return "--"
    parts = pathlib.PurePath(value).parts
    if len(parts) <= max_parts:
        return value
    return "/".join(parts[-max_parts:])


def num(row: dict[str, str], field: str) -> str:
    value = as_float(row, field)
    if value is None:
        return "--"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def cell(row: dict[str, str], field: str, default: str = "--") -> str:
    value = row.get(field, "")
    return value if value else default


def level_cells(row: dict[str, str], fields: tuple[str, ...]) -> str:
    return ",".join(f"{field.removesuffix('_level')}:{num(row, field)}" for field in fields)


def score_cells(row: dict[str, str]) -> str:
    return ",".join(
        f"{label}:{num(row, field)}"
        for label, field in (
            ("key", "keyboard_score"),
            ("gtr", "guitar_score"),
            ("voc", "vocal_score"),
            ("oth", "other_score"),
        )
    )


def trigger_cells(row: dict[str, str]) -> str:
    parts = []
    for drum in DRUMS:
        parts.append(f"{drum}:{num(row, drum + '_trigger')}/{num(row, drum + '_threshold')}")
    return ",".join(parts)


def representative_rows(
    rows: list[dict[str, str]],
    group_fields: tuple[str, ...],
    limit: int,
    *,
    prefer_non_hit: bool = True,
) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    ordered = sorted(
        rows,
        key=lambda row: (
            (row.get("status", "") == "hit") if prefer_non_hit else False,
            *(row.get(field, "") for field in group_fields),
            cell(row, "sample_id"),
            cell(row, "recording_id"),
            cell(row, "sample"),
            cell(row, "path"),
        ),
    )
    selected: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for row in ordered:
        key = tuple(row.get(field, "") for field in group_fields)
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def section(title: str) -> None:
    print()
    print(title)


def report_instruments(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("kind") == "note" and row.get("debug_note")]
    section("instrument sample attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(f"  note rows={len(rows)}")
    family_counts = collections.Counter(row.get("family", "unknown") for row in rows)
    print(f"  families {compact(family_counts, limit)}")
    for family, _count in family_counts.most_common(limit):
        family_rows = [row for row in rows if row.get("family") == family]
        owners = collections.Counter(row.get("debug_owner", "none") or "none" for row in family_rows)
        raw_rank1 = sum(1 for row in family_rows if float_or(row, "raw_expected_rank", 99.0) <= 1.0)
        tuned = sum(1 for row in family_rows if float_or(row, "raw_tuned_abs_cent_offset", 99.0) <= 9.0)
        print(
            f"  {family}: rows={len(family_rows)} owners={compact(owners, 5)} "
            f"raw_rank1={ratio(raw_rank1, len(family_rows))} tuned<=9c={ratio(tuned, len(family_rows))}"
        )
    examples = representative_rows(rows, ("status", "family", "debug_owner"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} {cell(row, 'family')} "
                f"expected={cell(row, 'note')}/{cell(row, 'midi')} "
                f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
                f"levels={level_cells(row, ('bass_level', 'piano_level', 'guitar_level', 'vocal_level', 'other_level', 'amb_level'))} "
                f"raw_ratio={num(row, 'raw_expected_ratio')} tuned_ratio={num(row, 'raw_tuned_ratio')} "
                f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
                f"scores={score_cells(row)} file={short_path(cell(row, 'path', ''))}"
            )


def real_note_bucket(row: dict[str, str]) -> str:
    return (
        f"{row.get('status', '')}:{row.get('family', '')}/"
        f"{row.get('source', '')}->{row.get('first_row', '')}"
    )


def report_real_notes(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample_id")]
    section("real-note full-mix attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    by_sample_status: dict[str, str] = {}
    for row in rows:
        by_sample_status.setdefault(row["sample_id"], row.get("status", "unknown"))
    print(f"  rows={len(rows)} samples={len(by_sample_status)} status={compact(collections.Counter(by_sample_status.values()), limit)}")
    miss_rows = [row for row in rows if row.get("status") == "ownership_miss" and row.get("debug_note")]
    print(f"  ownership miss rows={len(miss_rows)} samples={unique_sample_count(miss_rows, 'sample_id')}")
    raw_rank1 = sum(1 for row in miss_rows if float_or(row, "raw_expected_rank", 99.0) <= 1.0)
    raw_strong = sum(1 for row in miss_rows if float_or(row, "raw_expected_ratio", 0.0) >= 0.90)
    tuned = sum(1 for row in miss_rows if float_or(row, "raw_tuned_abs_cent_offset", 99.0) <= 9.0)
    print(
        f"  miss raw evidence raw_rank1={ratio(raw_rank1, len(miss_rows))} "
        f"raw_ratio>=0.90={ratio(raw_strong, len(miss_rows))} tuned<=9c={ratio(tuned, len(miss_rows))}"
    )
    deltas: collections.Counter[str] = collections.Counter()
    for row in miss_rows:
        expected = as_float(row, "expected_midi")
        debug_midi = midi_from_note(row.get("debug_note", ""))
        if expected is None or debug_midi is None:
            continue
        deltas[str(int(debug_midi - expected))] += 1
    print(f"  debug-midi deltas {compact(deltas, limit)}")
    bucket_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in miss_rows:
        bucket_rows[real_note_bucket(row)].append(row)
    for bucket, bucket_group in sorted(bucket_rows.items(), key=lambda item: (-len(item[1]), item[0]))[:limit]:
        print(
            f"  {bucket}: rows={len(bucket_group)} samples={unique_sample_count(bucket_group, 'sample_id')} "
            f"debug_owner={compact(collections.Counter(row.get('debug_owner', 'none') or 'none' for row in bucket_group), 4)} "
            f"strongest={compact(collections.Counter(row.get('buffer_strongest_row', 'none') or 'none' for row in bucket_group), 4)} "
            f"raw_best={compact(collections.Counter(row.get('raw_local_best_note', '') for row in bucket_group), 4)}"
        )
    examples = representative_rows(rows, ("status", "family", "source", "first_row", "debug_owner"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} {cell(row, 'family')}/{cell(row, 'source')} "
                f"expected={cell(row, 'expected_note')}/{cell(row, 'expected_midi')} "
                f"first={cell(row, 'first_row')} buffer={cell(row, 'buffer')} "
                f"got={cell(row, 'debug_note')}/{cell(row, 'debug_owner')} "
                f"levels={level_cells(row, ('bass_level', 'guitar_level', 'piano_level', 'vocal_level', 'other_level', 'amb_level'))} "
                f"raw={num(row, 'raw_expected_ratio')}/{num(row, 'raw_tuned_ratio')} "
                f"cent={num(row, 'raw_tuned_abs_cent_offset')} rank={num(row, 'raw_expected_rank')} "
                f"scores={score_cells(row)} sample={cell(row, 'sample_id')}"
            )


def split_list_cell(value: str) -> list[str]:
    if not value or value == "--":
        return []
    return [item for item in value.split(",") if item]


def report_guitar_chords(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("recording_id")]
    section("guitar chord attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    print(f"  rows={len(rows)} recordings={unique_sample_count(rows, 'recording_id')} status={compact(collections.Counter(row.get('status', 'unknown') for row in rows), limit)}")
    miss_rows = [row for row in rows if row.get("status") == "chord_miss"]
    print(f"  chord miss rows={len(miss_rows)} recordings={unique_sample_count(miss_rows, 'recording_id')}")
    print(f"  miss support {compact(collections.Counter(row.get('support', '') for row in miss_rows), limit)}")
    tone_counts: collections.Counter[str] = collections.Counter()
    for row in miss_rows:
        for field in ("visible_missing_tones", "analysis_missing_tones", "smooth_missing_tones"):
            for tone in split_list_cell(row.get(field, "")):
                tone_counts[tone] += 1
    print(f"  missing tones {compact(tone_counts, limit)}")
    print(
        "  raw tone medians "
        f"root={median([value for row in miss_rows if (value := as_float(row, 'raw_root')) is not None])} "
        f"third={median([value for row in miss_rows if (value := as_float(row, 'raw_third')) is not None])} "
        f"fifth={median([value for row in miss_rows if (value := as_float(row, 'raw_fifth')) is not None])}"
    )
    support_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in miss_rows:
        support_rows[f"{row.get('status', '')}:{row.get('quality', '')}:{row.get('support', '')}"].append(row)
    for bucket, bucket_group in sorted(support_rows.items(), key=lambda item: (-len(item[1]), item[0]))[:limit]:
        print(
            f"  {bucket}: rows={len(bucket_group)} recs={unique_sample_count(bucket_group, 'recording_id')} "
            f"expected={compact(collections.Counter(row.get('expected_chords', '') for row in bucket_group), 5)} "
            f"pred={compact(collections.Counter(row.get('guitar_chord', '') for row in bucket_group), 5)}"
        )
    examples = representative_rows(rows, ("status", "quality", "support"), row_examples)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'status')} quality={cell(row, 'quality')} "
                f"expected={cell(row, 'expected_chords')} got={cell(row, 'guitar_chord')} "
                f"pc={cell(row, 'guitar_pitch_classes')} analysis_pc={cell(row, 'guitar_analysis_pitch_classes')} "
                f"smooth_pc={cell(row, 'guitar_smoothed_pitch_classes')} "
                f"missing=v:{cell(row, 'visible_missing_tones')} a:{cell(row, 'analysis_missing_tones')} s:{cell(row, 'smooth_missing_tones')} "
                f"tones=root:{num(row, 'raw_root')} third:{num(row, 'raw_third')} fifth:{num(row, 'raw_fifth')} "
                f"quality_raw={cell(row, 'quality_raw', cell(row, 'expected_quality_raw_profile'))} "
                f"rms={num(row, 'rms')} rec={cell(row, 'recording_id')}"
            )


def report_drums(path: pathlib.Path, limit: int, row_examples: int) -> None:
    rows = [row for row in load_rows(path) if row.get("sample")]
    section("drum primary miss attributes")
    if not rows:
        print(f"  missing rows: {path}")
        return
    routes = collections.Counter(f"{row.get('expected', '')}->{row.get('got', '')}" for row in rows)
    print(f"  rows={len(rows)} routes={compact(routes, limit)}")
    for route, _count in routes.most_common(limit):
        expected, got = route.split("->", 1)
        route_rows = [row for row in rows if row.get("expected") == expected and row.get("got") == got]
        expected_levels = [
            value for row in route_rows if (value := as_float(row, f"{expected}_level")) is not None
        ]
        got_levels = [value for row in route_rows if (value := as_float(row, f"{got}_level")) is not None]
        active = sum(1 for value in expected_levels if value > 0.30)
        print(
            f"  {route}: rows={len(route_rows)} expected_level_med={median(expected_levels)} "
            f"got_level_med={median(got_levels)} expected_active={ratio(active, len(route_rows))} "
            f"energy_med={median([value for row in route_rows if (value := as_float(row, 'energy_low')) is not None])}/"
            f"{median([value for row in route_rows if (value := as_float(row, 'energy_mid')) is not None])}/"
            f"{median([value for row in route_rows if (value := as_float(row, 'energy_high')) is not None])}"
        )
    examples = representative_rows(rows, ("expected", "got"), row_examples, prefer_non_hit=False)
    if examples:
        print("  representative detected rows")
        for row in examples:
            print(
                f"    {cell(row, 'expected')}->{cell(row, 'got')} "
                f"energy={num(row, 'energy_low')}/{num(row, 'energy_mid')}/{num(row, 'energy_high')} "
                f"body={num(row, 'kick_body')}/{num(row, 'snare_body')}/{num(row, 'tom_body')} "
                f"crack={num(row, 'snare_crack')} upper_tom={num(row, 'upper_tom_body')} "
                f"levels={level_cells(row, tuple(f'{drum}_level' for drum in DRUMS))} "
                f"triggers={trigger_cells(row)} "
                f"sample={short_path(cell(row, 'sample', ''))}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument", type=pathlib.Path, default=pathlib.Path("build/instrument_detected_attribute_rows.tsv"))
    parser.add_argument("--real-note", type=pathlib.Path, default=pathlib.Path("build/real_note_detected_attribute_rows.tsv"))
    parser.add_argument("--guitar-chord", type=pathlib.Path, default=pathlib.Path("build/guitar_chord_detected_attribute_rows.tsv"))
    parser.add_argument("--drum", type=pathlib.Path, default=pathlib.Path("build/drum_primary_miss_attribute_rows.tsv"))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument(
        "--row-examples",
        type=int,
        default=4,
        help="print representative row-level detector attributes per section",
    )
    args = parser.parse_args()

    limit = max(1, args.limit)
    row_examples = max(0, args.row_examples)
    report_instruments(args.instrument, limit, row_examples)
    report_real_notes(args.real_note, limit, row_examples)
    report_guitar_chords(args.guitar_chord, limit, row_examples)
    report_drums(args.drum, limit, row_examples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
