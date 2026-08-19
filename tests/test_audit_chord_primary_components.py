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
            "expected_chords\tkeyboard_chord\nC\tC=Am\nG\tC=G\nDm\t--\n",
            encoding="utf-8",
        )
        result = MODULE.measure(path)
        assert result.rows == 3
        assert result.displayed == 2
        assert result.any_hit == 2
        assert result.primary_hit == 1
        assert result.alias_rescued == 1
    print("audit_chord_primary_components: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
