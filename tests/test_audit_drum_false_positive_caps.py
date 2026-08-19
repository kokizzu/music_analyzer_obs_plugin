#!/usr/bin/env python3
"""Regression checks for protected replay of real-mix false-positive caps."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_drum_false_positive_caps as MODULE  # noqa: E402
import search_egmd_false_positive_caps as SEARCH  # noqa: E402


def main() -> int:
    candidate = SEARCH.Candidate("ride", "level", ">=", 0.6, 2, 0, (("MDB", 1), ("STAR", 1)))
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.tsv"
        path.write_text(
            "expected\tgot\tride_level\nride\tride\t0.7\nsnare\tride\t0.5\n",
            encoding="utf-8",
        )
        result = MODULE.replay(candidate, [path])
        assert result.rows == 2
        assert result.primary_suppressed == 1
        assert result.correct_suppressed == 1
        assert result.unsupported == 0
    print("audit_drum_false_positive_caps: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
