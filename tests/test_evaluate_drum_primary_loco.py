#!/usr/bin/env python3
"""Regression checks for the drum-primary LOCO diagnostic."""

from __future__ import annotations

import csv
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_drum_primary_loco.py"
CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")


def row(expected: str, got: str, level: float) -> dict[str, str]:
    values = {"expected": expected, "got": got, "energy_low": "0.2", "energy_mid": "0.3",
              "energy_high": "0.4", "kick_body": "1", "snare_body": "1", "tom_body": "1",
              "snare_crack": "1", "upper_tom_body": "1"}
    for category in CATEGORIES:
        values.update({f"{category}_level": "0.1", f"{category}_shape_score": "0.1",
                       f"{category}_band": "0.1", f"{category}_seg": "0.1",
                       f"{category}_trigger": "1", f"{category}_threshold": "1"})
    for field in ("level", "shape_score", "band", "seg"):
        values[f"{expected}_{field}"] = str(level)
    values[f"{expected}_trigger"] = "10"
    return values


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = pathlib.Path(temp_dir)
        headers = list(row("kick", "kick", 1.0))
        paths = []
        for index in range(2):
            path = directory / f"corpus{index}.tsv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t")
                writer.writeheader()
                writer.writerow(row("kick", "snare" if index == 0 else "kick", 1.0))
                writer.writerow(row("snare", "kick" if index == 0 else "snare", 0.9))
            paths.append(path)
        result = subprocess.run([sys.executable, str(SCRIPT), *(str(path) for path in paths)],
                                check=True, capture_output=True, text=True)
        assert "drum primary LOCO audit" in result.stdout
        assert "drum_primary_loco: improved_corpora=" in result.stdout
        assert "target_delta=n/a" in result.stdout
    print("evaluate_drum_primary_loco: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
