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
                    f"other:{row.get('other_label', '')}"
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
