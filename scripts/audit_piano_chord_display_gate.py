#!/usr/bin/env python3
"""Compare a keyboard-chord display-confidence gate with its protected replay."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "scripts" / "summarize_piano_chord_state_audit.py"
SPEC = importlib.util.spec_from_file_location("piano_chord_state_summary", SUMMARY)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def totals(paths: list[Path]) -> tuple[int, int, int, int]:
    values = [MODULE.summarize(path) for path in paths]
    return (
        sum(value[1] for value in values),
        sum(value[2] for value in values),
        sum(value[4] for value in values),
        sum(value[5] for value in values),
    )


def render(baseline_paths: list[Path], trial_paths: list[Path], floor: float) -> str:
    baseline_frames, baseline_correct, baseline_wrong, baseline_flickers = totals(baseline_paths)
    trial_frames, trial_correct, trial_wrong, trial_flickers = totals(trial_paths)
    if baseline_frames != trial_frames:
        raise ValueError("baseline and trial frame totals differ")
    eligible = (
        trial_correct >= baseline_correct
        and trial_wrong < baseline_wrong
        and trial_flickers <= baseline_flickers
    )
    return (
        "piano_chord_display_gate: "
        f"floor={floor:.2f} baseline_correct={baseline_correct}/{baseline_frames} "
        f"baseline_wrong={baseline_wrong} baseline_flickers={baseline_flickers} "
        f"trial_correct={trial_correct}/{trial_frames} trial_wrong={trial_wrong} "
        f"trial_flickers={trial_flickers} eligible={int(eligible)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", nargs=2, required=True, type=Path)
    parser.add_argument("--trial", nargs=2, required=True, type=Path)
    parser.add_argument("--floor", required=True, type=float)
    args = parser.parse_args()
    if not 0.0 <= args.floor <= 1.0:
        parser.error("floor must be in [0, 1]")
    try:
        print(render(args.baseline, args.trial, args.floor))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
