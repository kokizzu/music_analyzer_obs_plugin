#!/usr/bin/env python3
"""Tests for leave-one-corpus-out owner-classifier evaluation."""

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_owner_classifier_loco.py"
FEATURES = ("bass_score", "keyboard_score", "guitar_score", "vocal_score", "other_score")
HEADER = "family\texpected_midi\tdebug_midi\tdebug_owner\t" + "\t".join(FEATURES) + "\n"
QUALITY_FIELDS = (
    "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise",
    "adjacent_lower_ratio", "adjacent_upper_ratio", "third_octave_ratio", "partial1", "partial2", "partial3", "partial4", "partial5",
)


def row(family: str, owner: str, values: tuple[float, ...]) -> str:
    return f"{family}\t60\t60\t{owner}\t" + "\t".join(map(str, values)) + "\n"


def write(path: Path) -> None:
    # Keep bass in the labelled set: the evaluator must not silently discard the
    # analyzer's existing bass-score evidence.
    bass = (1.0, 0.0, 0.0, 0.0, 0.0)
    keyboard = (0.0, 1.0, 0.0, 0.0, 0.0)
    guitar = (0.0, 0.0, 1.0, 0.0, 0.0)
    path.write_text(
        HEADER
        + row("bass", "bass", bass)
        + row("piano", "guitar", keyboard)
        + row("guitar", "guitar", guitar),
        encoding="utf-8",
    )


def write_quality(path: Path) -> None:
    header = HEADER.rstrip("\n") + "\t" + "\t".join(QUALITY_FIELDS) + "\n"
    path.write_text(
        header
        + row("bass", "bass", (1.0, 0.0, 0.0, 0.0, 0.0)).rstrip("\n") + "\t" + "\t".join(["0.1"] * len(QUALITY_FIELDS)) + "\n"
        + row("piano", "guitar", (0.0, 1.0, 0.0, 0.0, 0.0)).rstrip("\n") + "\t" + "\t".join(["0.2"] * len(QUALITY_FIELDS)) + "\n"
        + row("guitar", "guitar", (0.0, 0.0, 1.0, 0.0, 0.0)).rstrip("\n") + "\t" + "\t".join(["0.3"] * len(QUALITY_FIELDS)) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first, second = root / "first.tsv", root / "second.tsv"
        write(first)
        write(second)
        result = subprocess.run([sys.executable, str(SCRIPT), str(first), str(second)], check=True, capture_output=True, text=True)
        quality_first, quality_second = root / "quality_first.tsv", root / "quality_second.tsv"
        write_quality(quality_first)
        write_quality(quality_second)
        quality = subprocess.run(
            [sys.executable, str(SCRIPT), "--feature-profile", "quality", str(quality_first), str(quality_second)],
            check=True,
            capture_output=True,
            text=True,
        )
    assert "first.tsv: current=2/3 model=3/3 delta=+1 improved=1" in result.stdout
    assert "owner_classifier_loco: improved_corpora=2/2 current=4/6 model=6/6" in result.stdout
    assert "feature_profile=quality" in quality.stdout
    assert "owner_classifier_loco: improved_corpora=2/2 current=4/6 model=6/6" in quality.stdout
    print("test_evaluate_owner_classifier_loco: ok")


if __name__ == "__main__":
    main()
