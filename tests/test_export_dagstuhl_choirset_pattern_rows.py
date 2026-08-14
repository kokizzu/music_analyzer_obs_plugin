#!/usr/bin/env python3
"""Regression checks for DCS-to-pattern-row export semantics."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "export_dagstuhl_choirset_pattern_rows.py"
SPEC = importlib.util.spec_from_file_location("export_dcs_pattern_rows", SCRIPT)
assert SPEC and SPEC.loader
EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"pieces": [{"id": "DCS_Test_Take01"}]}), encoding="utf-8")
        attributes = root / "attributes.tsv"
        header = (
            "recording\tcenter_sample\tactive_notes\tcandidate_evidence\tbass_notes\tkeys_notes\tguitar_notes\t"
            "vocal_notes\tother_notes\tamb_notes\tbass_visual_notes\tkeys_visual_notes\tguitar_visual_notes\t"
            "vocal_visual_notes\tother_visual_notes\tamb_visual_notes\n"
        )
        attributes.write_text(
            header
            + "1\t100\t52:60,55:52\t60,vocal,0.90,0.00,0.00,0.00,0.90,0.00,0.95,0.80,1,0;52,other,0.80,0.00,0.00,0.00,0.10,0.90,0.80,0.70,0,0\t\t\t\tC4:1.00\tE3:0.90\t\t\t\t\tC4:0.25\tE3:0.24\t\n",
            encoding="utf-8",
        )
        rows = EXPORT.export_rows(attributes, manifest)
        assert len(rows) == 2
        soprano, bass = rows
        assert soprano["status"] == "hit"
        assert soprano["first_row"] == "vocals"
        assert soprano["visual_first_row"] == "vocals"
        assert soprano["debug_owner"] == "vocal"
        assert bass["status"] == "ownership_miss"
        assert bass["first_row"] == "other"
        assert bass["visual_first_row"] == ""
        assert bass["debug_owner"] == "other"
    print("test_export_dagstuhl_choirset_pattern_rows: 10 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
