#!/usr/bin/env python3
"""Regression checks for exact-MIDI vocal cross-corpus accounting."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_vocal_exact_note_cross_corpus.py"
SPEC = importlib.util.spec_from_file_location("inspect_exact_note_cross_corpus", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.tsv"
        path.write_text(
            "family\texpected_midi\tbass_notes\tpiano_notes\tvocal_notes\n"
            "vocals\t60\t\t\tC4:1.00\n"
            "vocals\t62\t\tD4:1.00\t\n"
            "vocals\t64\t\tE5:1.00\t\n"
            "vocals\t65\t\tG4:1.00\t\n"
            "other\t67\t\tG4:1.00\t\n",
            encoding="utf-8",
        )
        assert INSPECT.summarize([("fixture", path)]) == [("fixture", 1, 1, 1, 1, 4)]
        oversized = Path(temporary) / "oversized.tsv"
        oversized.write_text(
            "family\texpected_midi\tbass_notes\tpiano_notes\tvocal_notes\n"
            f"vocals\t60\t\t\tC4:1.00,{',' * 140000}\n",
            encoding="utf-8",
        )
        assert INSPECT.summarize([("oversized", oversized)]) == [("oversized", 1, 0, 0, 0, 1)]
    print("test_inspect_vocal_exact_note_cross_corpus: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
