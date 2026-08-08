#!/usr/bin/env python3
"""Regression test for the drum primary-score comparison tool."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "compare_drum_primary_scores.py"
SPEC = importlib.util.spec_from_file_location("compare_drum_primary_scores", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(expected: str, *, snare_level: float, tom_level: float,
        snare_trigger: float, tom_trigger: float) -> dict[str, str]:
    values = {"expected": expected, "got": expected}
    for category in MODULE.CATEGORIES:
        values[f"{category}_level"] = "0"
        values[f"{category}_trigger"] = "0"
        values[f"{category}_threshold"] = "1"
    values.update({
        "snare_level": str(snare_level),
        "tom_level": str(tom_level),
        "snare_trigger": str(snare_trigger),
        "tom_trigger": str(tom_trigger),
    })
    return values


def main() -> int:
    snare = row("snare", snare_level=0.98, tom_level=1.0,
                snare_trigger=60.0, tom_trigger=40.0)
    assert MODULE.predicted(snare, 0.0) == "tom"
    assert MODULE.predicted(snare, 0.08) == "snare"

    tom = row("tom", snare_level=0.98, tom_level=1.0,
              snare_trigger=60.0, tom_trigger=65.0)
    assert MODULE.predicted(tom, 0.08) == "tom"

    with tempfile.TemporaryDirectory() as temp_dir:
        path = pathlib.Path(temp_dir) / "rows.tsv"
        headers = ["expected", "got"] + [
            f"{category}_{field}"
            for category in MODULE.CATEGORIES
            for field in ("level", "trigger", "threshold")
        ]
        path.write_text("\t".join(headers) + "\n" + "\t".join(
            snare.get(header, "") for header in headers) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), str(path), "--weights", "0,0.08"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "rows=1 baseline=1/1" in result.stdout
        assert "trigger_weight=0.08 correct=1/1" in result.stdout

    print("compare_drum_primary_scores: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
