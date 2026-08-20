#!/usr/bin/env python3
"""Summarize continuous piano chord-state replay TSVs."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def label_status(row: dict[str, str]) -> str:
    if row.get("chord_hit") == "1":
        return "correct"
    return "no_label" if row.get("keyboard_chord", "") in {"", "--"} else "wrong"


def summarize(path: Path) -> tuple[int, int, int, int, int, int, dict[int, tuple[int, int, int]]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        required = {"recording", "anchor_sample", "frame", "keyboard_chord", "chord_hit"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
        for row in reader:
            groups[(row["recording"], row["anchor_sample"])].append(row)
    sequences = frames = correct = no_label = wrong = flickers = 0
    by_frame: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
    for rows in groups.values():
        rows.sort(key=lambda row: int(row["frame"]))
        if len(rows) < 3:
            continue
        sequences += 1
        statuses = [label_status(row) for row in rows]
        frames += len(statuses)
        correct += statuses.count("correct")
        no_label += statuses.count("no_label")
        wrong += statuses.count("wrong")
        flickers += sum(
            1
            for before, middle, after in zip(statuses, statuses[1:], statuses[2:])
            if before == after == "correct" and middle != "correct"
        )
        for row, status in zip(rows, statuses):
            counts = by_frame[int(row["frame"])]
            counts[0] += 1
            counts[{"correct": 1, "no_label": 2, "wrong": 2}[status]] += 1
    return sequences, frames, correct, no_label, wrong, flickers, {
        frame: (counts[0], counts[1], counts[2]) for frame, counts in by_frame.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    total = [0] * 6
    total_by_frame: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
    for path in args.inputs:
        values = summarize(path)
        sequences, frames, correct, no_label, wrong, flickers, by_frame = values
        total = [left + right for left, right in zip(total, values[:6])]
        for frame, counts in by_frame.items():
            for index, count in enumerate(counts):
                total_by_frame[frame][index] += count
        print(
            f"piano_chord_state_audit: source={path.name} sequences={sequences} frames={frames} "
            f"correct={correct}/{frames} no_label={no_label} wrong={wrong} transient_losses={flickers}"
        )
        for frame, (frame_total, frame_correct, frame_not_correct) in sorted(by_frame.items()):
            print(
                f"piano_chord_state_audit: source={path.name} frame={frame} frames={frame_total} "
                f"correct={frame_correct}/{frame_total} not_correct={frame_not_correct}"
            )
    if len(args.inputs) > 1:
        sequences, frames, correct, no_label, wrong, flickers = total
        print(
            f"piano_chord_state_audit: combined sequences={sequences} frames={frames} "
            f"correct={correct}/{frames} no_label={no_label} wrong={wrong} transient_losses={flickers}"
        )
        for frame, (frame_total, frame_correct, frame_not_correct) in sorted(total_by_frame.items()):
            print(
                f"piano_chord_state_audit: combined frame={frame} frames={frame_total} "
                f"correct={frame_correct}/{frame_total} not_correct={frame_not_correct}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
