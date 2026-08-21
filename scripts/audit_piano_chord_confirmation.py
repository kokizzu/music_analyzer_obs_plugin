#!/usr/bin/env python3
"""Compare the protected two-frame chord switch gate with a one-frame trial."""

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


def render(baseline_paths: list[Path], trial_paths: list[Path]) -> str:
    baseline_frames, baseline_correct, baseline_wrong, baseline_flickers = totals(baseline_paths)
    trial_frames, trial_correct, trial_wrong, trial_flickers = totals(trial_paths)
    if baseline_frames != trial_frames:
        raise ValueError("baseline and trial frame totals differ")
    # Correct labels may only be gained if the existing no-flicker invariant is
    # still met.  A chord display that briefly leaves a correct label is worse
    # than a delayed replacement in a live overlay.
    eligible = trial_correct > baseline_correct and trial_flickers <= baseline_flickers
    return (
        "piano_chord_confirmation_audit: "
        f"baseline_correct={baseline_correct}/{baseline_frames} baseline_wrong={baseline_wrong} "
        f"baseline_flickers={baseline_flickers} trial_correct={trial_correct}/{trial_frames} "
        f"trial_wrong={trial_wrong} trial_flickers={trial_flickers} "
        f"retained_confirm_frames={2 if not eligible else 1} eligible={int(eligible)}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", nargs=2, required=True, type=Path)
    parser.add_argument("--trial", nargs=2, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(render(args.baseline, args.trial))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
