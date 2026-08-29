#!/usr/bin/env python3
"""Summarize C5 synth debug records by program and detected candidate."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


def first_value(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name, "")
        if value:
            return value
    return "--"


def main() -> int:
    path = Path("build/synth_c5_attributes.tsv")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    print(f"synth_c5_attribute_rows={len(rows)}")
    if not rows:
        return 0
    print("columns=" + ",".join(rows[0].keys()))
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        program = first_value(row, "program", "family_program", "sample_program")
        if program == "--":
            program = first_value(row, "path", "sample", "filename").split("_")[1] if "_" in first_value(row, "path", "sample", "filename") else "unknown"
        candidate = first_value(row, "debug_note", "debug_midi")
        owner = first_value(row, "debug_owner", "owner")
        groups[program][f"{candidate}/{owner}"] += 1
    for program in sorted(groups):
        summary = ", ".join(f"{candidate}={count}" for candidate, count in groups[program].most_common())
        print(f"{program}: {summary}")
    failures = [row for row in rows if row.get("primary_delta") not in ("", "0")]
    print(f"primary_octave_failures={len(failures)}")
    for row in failures[:16]:
        print(
            "failure"
            f" program={row.get('program', '--')}"
            f" debug={row.get('debug_note', '--')}"
            f" primary={row.get('primary_note', '--')}"
            f" display={row.get('display_note', '--')}"
            f" raw_expected_ratio={row.get('raw_expected_ratio', '--')}"
            f" down={row.get('raw_octave_down_ratio', '--')}"
            f" up={row.get('raw_octave_up_ratio', '--')}"
            f" second_up={row.get('raw_second_octave_up_ratio', '--')}"
            f" debug_count={row.get('debug_count', '--')}"
            f" debug_candidates={row.get('debug_candidates', '--')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
