#!/usr/bin/env python3
"""Regression checks for protected replay of two-feature drum contexts."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_drum_false_positive_contexts as MODULE  # noqa: E402


def main() -> int:
    context = MODULE.Context(
        "ride", MODULE.Predicate("level", ">=", 0.6), MODULE.Predicate("high", "<=", 0.1), 2, ()
    )
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.tsv"
        path.write_text(
            "expected\tgot\tride_level\tenergy_high\nride\tride\t0.7\t0.05\nsnare\tride\t0.7\t0.20\n",
            encoding="utf-8",
        )
        result = MODULE.replay(context, [path])
        assert result.rows == 2
        assert result.primary_suppressed == 1
        assert result.correct_suppressed == 1
        assert result.unsupported == 0
    print("audit_drum_false_positive_contexts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
