#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import statistics
from typing import Iterable


NUMERIC_FIELDS = [
    "expected_level",
    "bass_level",
    "piano_level",
    "guitar_level",
    "vocal_level",
    "other_level",
    "amb_level",
    "rms",
    "low",
    "mid",
    "high",
    "raw_expected_peak",
    "raw_expected_ratio",
    "raw_tuned_peak",
    "raw_tuned_ratio",
    "raw_tuned_cent_offset",
    "raw_tuned_abs_cent_offset",
    "raw_local_best_midi",
    "raw_local_best_peak",
    "raw_expected_rank",
    "raw_prev_ratio",
    "raw_next_ratio",
    "raw_octave_down_ratio",
    "raw_octave_up_ratio",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
    "debug_midi",
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
    "third_octave_ratio",
    "partial1",
    "partial2",
    "partial3",
    "partial4",
    "partial5",
    "debug_count",
    "drum_level",
    "kick_level",
    "snare_level",
    "hihat_level",
    "crash_level",
    "tom_level",
    "ride_level",
    "rim_level",
    "kick_trigger",
    "snare_trigger",
    "hihat_trigger",
    "crash_trigger",
    "tom_trigger",
    "ride_trigger",
    "rim_trigger",
    "kick_threshold",
    "snare_threshold",
    "hihat_threshold",
    "crash_threshold",
    "tom_threshold",
    "ride_threshold",
    "rim_threshold",
    "transient",
    "onset",
    "kick_body",
    "snare_body",
    "tom_body",
    "snare_crack",
    "upper_tom",
]

