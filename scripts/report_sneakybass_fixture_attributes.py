#!/usr/bin/env python3
"""Summarize raw tuning evidence from the real Sneakybass fixture audit."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def as_float(row: dict[str, str], name: str) -> float:
    try:
        return float(row.get(name, "0"))
    except ValueError:
        return 0.0


def active(row: dict[str, str]) -> bool:
    return row.get("detected_expected_row", "0") not in {"", "0", "false", "False"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attributes", required=True, type=Path)
    args = parser.parse_args()
    if not args.attributes.is_file():
        print(f"sneakybass_attributes_exists=false path={args.attributes}")
        return 1
    with args.attributes.open(encoding="utf-8", newline="") as input_file:
        rows = [row for row in csv.DictReader(input_file, delimiter="\t") if row.get("family") == "real_bass"]
    if not rows:
        print("sneakybass_attributes_rows=0")
        return 1
    buckets = Counter()
    detected = Counter()
    articulations: dict[str, Counter[str]] = {}
    evidence: dict[tuple[str, str], Counter[str]] = {}
    examples: dict[str, list[dict[str, str]]] = {}
    peak_deltas = Counter()
    for row in rows:
        cents = abs(as_float(row, "raw_tuned_cent_offset"))
        bucket = "within_9c" if cents <= 9.01 else "within_18c" if cents <= 18.01 else "outside_18c"
        buckets[bucket] += 1
        if active(row):
            detected[bucket] += 1
        try:
            peak_delta = int(row.get("raw_local_best_midi", "-999")) - int(row.get("midi", "0"))
        except ValueError:
            peak_delta = -999
        peak_deltas[peak_delta] += 1
        parts = Path(row.get("path", "")).parts
        articulation = parts[2] if len(parts) > 2 and parts[0] == "source" and parts[1] == "Samples" else "unknown"
        values = articulations.setdefault(articulation, Counter())
        values["total"] += 1
        values[bucket] += 1
        if active(row):
            values["detected"] += 1
            values[f"detected_{bucket}"] += 1
        if bucket == "within_9c":
            state = "detected" if active(row) else "missed"
            summary = evidence.setdefault((articulation, state), Counter())
            summary["samples"] += 1
            for field in ("raw_expected_ratio", "raw_expected_rank", "raw_tuned_ratio", "rms"):
                summary[field] += as_float(row, field)
            if state == "missed" and len(examples.setdefault(articulation, [])) < 3:
                examples[articulation].append(row)
    print(f"sneakybass_attributes_rows={len(rows)}")
    for bucket in ("within_9c", "within_18c", "outside_18c"):
        total = buckets[bucket]
        hits = detected[bucket]
        recall = 100.0 * hits / total if total else 0.0
        print(f"{bucket}=samples:{total} detected:{hits} recall:{recall:.1f}%")
    print("raw_local_peak_delta:")
    for delta, count in peak_deltas.most_common(8):
        print(f"delta:{delta:+d}=samples:{count}")
    print("articulations:")
    for articulation in sorted(articulations):
        values = articulations[articulation]
        total = values["total"]
        hits = values["detected"]
        recall = 100.0 * hits / total if total else 0.0
        print(
            f"{articulation}=samples:{total} detected:{hits} recall:{recall:.1f}% "
            f"within_9c:{values['within_9c']}/{values['detected_within_9c']} "
            f"within_18c:{values['within_18c']}/{values['detected_within_18c']}"
        )
    print("within_9c_evidence:")
    for articulation, state in sorted(evidence):
        summary = evidence[(articulation, state)]
        samples = summary["samples"]
        print(
            f"{articulation}:{state}=samples:{samples} "
            f"expected_ratio:{summary['raw_expected_ratio'] / samples:.3f} "
            f"expected_rank:{summary['raw_expected_rank'] / samples:.2f} "
            f"tuned_ratio:{summary['raw_tuned_ratio'] / samples:.3f} "
            f"rms:{summary['rms'] / samples:.4f}"
        )
    print("within_9c_miss_examples:")
    for articulation in sorted(examples):
        for row in examples[articulation]:
            print(
                f"{articulation} expected:{row.get('note')} midi:{row.get('midi')} "
                f"label:{row.get('bass_label')} grid:{row.get('bass_notes')} "
                f"raw_best:{row.get('raw_local_best_note')}({row.get('raw_local_best_midi')}) "
                f"rank:{row.get('raw_expected_rank')} "
				f"spectral:{row.get('bass_spectral_midi')}/{row.get('bass_spectral_confidence')} "
				f"periodic:{row.get('bass_periodic_midi')}/{row.get('bass_periodic_confidence')} "
                f"candidates:{row.get('debug_candidates')}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
