#!/usr/bin/env python3
"""Regression check for the high-vocal octave safety audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_high_vocal_octave_evidence.py"
SPEC = importlib.util.spec_from_file_location("high_vocal_octave", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def write_rows(path: Path, rows: list[str]) -> None:
    path.write_text(
        "status\tfamily\tdebug_midi\tdebug_owner\traw_octave_down_ratio\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        candidates = root / "candidates.tsv"
        protected = root / "protected.tsv"
        write_rows(candidates, [
            "ownership_miss\tvocals\t77\tpiano\t0.10",
            "ownership_miss\tvocals\t78\tpiano\t0.60",
            "hit\tvocals\t77\tpiano\t0.01",
        ])
        write_rows(protected, [
            "hit\tguitar\t77\tpiano\t0.20",
            "hit\tguitar\t78\tpiano\t0.80",
        ])
        rows = AUDIT.load_rows(candidates)
        protected_rows = AUDIT.load_rows(protected)
        midi_values = {77, 78}
        assert sum(AUDIT.is_vocal_miss(row, midi_values) for row in rows) == 2
        assert AUDIT.count_at_threshold(rows, lambda row: AUDIT.is_vocal_miss(row, midi_values), 0.20) == 1
        assert AUDIT.count_at_threshold(protected_rows, lambda row: AUDIT.is_protected_risk(row, midi_values), 0.20) == 1
    print("test_inspect_high_vocal_octave_evidence: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