NOTE_PROFILE_FIELDS = [
    "expected_level",
    "raw_expected_ratio",
    "raw_tuned_ratio",
    "raw_tuned_abs_cent_offset",
    "raw_expected_rank",
    "raw_fifth_up_ratio",
    "raw_second_octave_up_ratio",
    "raw_upper_major_third_ratio",
    "raw_upper_fifth_ratio",
    "raw_third_octave_up_ratio",
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
    "debug_count",
]


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def as_float(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = int(round((len(values) - 1) * fraction))
    return values[max(0, min(len(values) - 1, index))]


def compact_counter(counter: collections.Counter[str], limit: int = 8) -> str:
    if not counter:
        return "--"
    return " ".join(f"{key}={value}" for key, value in counter.most_common(limit))


def numeric_summary(rows: Iterable[dict[str, str]], fields: list[str]) -> list[str]:
    source_rows = list(rows)
    lines: list[str] = []
    for field in fields:
        values = sorted(value for row in source_rows if (value := as_float(row, field)) is not None)
        if not values:
            continue
        lines.append(
            f"  {field}=min{values[0]:.3f}/q25{percentile(values, 0.25):.3f}/"
            f"med{statistics.median(values):.3f}/q75{percentile(values, 0.75):.3f}/"
            f"max{values[-1]:.3f}"
        )
    return lines


def note_row_family(row: dict[str, str]) -> str:
    return row.get("family", "") or row.get("expected_family", "") or "unknown"


def summarize(path: pathlib.Path, top: int, examples: int) -> list[str]:
    rows = load_rows(path)
    lines = [f"summarize_instrument_sample_attributes: rows {len(rows)}"]
    if not rows:
        return lines

    by_kind_status = collections.Counter((row.get("kind", ""), row.get("status", "")) for row in rows)
    lines.append(
        "status "
        + " ".join(f"{kind}:{status}={count}" for (kind, status), count in sorted(by_kind_status.items()))
    )

    note_rows = [row for row in rows if row.get("kind") == "note"]
    drum_rows = [row for row in rows if row.get("kind") == "drum"]

    if note_rows:
        counts = collections.Counter((note_row_family(row), row.get("status", "")) for row in note_rows)
        parts = [f"{family}:{status}={count}" for (family, status), count in sorted(counts.items())]
        lines.append("note status " + " ".join(parts))
        profile_groups: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
        for row in note_rows:
            profile_groups[note_row_family(row)].append(row)
        lines.append("note family profiles")
        for family, group in sorted(profile_groups.items()):
            owners = collections.Counter(row.get("debug_owner", "") or "none" for row in group)
            best_notes = collections.Counter(row.get("raw_local_best_note", "") or "none" for row in group)
            lines.append(
                f"note profile:{family} count {len(group)} "
                f"owners {compact_counter(owners, 6)} raw_best {compact_counter(best_notes, 6)}"
            )
            lines.extend(numeric_summary(group, NOTE_PROFILE_FIELDS))
        miss_groups: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
        for row in note_rows:
            if row.get("status") == "hit":
                continue
            miss_groups[(note_row_family(row), row.get("status", ""))].append(row)
        for (family, status), group in sorted(miss_groups.items(), key=lambda item: (-len(item[1]), item[0]))[:top]:
            lines.append(f"note {status}:{family} count {len(group)}")
            lines.extend(
                numeric_summary(
                    group,
                    [
                        "expected_level",
                        "bass_level",
                        "piano_level",
                        "guitar_level",
                        "vocal_level",
                        "other_level",
                        "amb_level",
                        "rms",
                        "low",
                        "mid",
                        "high",
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
                        "fit_error",
                        "noise",
                        "debug_count",
                    ],
                )
            )
            for row in group[:examples]:
                lines.append(
                    "  example "
                    f"{row.get('program_name', '')} {row.get('note', '')} {row.get('path', '')} "
                    f"expected={family} status={status} levels="
                    f"bass:{row.get('bass_level', '')},piano:{row.get('piano_level', '')},"
                    f"guitar:{row.get('guitar_level', '')},vocal:{row.get('vocal_level', '')},"
                    f"other:{row.get('other_level', '')},amb:{row.get('amb_level', '')} "
                    f"labels=bass:{row.get('bass_label', '')} piano:{row.get('piano_label', '')} "
                    f"guitar:{row.get('guitar_label', '')} vocal:{row.get('vocal_label', '')} "
                    f"other:{row.get('other_label', '')} "
                    f"debug={row.get('debug_note', '')}/{row.get('debug_owner', '')}/"
                    f"{row.get('debug_conf', '')} debug_count={row.get('debug_count', '')} "
                    f"candidates={row.get('debug_candidates', '')} scores="
                    f"b:{row.get('bass_score', '')},k:{row.get('keyboard_score', '')},"
                    f"g:{row.get('guitar_score', '')},"
                    f"v:{row.get('vocal_score', '')},o:{row.get('other_score', '')} "
                    f"raw={row.get('raw_expected_ratio', '')}/{row.get('raw_tuned_ratio', '')}"
                )

    if drum_rows:
        counts = collections.Counter((row.get("expected_family", ""), row.get("status", "")) for row in drum_rows)
        parts = [f"{family}:{status}={count}" for (family, status), count in sorted(counts.items())]
        lines.append("drum status " + " ".join(parts))
        miss_groups: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
        for row in drum_rows:
            if row.get("status") == "hit":
                continue
            miss_groups[(row.get("expected_family", ""), row.get("status", ""))].append(row)
        for (family, status), group in sorted(miss_groups.items(), key=lambda item: (-len(item[1]), item[0]))[:top]:
            lines.append(f"drum {status}:{family} count {len(group)}")
            lines.extend(
                numeric_summary(
                    group,
                    [
                        "drum_level",
                        "kick_level",
                        "snare_level",
                        "hihat_level",
                        "crash_level",
                        "tom_level",
                        "ride_level",
                        "rim_level",
                        "kick_trigger",
                        "snare_trigger",
                        "hihat_trigger",
                        "crash_trigger",
                        "tom_trigger",
                        "ride_trigger",
                        "rim_trigger",
                        "transient",
                        "onset",
                        "kick_body",
                        "snare_body",
                        "tom_body",
                        "snare_crack",
                        "upper_tom",
                    ],
                )
            )
            for row in group[:examples]:
                lines.append(
                    "  example "
                    f"{row.get('program_name', '')} {row.get('expected_family', '')} {row.get('path', '')} "
                    f"active={row.get('drum_active_list', '')} "
                    f"levels=kick:{row.get('kick_level', '')},snare:{row.get('snare_level', '')},"
                    f"hihat:{row.get('hihat_level', '')},crash:{row.get('crash_level', '')},"
                    f"tom:{row.get('tom_level', '')},ride:{row.get('ride_level', '')},"
                    f"rim:{row.get('rim_level', '')}"
                )

    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()
    for line in summarize(args.path, max(0, args.top), max(0, args.examples)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
