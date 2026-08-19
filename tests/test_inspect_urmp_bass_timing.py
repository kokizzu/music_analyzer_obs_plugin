#!/usr/bin/env python3
"""Regression checks for URMP double-bass timing provenance inspection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "inspect_urmp_bass_timing", ROOT / "scripts" / "inspect_urmp_bass_timing.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        piece = root / "Dataset" / "35_Rondeau_vn_vn_va_db"
        piece.mkdir(parents=True)
        (piece / "Notes_04_db_35_Rondeau_vn_vn_va_db.txt").write_text("0 55 1\n", encoding="utf-8")
        (piece / "AuSep_04_db_35_Rondeau_vn_vn_va_db.wav").write_bytes(b"wav")
        (piece / "Sco_35_Rondeau_vn_vn_va_db.mid").write_bytes(b"MThd")
        rows = MODULE.rows(root)
        assert len(rows) == 1
        assert rows[0]["audio_aligned_notes"] == "1"
        assert rows[0]["score_midi"] == "1"
        assert rows[0]["explicit_beat_grid"] == "0"
        assert rows[0]["qualifies_as_tempo_truth"] == "0"
        (piece / "Beat_35.txt").write_text("0.0\n", encoding="utf-8")
        assert MODULE.rows(root)[0]["qualifies_as_tempo_truth"] == "1"
    print("inspect_urmp_bass_timing: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
