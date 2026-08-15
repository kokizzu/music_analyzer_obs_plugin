#!/usr/bin/env python3
"""Audit whether high vocal candidates survive a lower-octave safety gate."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


KEYBOARD_OWNERS = {"keyboard", "keys", "piano"}
DEFAULT_THRESHOLDS = (0.05, 0.10, 0.20, 0.35, 0.50, 0.75, 1.00)


@dataclass(frozen=True)
class CandidateInput:
    label: str
    path: Path


def parse_input(value: str) -> CandidateInput:
    try:
        label, raw_path = value.split("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("input must use LABEL=PATH") from exc
    if not label or not raw_path:
        raise argparse.ArgumentTypeError("input must use LABEL=PATH")
    return CandidateInput(label, Path(raw_path))


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def number(row: dict[str, str], field: str) -> float | None:
    try:
        return float(row.get(field, ""))
    except ValueError:
        return None


def high_keyboard_candidate(row: dict[str, str], midi_values: set[int]) -> bool:
    midi = number(row, "debug_midi")
    return (
        midi is not None
        and int(midi) in midi_values
        and row.get("debug_owner", "").lower() in KEYBOARD_OWNERS
    )


def is_vocal_miss(row: dict[str, str], midi_values: set[int]) -> bool:
    return (
        row.get("status") == "ownership_miss"
        and row.get("family") == "vocals"
        and high_keyboard_candidate(row, midi_values)
    )


def is_protected_risk(row: dict[str, str], midi_values: set[int]) -> bool:
    return row.get("status") == "hit" and row.get("family") != "vocals" and high_keyboard_candidate(row, midi_values)


def is_multisignal_candidate(row: dict[str, str], midi_values: set[int]) -> bool:
    adjacent_upper = number(row, "adjacent_upper_ratio")
    centroid = number(row, "centroid")
    return (
        high_keyboard_candidate(row, midi_values)
        and adjacent_upper is not None
        and adjacent_upper >= 0.053
        and centroid is not None
        and 0.013 <= centroid <= 0.116
    )


def count_at_threshold(rows: list[dict[str, str]], predicate, threshold: float) -> int:
    return sum(
        predicate(row) and (ratio := number(row, "raw_octave_down_ratio")) is not None and ratio <= threshold
        for row in rows
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", type=parse_input, required=True)
    parser.add_argument("--protected", action="append", type=Path, required=True)
    parser.add_argument("--midi", action="append", type=int, default=[77, 78])
    parser.add_argument("--threshold", action="append", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    midi_values = set(args.midi)
    thresholds = tuple(args.threshold or DEFAULT_THRESHOLDS)
    candidates = [(item.label, load_rows(item.path)) for item in args.candidate]
    protected = [row for path in args.protected for row in load_rows(path)]
    candidate_totals = {
        label: sum(is_vocal_miss(row, midi_values) for row in rows) for label, rows in candidates
    }
    protected_total = sum(is_protected_risk(row, midi_values) for row in protected)

    midi_text = ",".join(str(midi) for midi in sorted(midi_values))
    lines = [
        f"high-vocal octave safety audit: midi={midi_text}",
        "| Lower-octave ratio cap | DCS candidates | CSD candidates | ESMUC candidates | Corpora with candidates | Protected risks |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for threshold in thresholds:
        counts = {label: count_at_threshold(rows, lambda row: is_vocal_miss(row, midi_values), threshold) for label, rows in candidates}
        risk = count_at_threshold(protected, lambda row: is_protected_risk(row, midi_values), threshold)
        corpora = sum(count > 0 for count in counts.values())
        cells = [
            f"{counts.get(label, 0)} / {candidate_totals[label]}" for label, _rows in candidates
        ]
        lines.append(
            f"| <= {threshold:.2f} | "
            + " | ".join(cells)
            + f" | {corpora} / {len(candidates)} | {risk} / {protected_total} |"
        )
    multisignal_counts = {
        label: sum(
            is_vocal_miss(row, midi_values) and is_multisignal_candidate(row, midi_values)
            for row in rows
        )
        for label, rows in candidates
    }
    multisignal_risk = sum(
        is_protected_risk(row, midi_values) and is_multisignal_candidate(row, midi_values)
        for row in protected
    )
    multisignal_corpora = sum(count > 0 for count in multisignal_counts.values())
    lines.extend(
        [
            "",
            "| Multi-signal route profile | "
            + " | ".join(f"{label} candidates" for label, _rows in candidates)
            + " | Corpora with candidates | Protected risks |",
            "| --- | " + " | ".join("---:" for _label, _rows in candidates)
            + " | ---: | ---: |",
            "| upper-adjacent >= 0.053; centroid 0.013..0.116 | "
            + " | ".join(
                f"{multisignal_counts[label]} / {candidate_totals[label]}"
                for label, _rows in candidates
            )
            + f" | {multisignal_corpora} / {len(candidates)} | {multisignal_risk} / {protected_total} |",
        ]
    )
    text = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"inspect_high_vocal_octave_evidence: wrote {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
