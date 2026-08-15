#!/usr/bin/env python3
"""Describe DCS exact-note ownership evidence without changing detection."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def candidates(value: str) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for item in value.split(";"):
        fields = item.split(",")
        if len(fields) < 12:
            continue
        try:
            result[int(fields[0])] = fields
        except ValueError:
            continue
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attributes", required=True, type=Path)
    args = parser.parse_args(argv)
    owner = Counter()
    profile = Counter()
    candidate_count = 0
    missing_count = 0
    score_buckets: dict[str, Counter[str]] = defaultdict(Counter)
    with args.attributes.open(encoding="utf-8", newline="") as source:
        rows = csv.DictReader(source, delimiter="\t")
        required = {"active_notes", "candidate_evidence"}
        missing = required - set(rows.fieldnames or ())
        if missing:
            parser.error(f"missing columns: {', '.join(sorted(missing))}")
        for row in rows:
            evidence = candidates(row["candidate_evidence"])
            for active in row["active_notes"].split(","):
                try:
                    _program, midi = active.split(":", 1)
                    fields = evidence.get(int(midi))
                except ValueError:
                    fields = None
                if fields is None:
                    missing_count += 1
                    continue
                candidate_count += 1
                owner[fields[1]] += 1
                profile[f"profile={fields[10]} rejected_polyphony={fields[11]}"] += 1
                vocal_score = float(fields[6])
                for threshold in ("0.10", "0.20", "0.30", "0.40", "0.50", "0.60", "0.70"):
                    if vocal_score >= float(threshold):
                        score_buckets[threshold][fields[1]] += 1
    total = candidate_count + missing_count
    print(f"DCS exact score notes with detector candidate: {candidate_count}/{total} ({candidate_count * 100.0 / total:.1f}%)")
    print(f"DCS exact score notes with no detector candidate: {missing_count}/{total} ({missing_count * 100.0 / total:.1f}%)")
    for label, count in sorted(owner.items()):
        print(f"owner {label}: {count}/{candidate_count} ({count * 100.0 / candidate_count:.1f}%)")
    for label, count in sorted(profile.items()):
        print(f"{label}: {count}/{candidate_count} ({count * 100.0 / candidate_count:.1f}%)")
    for threshold, counts in sorted(score_buckets.items(), key=lambda item: float(item[0])):
        total_at_threshold = sum(counts.values())
        print(f"vocal_score>={threshold}: {total_at_threshold}/{candidate_count} "
              f"({total_at_threshold * 100.0 / candidate_count:.1f}%), owners=" +
              ",".join(f"{name}:{count}" for name, count in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
