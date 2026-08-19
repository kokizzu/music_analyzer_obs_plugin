#!/usr/bin/env python3
"""Regression checks for primary chord-label display audit."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_chord_primary_components as MODULE  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.tsv"
        path.write_text(
            "expected_chords\tkeyboard_chord\nC\tC=Am\nG\tC=G\nC#dim7\tC#dim7=C#dim=Edim7\nDm\t--\n",
            encoding="utf-8",
        )
        result = MODULE.measure(path)
        assert result.rows == 4
        assert result.displayed == 3
        assert result.any_hit == 3
        assert result.primary_hit == 2
        assert result.alias_rescued == 1
        assert result.dim7_primary_hit == 2
        assert result.dim7_promotions == 1
        assert result.dim7_regressions == 0
    assert MODULE.dim7_first(["C#dim", "C#dim7", "Edim7"]) == "C#dim7"
    assert MODULE.runtime_dim7_promotion(["C#dim7", "C#dim", "Edim7"])
    print("audit_chord_primary_components: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
