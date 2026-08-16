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


def row(family: str, owner: str, values: tuple[float, ...]) -> str:
    return f"{family}\t60\t60\t{owner}\t" + "\t".join(map(str, values)) + "\n"


def write(path: Path) -> None:
    keyboard = (0.0, 1.0, 0.0, 0.0, 0.0)
    guitar = (0.0, 0.0, 1.0, 0.0, 0.0)
    path.write_text(HEADER + row("piano", "guitar", keyboard) + row("guitar", "guitar", guitar), encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first, second = root / "first.tsv", root / "second.tsv"
        write(first)
        write(second)
        result = subprocess.run([sys.executable, str(SCRIPT), str(first), str(second)], check=True, capture_output=True, text=True)
    assert "first.tsv: current=1/2 model=2/2 delta=+1 improved=1" in result.stdout
    assert "owner_classifier_loco: improved_corpora=2/2 current=2/4 model=4/4" in result.stdout
    print("test_evaluate_owner_classifier_loco: ok")


if __name__ == "__main__":
    main()
